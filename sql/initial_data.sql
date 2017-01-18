BEGIN;
INSERT INTO roles (role_name) VALUES ('new user');
INSERT INTO roles (role_name) VALUES ('developer');
INSERT INTO roles (role_name) VALUES ('manager');

INSERT INTO results (result_name) VALUES ('in queue');
INSERT INTO results (result_name) VALUES ('cancelled');
INSERT INTO results (result_name) VALUES ('running');
INSERT INTO results (result_name) VALUES ('passed');
INSERT INTO results (result_name) VALUES ('failed');
INSERT INTO results (result_name) VALUES ('partial');
END;