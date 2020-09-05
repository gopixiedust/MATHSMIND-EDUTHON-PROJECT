from app import db
from DbModels import Question,Contest

contest = Contest(name="DIV 1",number_of_question = 3,description = "YOYOYO")
db.session.add(contest)
db.session.commit()
q1 = Question(name="Simple",question_text="what is 2+2",answer=4,contest_id=contest.id)
q2 = Question(name="Simple 1",question_text="what is 5+2",answer=7,contest_id=contest.id)
q3 = Question(name="Simple 2",question_text="what is 10+7",answer=17,contest_id=contest.id)

db.session.add(q1)
db.session.add(q2)
db.session.add(q3)

db.session.commit()
