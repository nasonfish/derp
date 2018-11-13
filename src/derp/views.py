from flask import render_template, request, redirect, url_for, session, flash
import datetime

from derp import app, cur, conn, github
from derp.account import get_session_user, login_required

# jinja2 format functions
@app.template_filter('monday')
def format_monday(dt):
    """
    Input: datetime object
    Output: date object representing the monday preceding the input datetime
    """
    return (dt - datetime.timedelta(days = dt.weekday())).date()

@app.template_filter('to_date')
def format_date(dt):
    """
    Input: datetime object
    Output: date object
    """
    return dt.date()

def check_daily():
    """
    Check whether the user has submitted a daily status today, where 'today' is defined
    as the 24-hour period stretching from the prior 0600 to the next 0600.
    """
    # Select only the records for today
    SQL = """SELECT create_dt::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'PST'
FROM dailies
WHERE date_trunc('day',(now()-interval '6 hours')::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'PST') = date_trunc('day',(create_dt-interval '6 hours')::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'PST')
and user_fk=%s"""
    data = (session['user_pk'],)
    cur.execute(SQL, data)
    db_row = cur.fetchone()
    if db_row is None:
        session['daily_completed'] = False
    else:
        session['daily_completed'] = True


def check_weekly():
    """
    Check whether the user has submitted a weekly status this week, where 'this week'
    is defined as the period stretching from the prior 0600 Monday to the next 0600 Monday.
    """
    # Select only the records for this week
    SQL = """SELECT create_dt::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'PST'
FROM weeklies
WHERE date_trunc('week',(now()-interval '6 hours')::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'PST') = date_trunc('week',(create_dt-interval '6 hours')::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'PST')
and user_fk=%s"""
    data = (session['user_pk'],)
    cur.execute(SQL, data)
    db_row = cur.fetchone()
    if db_row is None:
        session['weekly_completed'] = False
    else:
        session['weekly_completed'] = True


def check_pending_reviews():
    """
    Check whether the user has pending code reviews to complete. Puts the pending review
    information into the session.
    """
    SQL = "SELECT review_pk, reviewee_fk, assignment FROM code_reviews WHERE (reviewer_fk = %s AND review_dt IS NULL);"
    data = (session['user_pk'],)
    cur.execute(SQL, data)
    res = cur.fetchall()
    app.logger.debug("user pending code reviews query: {}".format(str(res)))
    pending_reviews = []
    for r in res:
        pending_reviews.append( dict(zip(('review_pk', 'reviewee_fk', 'assignment'), r)) )
    for entry in pending_reviews:
        SQL = "SELECT repo FROM users WHERE user_pk = %s;"
        data = (entry['reviewee_fk'],)
        cur.execute(SQL, data)
        res = cur.fetchone()[0]
        entry['url'] = res
    session['pending_reviews'] = pending_reviews
    app.logger.debug("pending reviews session: {}".format(session['pending_reviews']))


# Set "homepage" to index.html
@app.route('/')
@app.route('/index')
@login_required
def index():
    # Does the session have github credentials? If not go to authentication.
    #if not 'github_username' in session:
    #    return github.authorize()
    # If the user is already signed in, do the credentials match?
    #if get_session_user():
        # User looks alright, let them enter
    return redirect(url_for('dashboard'))
    # Something bad happened... Assume evil.
    #return redirect(url_for('logout'))


# display dashboard
@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # display the dashboard page
    return render_template('dashboard.html')


# display profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # if we are getting a POST, handle it
    if request.method == 'POST':

        # handle profile info submission
        if 'repo' in request.form and 'email' in request.form:
            repo_msg = request.form['repo']
            email_msg = request.form['email']

            SQL = "UPDATE users SET repo=%s, email=%s WHERE (user_pk=%s);"
            data = (repo_msg, email_msg, session['user_pk'])
            cur.execute(SQL, data)
            conn.commit()

    # get the user's info from the db
    SQL = "SELECT github_username, duck_id, email, repo FROM users WHERE duck_id = %s;"
    data = (session['duck_id'],)
    cur.execute(SQL, data)
    res = cur.fetchone()
    session['user_info'] = dict(zip(('github_username', 'duck_id', 'email', 'repo'), res))
    app.logger.debug("setting user_info: {}".format(str(session['user_info'])))

    # in any event, display the profile page
    return render_template('profile.html')
