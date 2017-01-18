from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask.ext.github import GitHub
from CONFIG import HOST, PORT, DEBUG, APP_SECRET_KEY, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, DB_LOCATION
import psycopg2
import datetime
from ast import literal_eval
from operator import attrgetter

from picklesession import PickleSessionInterface
import os

# globals
app  = Flask(__name__)  # instantiate the app here so it can be run as a module
app.config['GITHUB_CLIENT_ID'] = GITHUB_CLIENT_ID
app.config['GITHUB_CLIENT_SECRET'] = GITHUB_CLIENT_SECRET
app.secret_key = str(APP_SECRET_KEY)

path='/dev/shm/derp_sessions'
if not os.path.exists(path):
    os.mkdir(path)
    os.chmod(path, int('700',8))
app.session_interface=PickleSessionInterface(path)

github = GitHub(app)
conn = psycopg2.connect(DB_LOCATION)
cur  = conn.cursor()

# helper functions
def dequote(s):
    """
    If a string has single or double quotes around it, remove them.
    Make sure the pair of quotes match.
    If a matching pair of quotes is not found, return the string unchanged.
    """
    if (s[0] == s[-1]) and s.startswith(("'", '"')):
        return s[1:-1]
    return s

def make_tuple(tuple_string):
    """
    Builds a tuple from a quoted tuple. This is more complicated than it needs to be
    because psycopg2 will return unquoted strings for single word results and double
    quoted strings for whitespace delimited results.
    """
    return tuple(dequote(str(x)) for x in tuple_string[1:-1].split(','))

def is_login_ok():
    """
    Check that a login is sensible. Should be checked before rendering any content.
    """
    if 'github_username' not in session:
        # If there isn't a github_username in the session, authentication hasn't been done
        return False
    if 'duck_id' not in session:
        return False
        
    SQL = "SELECT duck_id,github_username FROM users WHERE github_username=%s and duck_id=%s;"
    data = (session['github_username'],session['duck_id'])
    cur.execute(SQL, data)
    db_row = cur.fetchone()
    if db_row is None:
        return False
    return True
    
# Set "homepage" to index.html
@app.route('/')
@app.route('/index')
def index():
    # Does the session have github credentials? If not go to authentication.
    if not 'github_username' in session:
        return github.authorize()
    # If the user is already signed in, do the credentials match?
    if is_login_ok():
        # User looks alright, let them enter
        return redirect(url_for('dashboard'))
    # Something bad happened... Assume evil.
    return redirect(url_for('logout'))

# get username from homepage input form
@app.route('/signin', methods=['GET', 'POST'])
def signin():

    # this is probably called by a POST from the home page
    if request.method == 'POST':
        duck_id = request.form['duck_id']
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

    # else redirect to the top
    if request.method == 'GET':
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


# display dashboard
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not is_login_ok():
        msg = "login failure: something is wrong with the session ... try logging in again"
        return redirect(url_for("logout", logout_message = msg))
        
    
    # put the user's id from the db into the session
    #   NOTE: all other methods assume that the user_pk has been put into the session
    if 'user_pk' not in session:
        SQL = "SELECT user_pk FROM users WHERE duck_id = %s;"
        data = (session['duck_id'],)
        cur.execute(SQL, data)
        user_pk = cur.fetchone()[0]
        app.logger.debug("setting user_pk: " + str(user_pk))
        session['user_pk'] = user_pk

    # check if the user has submitted a daily status update
    SQL = "SELECT create_dt FROM dailies WHERE user_fk = %s;"
    data = (session['user_pk'],)
    cur.execute(SQL, data)
    timestamps = list(map(lambda t: t[0], cur.fetchall()))
    if timestamps:
        latest_daily_ts = max(timestamps)
        app.logger.debug("latest user daily: " + str(latest_daily_ts))
        current_time = datetime.datetime.now()
        session['daily_completed'] = latest_daily_ts.year == current_time.year and latest_daily_ts.month == current_time.month and latest_daily_ts.day == current_time.day
        app.logger.debug("user completed daily: " + str(session['daily_completed']))
    else:
        session['daily_completed'] = False

    # check if the user has submitted a weekly status update
    SQL = "SELECT create_dt FROM weeklies WHERE user_fk = %s;"
    data = (session['user_pk'],)
    cur.execute(SQL, data)
    timestamps = list(map(lambda t: t[0], cur.fetchall()))
    if timestamps:
        latest_weekly_ts = max(timestamps)
        latest_weekly_wk = latest_weekly_ts.isocalendar()[1]
        app.logger.debug("latest user weekly: " + str(latest_daily_ts))
        current_time = datetime.datetime.now()
        current_wk = current_time.isocalendar()[1]
        session['weekly_completed'] = latest_weekly_wk == current_wk
        app.logger.debug("user completed weekly: " + str(session['weekly_completed']))
    else:
        session['weekly_completed'] = False

    # display the dashboard page
    return render_template('dashboard.html')


# display profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not is_login_ok():
        msg = "login failure: something is wrong with the session ... try logging in again"
        return redirect(url_for("logout", logout_message = msg))
        
    # if we are getting a POST, handle it
    if request.method == 'POST':

        # handle daily status submission
        if 'repo' in request.form and 'email' in request.form:
            repo_msg = request.form['repo']
            email_msg = request.form['email']

            SQL = "UPDATE users SET repo=%s, email=%s WHERE (user_pk=%s);"
            data = (repo_msg, email_msg, session['user_pk'])
            cur.execute(SQL, data)
            conn.commit()

    # get the user's info from the db
    SQL = "SELECT (github_username, duck_id, email, repo) FROM users WHERE duck_id = %s;"
    data = (session['duck_id'],)
    cur.execute(SQL, data)
    res = cur.fetchone()
    session['user_info'] = dict(zip(('github_username', 'duck_id', 'email', 'repo'), make_tuple(res[0])))
    app.logger.debug("setting user_info: {}".format(str(session['user_info'])))

    # in any event, display the profile page
    return render_template('profile.html')


# display daily submission / report page
@app.route('/daily', methods=['GET', 'POST'])
def daily():
    if not is_login_ok():
        msg = "login failure: something is wrong with the session ... try logging in again"
        return redirect(url_for("logout", logout_message = msg))

    # check if the user has submitted a daily status update
    SQL = "SELECT create_dt FROM dailies WHERE user_fk = %s;"
    data = (session['user_pk'],)
    cur.execute(SQL, data)
    timestamps = list(map(lambda t: t[0], cur.fetchall()))
    if timestamps:
        latest_daily_ts = max(timestamps)
        app.logger.debug("latest user daily: " + str(latest_daily_ts))
        current_time = datetime.datetime.now()
        session['daily_completed'] = latest_daily_ts.year == current_time.year and latest_daily_ts.month == current_time.month and latest_daily_ts.day == current_time.day
        app.logger.debug("user completed daily: " + str(session['daily_completed']))
    else:
        session['daily_completed'] = False

    # if we are getting a POST, handle it
    if request.method == 'POST':

        # handle daily status submission
        if 'daily' in request.form:
            message = request.form['daily']
            if len(message) > 500:
                flash("TOO MANY CHARACTERS!!! 500 CHARACTER LIMIT")
                return redirect(url_for("daily"))

            if not session['daily_completed']:
                SQL = "INSERT INTO dailies (user_fk, create_dt, message) VALUES (%s, %s, %s);"
                data = (session['user_pk'], datetime.datetime.now(), message)
                cur.execute(SQL, data)
                conn.commit()
                session['daily_completed'] = True
            else:
                # update the most recent daily entry
                SQL = "UPDATE dailies s SET message=%s FROM (SELECT * FROM dailies WHERE user_fk=%s ORDER BY create_dt DESC LIMIT 1) sub WHERE s.create_dt = sub.create_dt;"
                data = (message, session['user_pk'])
                cur.execute(SQL, data)
                conn.commit()

    # build the report
    #   note: this could be done in the same query as above, but this seems safer
    #         in case the tables change
    SQL = "SELECT (create_dt, message) FROM dailies WHERE user_fk = %s;"
    data = (session['user_pk'],)
    cur.execute(SQL, data)
    res = cur.fetchall()
    app.logger.debug("user daily entries: {}".format(str(res)))
    daily_report = []
    for r in res:
        daily_report.append( dict(zip(('timestamp', 'status_message'), make_tuple(r[0]))) )
    for entry in daily_report:
        entry['timestamp'] = entry['timestamp'].split()[0]
    daily_report.sort(reverse=True, key=lambda entry: entry['timestamp'])
    session['daily_report'] = daily_report
    app.logger.debug("user daily entries session object: {}".format(str(daily_report)))

    # in any event, display the daily page
    return render_template('daily.html')


# display weekly submission / report page
@app.route('/weekly', methods=['GET', 'POST'])
def weekly():
    if not is_login_ok():
        msg = "login failure: something is wrong with the session ... try logging in again"
        return redirect(url_for("logout", logout_message = msg))
    
    # check if the user has submitted a weekly status update
    SQL = "SELECT create_dt FROM weeklies WHERE user_fk = %s;"
    data = (session['user_pk'],)
    cur.execute(SQL, data)
    timestamps = list(map(lambda t: t[0], cur.fetchall()))
    if timestamps:
        latest_weekly_ts = max(timestamps)
        latest_weekly_wk = latest_weekly_ts.isocalendar()[1]
        app.logger.debug("latest user weekly: " + str(latest_weekly_ts))
        current_time = datetime.datetime.now()
        current_wk = current_time.isocalendar()[1]
        session['weekly_completed'] = latest_weekly_wk == current_wk
        app.logger.debug("user completed weekly: " + str(session['weekly_completed']))
    else:
        session['weekly_completed'] = False

    # if we are getting a POST, handle it
    if request.method == 'POST':

        # handle weekly status submission
        if ('accomplishments' in request.form) and ('challenges' in request.form) and ('next_steps' in request.form) and ('comments' in request.form):
            accomplishments_msg = request.form['accomplishments']
            challenges_msg = request.form['challenges']
            next_steps_msg = request.form['next_steps']
            comments_msg = request.form['comments']

            if not session['weekly_completed']:
                SQL = "INSERT INTO weeklies (user_fk, create_dt, accomplishments, challenges, next_steps, comments) VALUES (%s, %s, %s, %s, %s, %s);"
                data = (session['user_pk'], datetime.datetime.now(), accomplishments_msg, challenges_msg, next_steps_msg, comments_msg)
                cur.execute(SQL, data)
                conn.commit()
                session['weekly_completed'] = True
            else:
                SQL = "UPDATE weeklies s SET accomplishments=%s, challenges=%s, next_steps=%s, comments=%s FROM (SELECT * FROM weeklies WHERE user_fk=%s ORDER BY create_dt DESC LIMIT 1) sub WHERE s.create_dt = sub.create_dt;"
                data = (accomplishments_msg, challenges_msg, next_steps_msg, comments_msg, session['user_pk'])
                cur.execute(SQL, data)
                conn.commit()

    # build the report
    #   note: this could be done in the same query as above, but this seems safer
    #         in case the tables change
    SQL = "SELECT (create_dt, accomplishments, challenges, next_steps, comments) FROM weeklies WHERE user_fk = %s;"
    data = (session['user_pk'],)
    cur.execute(SQL, data)
    res = cur.fetchall()
    app.logger.debug("user weekly entries: {}".format(str(res)))
    weekly_report = []
    for r in res:
        weekly_report.append( dict(zip(('timestamp', 'accomplishments', 'challenges', 'next_steps', 'comments'), make_tuple(r[0]))) )
    for entry in weekly_report:
        dt = datetime.datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        monday_of_this_week = dt - datetime.timedelta(days = datetime.datetime.now().weekday())
        entry['timestamp'] = monday_of_this_week.date()
    weekly_report.sort(reverse=True, key=lambda entry: entry['timestamp'])
    session['weekly_report'] = weekly_report
    app.logger.debug("user weekly entries session object: {}".format(str(weekly_report)))

    # in any event, display the weekly page
    return render_template('weekly.html')


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

# if the application is run
if __name__ == '__main__':
    app.secret_key = str(APP_SECRET_KEY)
    app.debug = DEBUG
    app.run(port=PORT, host=HOST)
