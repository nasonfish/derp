from derp import db

from flask import request
import base64
import random
import datetime

from flask import session


class Privilege(db.Model):
    account_fk = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)
    account = db.relationship('Account', backref='privileges', foreign_keys=[account_fk])
    name = db.Column(db.String(128), primary_key=True)

    def __init__(self, account, name):
        self.account_fk = account.id
        self.account = account
        self.name = name
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def user_privilege(name):
        sess = Session.query.filter_by(challenge=session['challenge'], remote_addr=request.remote_addr) \
            .join(Account) \
            .filter(Account.student_id == session['student_id']).first()
        return bool([p for p in sess.account.privileges if p.name == name])


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_fk = db.Column(db.Integer, db.ForeignKey('account.id'))
    account = db.relationship('Account', backref='sessions', foreign_keys=[account_fk])
    remote_addr = db.Column(db.String(128), nullable=False)
    challenge = db.Column(db.String(256), nullable=False)

    def __init__(self, account, remote_addr, challenge):
        self.account_fk = account.id
        self.account = account
        self.remote_addr = remote_addr
        self.challenge = challenge

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def create(user):
        remote_addr = request.remote_addr
        challenge = str(base64.b64encode(str(random.getrandbits(256)).encode('ascii')))
        session['challenge'] = challenge
        session['student_id'] = user.student_id
        return Session(user, remote_addr, challenge)

    @staticmethod
    def session_user():
        if not session or 'challenge' not in session or 'student_id' not in session or not request:
            return None
        sess = Session.query.filter_by(challenge=session['challenge'], remote_addr=request.remote_addr) \
            .join(Account) \
            .filter(Account.student_id == session['student_id']).first()
        return sess.account


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    github_username = db.Column(db.String(128), nullable=False)
    student_id = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False)

    def __init__(self, github_username, student_id, email):
        self.github_username = github_username
        self.student_id = student_id
        self.email = email

        db.session.add(self)
        db.session.commit()

    def courses(self):
        return {
            'active': [e for e in self.enrollments if e.course.active],
            'inactive': [e for e in self.enrollments if not e.course.active]
        }

    def has_permission(self, name):
        for i in self.privileges:
            if i.name == name:
                return True
        return False


class Enrollment(db.Model):
    account_fk = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)
    account = db.relationship('Account', backref='enrollments', foreign_keys=[account_fk])
    course_fk = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    course = db.relationship('Course', backref='enrollments', foreign_keys=[course_fk])
    repo = db.Column(db.String(256))
    role = db.Column(db.String(128), nullable=False, default='student')

    def __init__(self, account, course, repo, role):
        self.account_fk = account.id
        self.account = account
        self.course = course
        self.repo = repo
        self.role = role

        db.session.add(self)
        db.session.commit()


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enrollment_fk = db.Column(db.Integer, db.ForeignKey('enrollment.id'), primary_key=True)
    enrollment = db.relationship('Enrollment', backref='submissions', foreign_keys=[enrollment_fk])
    feedback = db.Column(db.Text)
    status = db.Column(db.String(128))

    def __init__(self, enrollment, feedback=None, status='ungraded'):
        self.enrollment_fk = enrollment.id
        self.enrollment = enrollment
        self.feedback = feedback
        self.status = status

        db.session.add(self)
        db.session.commit()


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(128), nullable=False)
    block = db.Column(db.String(1), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, code, block, year, active):
        self.code = code
        self.block = block
        self.year = year
        self.active = active

        db.session.add(self)
        db.session.commit()


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_fk = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course', backref='assignments', foreign_keys=[course_fk])
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    available = db.Column(db.Integer, nullable=False)
    due = db.Column(db.Integer, nullable=False)

    def __init__(self, course, title, description, available, due):
        self.course = course
        self.title = title
        self.description = description
        self.available = available
        self.due = due

        db.session.add(self)
        db.session.commit()

    def active(self):
        current_time = datetime.datetime.now().timestamp()
        return self.available < current_time < self.due  # you can do this? wow
