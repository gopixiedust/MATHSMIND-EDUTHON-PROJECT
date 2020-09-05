from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user,current_user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login = LoginManager()
login.init_app(app)  
app.secret_key = 'itsmathtime'
admin_password = 'guruji'

from DbModels import Question,User,Contest,Contest_user,Question_user,Practice_question


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def landing():
    if current_user.is_authenticated:
        return render_template('Homepage.html',current_user=current_user,username = User.query.get(current_user.get_id()).name)
    else:
        return render_template('Homepage.html',current_user=current_user)

@app.route('/index')
@login_required
def index():
    return render_template("contestsinfo.html",contest=Contest.query.all())



@app.route('/contest/<int:Cid>')
@login_required
def home(Cid):
    contest =  Contest_user.query.filter(Contest_user.contest_id == Cid).filter(Contest_user.user_id == current_user.get_id()).first()
    if contest is None:
        contest = Contest_user(contest_id = Cid,user_id = current_user.get_id(),number_of_question = Contest.query.get(Cid).number_of_question)
        db.session.add(contest)
        db.session.commit()
        participants = Contest_user.query.filter(Contest_user.contest_id ==Cid).order_by(Contest_user.marks.desc()).all()
        j=1
        for i in range(0,len(participants)):
            participants[i].rank = j
            if i!=len(participants)-1:
                if participants[i].marks!=participants[i+1].marks:
                    j=i+2
        db.session.commit()
        questions = Contest.query.get(Cid).questions.all()
        for i in questions:
            que = Question_user(contest_user_id = contest.id,user_id = current_user.get_id(),question_id = i.id)
            db.session.add(que)
        db.session.commit()
    contest =  Contest_user.query.filter(Contest_user.contest_id == Cid).filter(Contest_user.user_id == current_user.get_id()).first()
   # ques = Contest_user.query.filter(contest_id = Cid).first().questions.all()
    return render_template("contest-problems.html",questions=contest.questions.all(),Question=Question,contest = Contest.query.get(Cid))


@app.route("/question/<int:my_id>", methods = ['GET','POST'])
def question(my_id):
    ans=0
    ques = Question.query.get(Question_user.query.get(my_id).question_id)
    if request.method == 'POST':
        ans = request.form['answer']
        if float(ans) == ques.answer:
            Question_user.query.get(my_id).isCompleted = True
            Contest_user.query.get(Question_user.query.get(my_id).contest_user_id).marks += 5
            db.session.commit()
            get_id = Contest_user.query.get(Question_user.query.get(my_id).contest_user_id).contest_id
            participants = Contest_user.query.filter(Contest_user.contest_id == get_id).order_by(Contest_user.marks.desc()).all()
            j=1
            for i in range(0,len(participants)):
                participants[i].rank = j
                if i!=len(participants)-1:
                    if participants[i].marks!=participants[i+1].marks:
                        j=i+2
            db.session.commit()
            ans = 1
        else:
            ans = -1

    return render_template("problem.html",text=ques.question_text,name = ques.name,contest = Contest.query.get(ques.contest_id),response = ans)


@app.route('/leaderboard/<int:Cid>')
def leaderboard(Cid):
    participants = Contest_user.query.filter(Contest_user.contest_id == Cid).order_by(Contest_user.marks.desc()).all()
    return render_template("leaderboard.html",users = participants,User=User,contest = Contest.query.get(Cid))




@app.route('/register',methods=['GET', 'POST'])
def register():
    exist = False
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User(username=request.form['username'], email=request.form['email'],name=request.form['fullname'])
        user.set_password(request.form['password'])
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('landing'))
        except:
            exist=True
    return render_template('signup.html',exist=exist)



@app.route('/login',methods = ['GET','POST'])
def loginUser():
    exist = False
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter(User.username == request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            exist = True
        else:
            login_user(user)
            return redirect(url_for('landing'))
    return render_template('login.html',exist = exist)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))





@app.route('/admin/contest',methods = ['GET','POST'])
@login_required
def contest_admin():
    if User.query.get(current_user.get_id()).username != admin_password:
        return redirect(url_for('landing'))
    if request.method == 'POST':
        contest = Contest(name=request.form["contest_name"],number_of_question =int( request.form["number_of_question"]),description = request.form["description"])
        db.session.add(contest)
        db.session.commit()
        p_id = contest.id
        return redirect(url_for('question_admin',p_id=p_id))
    return render_template("contest-admin.html")



@app.route('/admin/question/<int:p_id>',methods = ['GET','POST'])
@login_required
def question_admin(p_id):
    if User.query.get(current_user.get_id()).username != admin_password:
        return redirect(url_for('landing'))
    contest =Contest.query.get(p_id)
    if len(contest.questions.all()) >= contest.number_of_question:
        return redirect(url_for('index'))
    if request.method == 'POST':
        q = Question(name = request.form["q_name"],question_text = request.form["q_text"],answer = float(request.form["q_ans"]),contest_id = p_id)
        try:
            db.session.add(q)
            db.session.commit()
        except:
            return redirect(url_for('question_admin'))
    if len(contest.questions.all()) >= contest.number_of_question:
        return redirect(url_for('index'))
    return render_template('question_admin.html')


@login.unauthorized_handler
def unauthorized():
    return redirect(url_for('loginUser'))
	


@app.route('/del/<int:Cid>')
@login_required
def delete(Cid):
    if User.query.get(current_user.get_id()).username != admin_password:
        return redirect(url_for('landing'))
    questions_p = Question.query.filter(Contest.id == Cid).all()
    con_name = Contest.query.get(Cid).name
    for i in questions_p:
        quest = Practice_question(name = i.name,question_text = i.question_text,answer = i.answer,contest_name = con_name)
        db.session.add(quest)
        db.session.commit()
    participants = Contest_user.query.filter(Contest_user.contest_id == Cid).all()
    for i in participants:
        User.query.get(i.user_id).score+=i.marks
        db.session.delete(i)
    db.session.commit()
    db.session.delete(Contest.query.get(Cid))
    db.session.commit()
    participants = User.query.order_by(User.score.desc()).all()
    j=1
    for i in range(0,len(participants)):
        participants[i].grank = j
        if i!=len(participants)-1:
            if participants[i].score!=participants[i+1].score:
                j=i+2
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/practice/<int:page>')
@login_required
def practice(page):
    questions = Practice_question.query.filter(Practice_question.id> (page-1)*10).filter(Practice_question.id<=page*10).all()
    pages = ((len(Practice_question.query.all())-1)//10)+1
    return render_template('Practice.html',questions=questions,page = page,pages = pages)


@app.route('/practice/question/<int:Qid>',methods = ['GET','POST'])
@login_required
def p_question(Qid):
    ans=0
    ques = Practice_question.query.get(Qid)
    if request.method == 'POST':
        ans = request.form['answer']
        if float(ans) == ques.answer:
            ans=1
        else:
            ans=-1

    return render_template("problem.html",text=ques.question_text,name = ques.name,contest = 'PRACTICE',response = ans)



@app.route('/standings')
def standings():
    participants = User.query.filter(User.grank>=1).filter(User.grank<=5).order_by(User.score.desc()).all()
    return render_template("standings.html",topper=participants)



@app.errorhandler(500)
def internal_error(e):
    return "<center>contest may be ended or some internal server error</center>"