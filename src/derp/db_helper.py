import datetime

from derp import cur, conn

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


class User:

    def __init__(self, user_pk, github_username, student_id, role, email=None, repo=None):
        self.user_pk = user_pk
        self.github_username = github_username
        self.student_id = student_id
        self.role = role
        self.email = email
        self.repo = repo

    @staticmethod
    def table_init():
        sql = """CREATE TABLE IF NOT EXISTS user (
            user_pk         serial primary key,
            github_username varchar(128) not null,
            student_id      varchar(128) not null,
            email           varchar(128),
            repo            varchar(256),
            role_fk         varchar(128) not null DEFAULT 'student'"""
        cur.execute(sql)
        conn.commit()

    @staticmethod
    def create(github_username, student_id, role, email=None, repo=None):
        sql = """INSERT INTO user (github_username, student_id, email, repo, role) 
        VALUES (%s, %s, %s, %s, %s) RETURNING user_pk"""
        cur.execute(sql, (github_username, student_id, email, repo, role))
        conn.commit()
        db_row = cur.fetchone()
        if not db_row:
            # will only happen if the "not null" constraints are violated
            raise DatabaseError("Could not complete create operation.")
        return User(db_row['user_pk'], github_username, student_id, role, email, repo)

    @staticmethod
    def get(github_username=None, student_id=None, email=None, repo=None, role=None, limit=1):
        sql = 'SELECT (user_pk, github_username, student_id, email, repo, role) FROM user WHERE '
        params = []
        if github_username:
            params += github_username
            sql += 'github_username == %s AND '
        if student_id:
            params += student_id
            sql += 'student_id == %s AND '
        if email:
            params += email
            sql += 'email == %s AND '
        if repo:
            params += repo
            sql += 'repo == %s AND '
        if role:
            params += role
            sql += 'role == %s AND '
        sql += "1 "
        if limit:
            sql += "LIMIT 1"
        cur.execute(sql, params)
        conn.commit()
        u = cur.fetchone()
        return User(u['user_pk'], u['github_username'], u['student_id'], u['email'], u['repo'], u['role'])

    def delete(self):
        cur.execute("DELETE FROM user WHERE user_pk=%s", (self.pk,))  # TODO check if it was successful

    def save(self):
        cur.execute('UPDATE users SET github_username=%s, student_id=%s, email=%s, repo=%s, role=%s WHERE user_pk=%s',
                    self.github_username, self.student_id, self.email, self.repo, self.role, self.user_pk)
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