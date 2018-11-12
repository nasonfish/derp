from functools import wraps
from derp import cur, conn, app, github
from flask import session, redirect, url_for, request, flash

from derp.db_helper import Session, User

# helper functions
def is_login_ok():
    """
    Check that a login is sensible. Should be checked before rendering any content.
    """
    return Session.get_user()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_login_ok():
            return redirect(url_for("login"))
        return decorated_function(*args, **kwargs)


# get username from homepage input form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_login_ok():
        return redirect(url_for("dashboard"))
    # this is probably called by a POST from the home page
    if request.method == 'POST':
        student_id = request.form.get('student_id', False)
        if not student_id:
            flash("Please provide your student ID.", 'error')
            return redirect(url_for("index"))
        # check if the user is in the db, and redirect to the correct location
        user = User.get(student_id=student_id)
        if not user:
            app.logger.debug("user not in db ... redirecting to signup")
            return redirect(url_for("signup"))
        else:
            app.logger.debug("user found ... redirecting to authorization")
            return github.authorize()
    return redirect(url_for("index"))


# github access token getter
@github.access_token_getter
def token_getter():
    return session.get('github_access_token', None)


# handle github authentication
@app.route('/github_callback')
@github.authorized_handler
def authorized(access_token):
    app.logger.debug("entering authoriztion callback")

    if access_token is None:
        flash("Authorization failed!", 'error')
        return redirect(url_for("index"))

    # Add github information to the session
    session['github_access_token'] = access_token
    session['github_username'] = github.get('user')['login']

    user = User.get(github_username=session['github_username'])
    if user is None:
        # No user registered in the DB... Go to the signup page.
        return redirect(url_for('signup'))

    # a successful login!
    sess = Session.new_session(user)
    app.logger.debug("Session id: {}".format(sess.session_pk))
    session['student_id'] = sess.user.student_id
    session['session_challenge'] = sess.challenge
    return redirect(url_for("dashboard"))


# display signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Check that the session has at least the github credential
    if 'github_username' not in session:
        # Illegal entrance
        return redirect(url_for('logout'))
    # if it's a GET request, display the sign up page
    if request.method == 'GET':
        return render_template('signup.html')

    # if it's POST, save the user information to the database
    # and redirect to the index (so the user can authenticate through github)
    #   note: default role is developer
    if request.method == 'POST':
        github_username = session['github_username']
        repo = request.form['repo']
        email = request.form['email']
        duck_id = request.form['duck_id']
        cur.execute("SELECT role_pk FROM roles WHERE role_name = %s;", ('developer',))
        developer_fk = cur.fetchone()[0]
        app.logger.debug("got developer pk from roles table: {}".format(developer_fk))
        SQL = "INSERT INTO users (github_username, duck_id, email, repo, role_fk) VALUES (%s, %s, %s, %s, %s);"
        data = (github_username, duck_id, email, repo, developer_fk)
        cur.execute(SQL, data)
        conn.commit()
        return redirect(url_for("index"))


@app.route('/logout')
def logout(logout_message = None):
    if request.args.get("logout_message") is not None:
        app.logger.debug("got logout message: " + request.args.get("logout_message"))
        session.clear()
        flash(request.args.get("logout_message"))
    else:
        session.clear()
    return render_template('logout.html')



