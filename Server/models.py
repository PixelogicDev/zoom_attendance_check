from Server import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False) # 60 chars because of the hashing algo
    classes = db.relationship('Classroom', backref='teacher', lazy=True)
    
    def __repr__(self):
        return f'User({self.username}, {self.email}, {self.password})'

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=False, nullable=False)
    csv_students_file = db.Column(db.String(120), unique=True, nullable=False)
    teacher_id =  db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # TODO: also store the reports in the db