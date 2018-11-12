import datetime

from derp import cur, conn
from flask import request

import base64
import random

# globals

# note: this is a gross hack for converting utc to local ... platform dependent and incorrect
#       in general ... do not assume that this will work without checking that it does!
# UTC_OFFSET = datetime.datetime.now() - datetime.datetime.utcnow()
UTC_OFFSET = datetime.timedelta(hours = 8)  # worse hack ... difference between PT and UTC


# TODO: wrap db queries into functions


"""
class Roles:

    def __init__(self, role_name):
        self.role_name = role_name
        "INSERT INTO roles (role_name) VALUES (%s)"
    
    def get(self, role_pk=None, role_name=None):
        if not role_pk and not role_name:
            raise KeyError("key not provided")
"""


class DatabaseError(Exception):
    pass

# TODO some sort of class registration which will find all of the tables and init them


class Session:
    def __init__(self, session_pk, user, remote_addr, session_challenge):
        self.session_pk = session_pk
        self.user = user
        self.remote_addr = remote_addr
        self.session_challenge = session_challenge

    @staticmethod
    def new_session(self, user):
        remote_addr = request.remote_addr
        challenge = str(base64.b64encode(str(random.getrandbits(256)).encode('ascii')))
        sql = """
        INSERT INTO session (user_fk, remote_addr, challenge) VALUES (%s, %s, %s) RETURNING session_pk
        """
        cur.execute(sql, (user.user_pk, remote_addr, challenge))
        conn.commit()
        db_row = cur.fetchone()
        if not db_row:
            # will only happen if the "not null" constraints are violated
            raise DatabaseError("Could not complete create operation.")
        return Session(db_row['session_pk'], user, remote_addr, challenge)

    @staticmethod
    def table_init():
        sql = """
        CREATE TABLE IF NOT EXISTS session (
            session_pk    SERIAL PRIMARY KEY,
            user_fk       INTEGER NOT NULL REFERENCES user(user_pk),
            remote_addr   VARCHAR(128) NOT NULL,
            challenge     VARCHAR(256) NOT NULL
        )
        """
        cur.execute(sql)
        conn.commit()

class User:
    def __init__(self, user_pk, github_username, student_id, email):
        self.user_pk = user_pk
        self.github_username = github_username
        self.student_id = student_id
        self.email = email

    @staticmethod
    def table_init():
        sql = """CREATE TABLE IF NOT EXISTS user (
            user_pk         serial primary key,
            github_username varchar(128) NOT NULL,
            student_id      varchar(128) UNIQUE NOT NULL,
            email           varchar(128) NOT NULL)"""
        cur.execute(sql)
        conn.commit()

    @staticmethod
    def create(github_username, student_id, email):
        sql = """INSERT INTO user (github_username, student_id, email, repo) 
        VALUES (%s, %s, %s, %s) RETURNING user_pk"""
        cur.execute(sql, (github_username, student_id, email))
        conn.commit()
        db_row = cur.fetchone()
        if not db_row:
            # will only happen if the "not null" constraints are violated
            raise DatabaseError("Could not complete create operation.")
        return User(db_row['user_pk'], github_username, student_id, email)

    @staticmethod
    def get(user_pk=None, github_username=None, student_id=None, email=None, limit=1):
        sql = 'SELECT (user_pk, github_username, student_id, email) FROM user WHERE '
        params = []
        if user_pk:
            params += user_pk
            sql += 'user_pk == %s AND '
        if github_username:
            params += github_username
            sql += 'github_username == %s AND '
        if student_id:
            params += student_id
            sql += 'student_id == %s AND '
        if email:
            params += email
            sql += 'email == %s AND '
        sql += "1 "
        if limit:
            sql += "LIMIT " + limit
        cur.execute(sql, params)
        conn.commit()
        if limit == 1:
            u = cur.fetchone()
            if not u:
                return None
            return User(u['user_pk'], u['github_username'], u['student_id'], u['email'])
        # many results
        res = []
        for u in cur.fetchall():
            res.append(User(u['user_pk'], u['github_username'], u['student_id'], u['email']))
        return res

    def get_courses(self):
        return UserCourse

    def delete(self):
        cur.execute("DELETE FROM user WHERE user_pk=%s", (self.user_pk,))  # TODO check if it was successful
        conn.commit()

    def save(self):
        cur.execute('UPDATE users SET github_username=%s, student_id=%s, email=%s, WHERE user_pk=%s',
                    self.github_username, self.student_id, self.email, self.user_pk)
        conn.commit()
        # TODO check if it was successful


class UserCourse:

    def __init__(self, user, course, repo, role):
        self.user = user
        self.course = course
        self.repo = repo
        self.role = role

    @staticmethod
    def table_init():
        sql = """CREATE TABLE IF NOT EXISTS user_course (
            user_fk         INTEGER REFERENCES user(user_pk) NOT NULL,
            course_fk       INTEGER REFERENCES user(course_pk) NOT NULL,
            repo            varchar(256),
            role            varchar(128) not null DEFAULT 'student'
            PRIMARY KEY (user_fk, course_fk))"""
        cur.execute(sql)
        conn.commit()

    @staticmethod
    def enroll(user, course, repo=None, role=None):
        sql = """INSERT INTO user_course (user_fk, course_fk, repo, role) VALUES (%s, %s, %s, %s)"""
        cur.execute(sql, user.user_pk, course.course_pk, repo, role)
        conn.commit()

    @staticmethod
    def user_courses(self, user):
        sql = """SELECT user_course.repo AS repo, 
                user_course.role AS role, 
                course.course_pk AS course_pk, 
                course.course_code AS course_code
            FROM user_course 
            WHERE user_fk=%s 
            JOIN course ON course.course_pk=user_course.course_fk"""
        cur.execute(sql, user.user_pk)
        conn.commit()
        res = []
        for i in cur.fetchall():
            course = Course(i['course_pk'], i['course_code'])
            res.append(UserCourse(user, course, i['repo'], i['role']))
        return res

"""
Course:
  begin date
  end date
  code

"""
class Course:
    def __init__(self, course_pk, course_code):
        self.course_pk = course_pk
        self.course_code = course_code

    @staticmethod
    def table_init():
        sql = """CREATE TABLE IF NOT EXISTS course (
            course_pk       SERIAL PRIMARY KEY,
            course_code     VARCHAR(128) NOT NULL)"""
        # professor_fk    VARCHAR(128) REFERENCES user(user_pk) NOT NULL,
        cur.execute(sql)
        conn.commit()


    @staticmethod
    def create(course_code):
        sql = """INSERT INTO course (course_code) 
        VALUES (%s) RETURNING course_pk"""
        cur.execute(sql, (course_code,))
        conn.commit()
        db_row = cur.fetchone()
        if not db_row:
            # will only happen if the "not null" constraints are violated
            raise DatabaseError("Could not complete create operation.")
        return Course(db_row['course_pk'], course_code)

    @staticmethod
    def get(course_pk=None, course_code=None, limit=1):
        sql = 'SELECT (user_pk, github_username, student_id, email) FROM user WHERE '
        params = []
        if course_pk:
            params += course_pk
            sql += 'course_pk == %s AND '
        if course_code:
            params += course_code
            sql += 'course_code == %s AND '
        sql += "1 "
        if limit:
            sql += "LIMIT 1"
        cur.execute(sql, params)
        conn.commit()
        if limit == 1:
            c = cur.fetchone()
            if not c:
                return None
            return Course(c['course_pk'], c['course_code'])
        # many results
        res = []
        for i in cur.fetchall():
            res.append(Course(i['course_pk'], i['course_code']))
        return res

    def delete(self):
        cur.execute("DELETE FROM user WHERE course_pk=%s", (self.course_pk,))  # TODO check if it was successful
        conn.commit()

    def save(self):
        cur.execute('UPDATE users SET course_code=%s WHERE user_pk=%s',
                    self.course_code, self.course_pk)
        conn.commit()
        # TODO check if it was successful


class Assignment:
    def __init__(self, course_pk, course_code):
        self.course_pk = course_pk
        self.course_code = course_code

    @staticmethod
    def table_init():
        sql = """CREATE TABLE IF NOT EXISTS assignment (
            assignment_pk   SERIAL PRIMARY KEY
            course_fk       INTEGER REFERENCES course(course_pk),
            course_code     VARCHAR(128) NOT NULL"""
        # professor_fk    VARCHAR(128) REFERENCES user(user_pk) NOT NULL,
        cur.execute(sql)
        conn.commit()

    @staticmethod
    def create(course_code):
        sql = """INSERT INTO course (course_code) 
        VALUES (%s) RETURNING course_pk"""
        cur.execute(sql, (course_code,))
        conn.commit()
        db_row = cur.fetchone()
        if not db_row:
            # will only happen if the "not null" constraints are violated
            raise DatabaseError("Could not complete create operation.")
        return Course(db_row['course_pk'], course_code)

    @staticmethod
    def get(course_pk=None, course_code=None, limit=1):
        sql = 'SELECT (user_pk, github_username, student_id, email) FROM user WHERE '
        params = []
        if course_pk:
            params += course_pk
            sql += 'course_pk == %s AND '
        if course_code:
            params += course_code
            sql += 'course_code == %s AND '
        sql += "1 "
        if limit:
            sql += "LIMIT 1"
        cur.execute(sql, params)
        conn.commit()
        if limit == 1:
            c = cur.fetchone()
            if not c:
                return None
            return Course(c['course_pk'], c['course_code'])
        # many results
        res = []
        for i in cur.fetchall():
            res.append(Course(i['course_pk'], i['course_code']))
        return res

    def delete(self):
        cur.execute("DELETE FROM user WHERE course_pk=%s", (self.course_pk,))  # TODO check if it was successful
        conn.commit()

    def save(self):
        cur.execute('UPDATE users SET course_code=%s WHERE user_pk=%s',
                    self.course_code, self.course_pk)
        conn.commit()
        # TODO check if it was successful


"""
CREATE TABLE dailies (
    daily_pk        serial primary key,
    user_fk         integer REFERENCES  users (user_pk) not null,
    create_dt       timestamp DEFAULT current_timestamp,
    message         varchar(500)
);

CREATE TABLE weeklies (
    weekly_pk       serial primary key,
    user_fk         integer REFERENCES  users (user_pk) not null,
    create_dt       timestamp DEFAULT current_timestamp,
    accomplishments text,
    next_steps      text,
    challenges      text,
    comments        text
);

CREATE TABLE code_reviews (
    review_pk       serial primary key,
    reviewer_fk     integer REFERENCES users(user_pk) not null,  -- who is reviewing
    reviewee_fk     integer REFERENCES users (user_pk) not null, -- who is reviewed
    released        boolean DEFAULT false, -- can the reviewee see the review
    assigned_dt     timestamp, -- date review was assigned
    review_dt       timestamp, -- date of the review
    assignment      varchar(32), -- Which assignment to review for
    comments        text
);

CREATE TABLE results (
    result_pk       serial primary key,
    result_name     varchar(128)
);

CREATE TABLE tests (
    test_pk         serial primary key,
    user_fk         integer REFERENCES  users (user_pk) not null,
    create_dt       timestamp DEFAULT current_timestamp,
    result_fk       integer REFERENCES results (result_pk) not null DEFAULT 1,
    complete_dt     timestamp DEFAULT null,
    message         text DEFAULT 'Test has not run yet'
);

"""
