    CREATE TABLE IF NOT EXISTS privilege (
        user_fk         INTEGER NOT NULL REFERENCES account(user_pk),
        name            VARCHAR(128) NOT NULL,
        PRIMARY KEY (user_fk, name)
    )


    CREATE TABLE IF NOT EXISTS session (
        session_pk    SERIAL PRIMARY KEY,
        user_fk       INTEGER NOT NULL REFERENCES account(user_pk),
        remote_addr   VARCHAR(128) NOT NULL,
        challenge     VARCHAR(256) NOT NULL
    )

    CREATE TABLE IF NOT EXISTS account (
        user_pk         serial primary key,
        github_username varchar(128) NOT NULL,
        student_id      varchar(128) UNIQUE NOT NULL,
        email           varchar(128) NOT NULL
    )
    
    CREATE TABLE IF NOT EXISTS enrollment (
        user_fk         INTEGER REFERENCES account(user_pk) NOT NULL,
        course_fk       INTEGER REFERENCES course(course_pk) NOT NULL,
        repo            varchar(256),
        role            varchar(128) not null DEFAULT 'student',
        PRIMARY KEY (user_fk, course_fk)
    )
    
    CREATE TABLE IF NOT EXISTS course (
        course_pk       SERIAL PRIMARY KEY,
        code            VARCHAR(128) NOT NULL,
        block           CHAR(1) NOT NULL,
        year            INTEGER NOT NULL
    )
    
    CREATE TABLE IF NOT EXISTS assignment (
        assignment_pk   SERIAL PRIMARY KEY,
        course_fk       INTEGER REFERENCES course(course_pk),
        title           TEXT,
        description     TEXT
        available       TIMESTAMPZ NOT NULL,
        due             TIMESTAMPZ NOT NULL
    )


Users ("accounts") may have many privileges. Users may have many sessions. Users may have many enrollments. An enrollment associates a user with one class. Many students can be enrolled in one class. A course may have many assignments.


TODO: Create "submissions" table which associates an enrollment with an assignment, and has information about the submission. Alternatively, don't do this, and just have submissions automatically happen after the due date.