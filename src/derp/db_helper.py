import datetime

from derp import cur, conn
from flask import request, session

import base64
import random

from psycopg2 import IntegrityError

# globals

# note: this is a gross hack for converting utc to local ... platform dependent and incorrect
#       in general ... do not assume that this will work without checking that it does!
# UTC_OFFSET = datetime.datetime.now() - datetime.datetime.utcnow()
UTC_OFFSET = datetime.timedelta(hours=8)  # worse hack ... difference between PT and UTC


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


class DerpDB:
    # a collection of static methods which return instances of the above objects.
    # ideally the functions inside of these classes will be moved here.
    @staticmethod
    def enrollment(user, course_id):
        sql = """SELECT enrollment.repo AS repo, 
                enrollment.role AS role, 
                course.course_pk AS course_pk, 
                course.code AS code,
                course.block AS block,
                course.year AS year,
                course.active AS active
            FROM enrollment 
            JOIN course ON course.course_pk=enrollment.course_fk
            WHERE user_fk=%s AND course_pk=%s
            LIMIT 1"""
        cur.execute(sql, (user.user_pk, course_id))
        conn.commit()
        i = cur.fetchone()
        if not i:
            return None
        course = Course(i[2], i[3], i[4], i[5], i[6])
        return Enrollment(user, course, i[0], i[1])

    @staticmethod
    def get_user_permission(permission):
        sql = """SELECT account.user_pk, account.github_username, account.student_id, account.email FROM session 
            LEFT JOIN account ON session.user_fk=user_pk 
            INNER JOIN privilege ON privilege.user_fk=user_pk
            WHERE challenge=%s 
                AND student_id=%s 
                AND remote_addr=%s
                AND privilege.name=%s"""
        if not session or 'challenge' not in session or 'student_id' not in session or not request:
            return None
        cur.execute(sql, (session['challenge'], session['student_id'], request.remote_addr, permission))
        conn.commit()
        db_row = cur.fetchone()
        if not db_row:
            return None
        return User(db_row[0], db_row[1], db_row[2], db_row[3])

    @staticmethod
    def add_permissions(user, permissions):
        for permission in permissions:
            sql = """INSERT INTO privilege (user_fk, name) VALUES (%s, %s)"""
            try:
                cur.execute(sql, (user.user_pk, permission))
            except IntegrityError:
                pass  # this means they already had the permission. we can safely ignore
        conn.commit()

    @staticmethod
    def drop_permissions(user):
        sql = """DELETE FROM privilege WHERE user_fk=%s"""
        cur.execute(sql, (user.user_pk,))
        conn.commit()

    @staticmethod
    def session_init(user):
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
        session['challenge'] = challenge
        session['student_id'] = user.student_id
        return Session(db_row[0], user, remote_addr, challenge)

    @staticmethod
    def session_user():
        sql = """SELECT account.user_pk, account.github_username, account.student_id, account.email FROM session 
            LEFT JOIN account ON user_fk=user_pk 
            WHERE challenge=%s 
                AND student_id=%s 
                AND remote_addr=%s"""
        if not session or 'challenge' not in session or 'student_id' not in session or not request:
            return None
        cur.execute(sql, (session['challenge'], session['student_id'], request.remote_addr))
        conn.commit()
        db_row = cur.fetchone()
        if not db_row:
            return None
        return User(db_row[0], db_row[1], db_row[2], db_row[3])


    @staticmethod
    def user_create(github_username, student_id, email):
        sql = """INSERT INTO account (github_username, student_id, email) 
        VALUES (%s, %s, %s) RETURNING user_pk"""
        cur.execute(sql, (github_username, student_id, email))
        conn.commit()
        db_row = cur.fetchone()
        if not db_row:
            # will only happen if the "not null" constraints are violated
            raise DatabaseError("Could not complete create operation.")
        return User(db_row[0], github_username, student_id, email)

    @staticmethod
    def user_query(user_pk=None, github_username=None, student_id=None, email=None, limit=1):
        sql = 'SELECT user_pk, github_username, student_id, email FROM account WHERE '
        params = tuple()
        if user_pk:
            params += (user_pk,)
            sql += 'user_pk = %s AND '
        if github_username:
            params += (github_username,)
            sql += 'github_username = %s AND '
        if student_id:
            params += (student_id,)
            sql += 'student_id = %s AND '
        if email:
            params += (email,)
            sql += 'email = %s AND '
        sql += "TRUE "
        if limit:
            params += (limit,)
            sql += "LIMIT %s"
        cur.execute(sql, params)
        conn.commit()
        if limit == 1:
            u = cur.fetchone()
            if not u:
                return None
            return User(u[0], u[1], u[2], u[3])
        # many results
        res = []
        for u in cur.fetchall():
            res.append(User(u[0], u[1], u[2], u[3]))
        return res


    @staticmethod
    def user_enrollments(user):
        sql = """SELECT enrollment.repo AS repo, 
                enrollment.role AS role, 
                course.course_pk AS course_pk, 
                course.code AS code,
                course.block AS block,
                course.year AS year,
                course.active AS active
            FROM enrollment 
            JOIN course ON course.course_pk=enrollment.course_fk
            WHERE user_fk=%s"""
        cur.execute(sql, (user.user_pk,))
        conn.commit()
        res = []
        for i in cur.fetchall():
            course = Course(i[2], i[3], i[4], i[5], i[6])
            res.append(Enrollment(user, course, i[0], i[1]))
        return res

    @staticmethod
    def user_enroll_course(user, course, repo=None, role=None):
        sql = """INSERT INTO enrollment (user_fk, course_fk, repo, role) VALUES (%s, %s, %s, %s)"""
        cur.execute(sql, (user.user_pk, course.course_pk, repo, role))
        conn.commit()


    @staticmethod
    def course_query(course_pk=None, code=None, block=None, year=None, active=None, limit=1):
        sql = 'SELECT course_pk, code, block, year, active FROM course WHERE '
        params = tuple()
        if course_pk:
            params += (course_pk,)
            sql += 'course_pk = %s AND '
        if code:
            params += (code,)
            sql += 'code = %s AND '
        if block:
            params += (block,)
            sql += 'block = %s AND '
        if year:
            params += (year,)
            sql += 'year = %s AND '
        if active is not None:
            params += (active,)
            sql += 'active = %s AND '
        sql += "TRUE "
        if limit:
            params += (limit,)
            sql += "LIMIT %s"
        cur.execute(sql, params)
        conn.commit()

        if limit == 1:
            c = cur.fetchone()
            if not c:
                return None
            return Course(*c)
        # many results
        res = []
        for i in cur.fetchall():
            res.append(Course(*i))
        return res


    @staticmethod
    def course_create(code, block, year, active):
        sql = """INSERT INTO course (code, block, year, active) 
        VALUES (%s, %s, %s, %s) RETURNING course_pk"""
        cur.execute(sql, (code, block, year, active))
        conn.commit()
        db_row = cur.fetchone()
        if not db_row:
            # will only happen if the "not null" constraints are violated
            raise DatabaseError("Could not complete create operation.")
        return Course(db_row[0], code, block, year, active)

    @staticmethod
    def assignment_create(course, title, description, available, due):
        sql = """INSERT INTO assignment (course_fk, title, description, available, due)
        VALUES (%s, %s, %s, %s, %s) RETURNING assignment_pk"""
        cur.execute(sql, (course.course_pk, title, description, available, due))
        conn.commit()
        db_row = cur.fetchone()
        if not db_row:
            raise DatabaseError("The assignment was not able to be able to be created")
        return Assignment(db_row[0], course, title, description, available, due)

    @staticmethod
    def assignment_query(assignment_pk=None, course_fk=None, limit=1):
        sql = """SELECT course.course_pk, course.code, course.block, course.year, course.active,
              assignment_pk, title, description, available, due FROM assignment
              JOIN course ON course.course_pk=assignment.course_fk WHERE """
        params = tuple()
        if assignment_pk:
            params += (assignment_pk,)
            sql += 'assignment_pk = %s AND '
        if course_fk:
            params += (course_fk,)
            sql += 'course_fk = %s AND '
        sql += "TRUE "
        if limit:
            params += (limit,)
            sql += "LIMIT %s"
        cur.execute(sql, params)
        conn.commit()

        if limit == 1:
            c = cur.fetchone()
            if not c:
                return None
            course = Course(c[0], c[1], c[2], c[3], c[4])
            return Assignment(c[5], course, c[6], c[7], c[8], c[9])
        # many results
        res = []
        for c in cur.fetchall():
            course = Course(c[0], c[1], c[2], c[3], c[4])
            res.append(Assignment(c[5], course, c[6], c[7], c[8], c[9]))
        return res


class Privilege:
    @staticmethod
    def table_init():
        sql = """
        CREATE TABLE IF NOT EXISTS privilege (
            user_fk         INTEGER NOT NULL REFERENCES account(user_pk),
            name            VARCHAR(128) NOT NULL,
            PRIMARY KEY (user_fk, name)
        )
        """
        cur.execute(sql)
        conn.commit()

class Session:
    def __init__(self, session_pk, user, remote_addr, challenge):
        self.session_pk = session_pk
        self.user = user
        self.remote_addr = remote_addr
        self.challenge = challenge

    @staticmethod
    def table_init():
        sql = """
        CREATE TABLE IF NOT EXISTS session (
            session_pk    SERIAL PRIMARY KEY,
            user_fk       INTEGER NOT NULL REFERENCES account(user_pk),
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
    def table_init():  # 'user' is a reserved word in postgres AND I'M ANGRY ABOUT IT
        sql = """CREATE TABLE IF NOT EXISTS account (
            user_pk         serial primary key,
            github_username varchar(128) NOT NULL,
            student_id      varchar(128) UNIQUE NOT NULL,
            email           varchar(128) NOT NULL)"""
        cur.execute(sql)
        conn.commit()

    def courses(self):
        return {
            'active': [e for e in DerpDB.user_enrollments(self) if e.course.active],
            'inactive': [e for e in DerpDB.user_enrollments(self) if not e.course.active],
        }

    def delete(self):
        cur.execute("DELETE FROM account WHERE user_pk=%s", (self.user_pk,))  # TODO check if it was successful
        conn.commit()

    def save(self):
        cur.execute('UPDATE account SET github_username=%s, student_id=%s, email=%s, WHERE user_pk=%s',
                    self.github_username, self.student_id, self.email, self.user_pk)
        conn.commit()

    def has_permission(self, permission):
        sql = """SELECT 1 FROM privilege WHERE user_fk=%s AND name=%s"""
        cur.execute(sql, (self.user_pk, permission))
        conn.commit()
        db_row = cur.fetchone()
        return bool(db_row)  # coerce to boolean value depending on if we found a row or not.


class Enrollment:

    def __init__(self, user, course, repo, role):
        self.user = user
        self.course = course
        self.repo = repo
        self.role = role

    @staticmethod
    def table_init():
        sql = """CREATE TABLE IF NOT EXISTS enrollment (
            user_fk         INTEGER REFERENCES account(user_pk) NOT NULL,
            course_fk       INTEGER REFERENCES course(course_pk) NOT NULL,
            repo            varchar(256),
            role            varchar(128) not null DEFAULT 'student',
            PRIMARY KEY (user_fk, course_fk))"""
        cur.execute(sql)
        conn.commit()


class Course:
    def __init__(self, course_pk, code, block, year, active):
        self.course_pk = course_pk
        self.code = code
        self.block = block
        self.year = year
        self.active = active

    @staticmethod
    def table_init():
        sql = """CREATE TABLE IF NOT EXISTS course (
                course_pk       SERIAL PRIMARY KEY,
                code            VARCHAR(128) NOT NULL,
                block           CHAR(1) NOT NULL,
                year            INTEGER NOT NULL,
                active          BOOLEAN NOT NULL DEFAULT FALSE
            )"""
        # professor_fk    VARCHAR(128) REFERENCES user(user_pk) NOT NULL,
        cur.execute(sql)
        conn.commit()

    def assignments(self):
        return DerpDB.assignment_query(course_fk=self.course_pk, limit=None)


class Assignment:

    def __init__(self, assignment_pk, course, title, description, available, due):
        self.assignment_pk = assignment_pk
        self.course = course
        self.title = title
        self.description = description
        self.available = available
        self.due = due

    @staticmethod
    def table_init():
        sql = """CREATE TABLE IF NOT EXISTS assignment (
            assignment_pk   SERIAL PRIMARY KEY,
            course_fk       INTEGER REFERENCES course(course_pk),
            title           TEXT,
            description     TEXT,
            available       INTEGER NOT NULL,
            due             INTEGER NOT NULL)"""
        cur.execute(sql)
        conn.commit()
