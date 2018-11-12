from functools import wraps
from derp import cur, conn
from flask import session, redirect, url_for

# helper functions
def is_login_ok():
    """
    Check that a login is sensible. Should be checked before rendering any content.
    """
    if 'user_id' not in session:
        # If there isn't a github_username in the session, authentication hasn't been done
        return False
    if 'user_challenge' not in session:
        return False

    SQL = "SELECT duck_id,github_username FROM users WHERE github_username=%s and duck_id=%s;"
    data = (session['github_username'],session['duck_id'])
    cur.execute(SQL, data)
    db_row = cur.fetchone()
    conn.commit()
    if db_row is None:
        return False
    return True

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_login_ok():
            msg = "login failure: something is wrong with the session ... try logging in again"
            return redirect(url_for("logout", logout_message = msg))
        return decorated_function(*args, **kwargs)

def user():
    pass


# get username from homepage input form
@app.route('/login', methods=['GET', 'POST'])
def login():

    # this is probably called by a POST from the home page
    if request.method == 'POST':
        student_id = request.form['student_id']
        if not duck_id:
            flash("Please try again!")
            return redirect(url_for("index"))

        session['duck_id'] = duck_id

        # handle the login attempt
        if 'logged_in' not in session:

            # check if the user is in the db, and redirect to the correct location
            SQL = "SELECT duck_id FROM users WHERE duck_id = %s;"
            data = (duck_id,)
            cur.execute(SQL, data)
            if not cur.fetchone():
                app.logger.debug("user not in db ... redirecting to signup")
                return redirect(url_for("signup"))
            else:
                app.logger.debug("user found ... redirecting to authorization")
                return github.authorize()

        # else user is already logged in
        else:
            return redirect(url_for("dashboard"))
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
        flash("Authorization failed!")
        return redirect(url_for("index"))

    # Add github information to the session
    session['github_access_token'] = access_token
    session['github_username'] = github.get('user')['login']

    # Check for the duck_id based on the github username
    SQL = "SELECT duck_id FROM users WHERE github_username=%s;"
    data = (session['github_username'],)
    cur.execute(SQL, data)
    db_row = cur.fetchone()

    if db_row is None:
        # No user registered in the DB... Go to the signup page.
        return redirect(url_for('signup'))

    db_duck_id = db_row[0]
    app.logger.debug("db duck_id: {}".format(db_duck_id))
    session['logged_in'] = db_duck_id
    session['duck_id']   = db_duck_id

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



