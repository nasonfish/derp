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
    return redirect(url_for('dashboard'))


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')


# display profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # if we are getting a POST, handle it
    if request.method == 'POST':
        # TODO this needs to update information, but only related to the user and not to any classes.
        pass
        # handle profile info submission
        #if 'repo' in request.form and 'email' in request.form:
        #    repo_msg = request.form['repo']
        #    email_msg = request.form['email']

        #    SQL = "UPDATE users SET repo=%s, email=%s WHERE (user_pk=%s);"
        #    data = (repo_msg, email_msg, session['user_pk'])
        #    cur.execute(SQL, data)
        #    conn.commit()
    # in any event, display the profile page
    return render_template('profile.html')
