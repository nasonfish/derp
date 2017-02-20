CREATE TABLE roles (
    role_pk         serial primary key,
    role_name       varchar(128)
);

CREATE TABLE users (
    user_pk         serial primary key,
    github_username varchar(128) not null,
    duck_id         varchar(128) not null,
    email           varchar(128),
    repo            varchar(256),
    role_fk         integer REFERENCES roles (role_pk) not null DEFAULT 1
);

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
