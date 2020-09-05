from app import db,UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Question(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100),unique = True)
    question_text = db.Column(db.String(500),unique=False)
    answer = db.Column(db.Float , unique = False)
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'))


class Contest(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String(100),unique= True)
    number_of_question = db.Column(db.Integer)
    description = db.Column(db.String(500))
    questions = db.relationship('Question',backref='contest',lazy='dynamic',cascade = 'all, delete, delete-orphan')


class Contest_user(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    contest_id = db.Column(db.Integer , db.ForeignKey('contest.id'))
    user_id = db.Column(db.Integer , db.ForeignKey('user.id'))
    number_of_question = db.Column(db.Integer)
    questions = db.relationship('Question_user',backref= 'contest_user',lazy='dynamic',cascade = 'all, delete, delete-orphan')
    marks = db.Column(db.Integer,default = 0)
    rank = db.Column(db.Integer,default=1)

class Question_user(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    contest_user_id = db.Column(db.Integer,db.ForeignKey('contest_user.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer,db.ForeignKey('question.id'))
    isCompleted = db.Column(db.Boolean,unique=False,default=False)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(100), index=True,unique=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    contests_given = db.relationship('Contest_user', backref = 'user',lazy='dynamic')
    score = db.Column(db.Integer,default=0)
    grank = db.Column(db.Integer,default=1)
    def set_password(self,password):
        self.password = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password,password)