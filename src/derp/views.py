from flask import render_template, request, redirect, url_for, session, flash
import datetime

from derp import app, cur
from derp.account import login_required


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
