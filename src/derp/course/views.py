from derp import app
from derp.account import login_required, get_session_user, permission_required
from derp.course import course
from derp.db_helper import UserCourse, Course, DerpDB

from flask import render_template, abort, request, flash, redirect, url_for


# GET /course/
@course.route('/')
@login_required
def index():
    return render_template("course/list.html")


@course.route('/<id>')
@login_required
def view(id):
    user = get_session_user()
    user_course = DerpDB.user_course(user, id)
    if not user_course:
        return abort(404)
    return render_template("course/view.html", user_course=user_course)


@course.route('/create', methods=['GET', 'POST'])
@permission_required('course:create')
def create():
    if request.method == 'POST':
        block = request.form['block']
        if len(block) > 1:
            flash("Block must be a one-character identifier, such as 'A' or '1'", 'danger')
            return render_template('course/create.html')
        year = request.form['year']
        try:
            int(year)
        except ValueError:
            flash("Year must be a number.", 'danger')
            return render_template('course/create.html')
        code = request.form['code']
        course = Course.create(code, block, year)
        UserCourse.enroll(get_session_user(), course, None, 'professor')
        flash('Course successfully created', 'success')
        return redirect(url_for('.view', id=course.course_pk))
    return render_template('course/create.html')



#
# # display daily submission / report page
# @app.route('/daily', methods=['GET', 'POST'])
# def daily():
#     if not is_login_ok():
#         msg = "login failure: something is wrong with the session ... try logging in again"
#         return redirect(url_for("logout", logout_message = msg))
#
#     # check if the user has submitted a daily status update
#     check_daily()
#
#     # if we are getting a POST, handle it
#     if request.method == 'POST':
#
#         # handle daily status submission
#         if 'daily' in request.form:
#             message = request.form['daily']
#             if len(message) > 500:
#                 flash("TOO MANY CHARACTERS!!! 500 CHARACTER LIMIT")
#                 return redirect(url_for("daily"))
#
#             # Can't trust the session... use the stored proc to handle
#             #if not session['daily_completed']:
#             #    SQL = "INSERT INTO dailies (user_fk, create_dt, message) VALUES (%s, %s, %s);"
#             #    data = (session['user_pk'], datetime.datetime.utcnow(), message)
#             #    cur.execute(SQL, data)
#             #    conn.commit()
#             #    session['daily_completed'] = True
#             #else:
#                 # update the most recent daily entry
#             #    SQL = "UPDATE dailies s SET message=%s FROM (SELECT * FROM dailies WHERE user_fk=%s ORDER BY create_dt DESC LIMIT 1) sub WHERE s.create_dt = sub.create_dt;"
#             #    data = (message, session['user_pk'])
#             #    cur.execute(SQL, data)
#             #    conn.commit()
#             SQL = "select add_daily(%s,%s);"
#             data = (session['duck_id'],message)
#             cur.execute(SQL, data)
#             conn.commit()
#             session['daily_completed'] = True
#
#     # build the report
#     #   note: this could be done in the same query as above, but this seems safer
#     #         in case the tables change
#     SQL = "SELECT (create_dt-interval '6 hours')::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'PST', message FROM dailies WHERE user_fk = %s;"
#     data = (session['user_pk'],)
#     cur.execute(SQL, data)
#     res = cur.fetchall()
#     #app.logger.debug("user daily entries: {}".format(str(res)))
#     daily_report = []
#     for r in res:
#         e = dict()
#         e['timestamp']=r[0]
#         e['status_message']=r[1]
#         daily_report.append(e)
#
#     daily_report.sort(reverse=True, key=lambda entry: entry['timestamp'])
#     session['daily_report'] = daily_report
#     app.logger.debug("user daily entries session object: {}".format(str(daily_report)))
#
#     # in any event, display the daily page
#     return render_template('daily.html')
#
#
# # display weekly submission / report page
# @app.route('/weekly', methods=['GET', 'POST'])
# def weekly():
#     if not is_login_ok():
#         msg = "login failure: something is wrong with the session ... try logging in again"
#         return redirect(url_for("logout", logout_message = msg))
#
#     # check if the user has submitted a weekly status update
#     check_weekly()
#
#     # if we are getting a POST, handle it
#     if request.method == 'POST':
#
#         # handle weekly status submission
#         if ('accomplishments' in request.form) and ('challenges' in request.form) and ('next_steps' in request.form) and ('comments' in request.form):
#             accomplishments_msg = request.form['accomplishments']
#             challenges_msg = request.form['challenges']
#             next_steps_msg = request.form['next_steps']
#             comments_msg = request.form['comments']
#
#             if not session['weekly_completed']:
#                 SQL = "INSERT INTO weeklies (user_fk, create_dt, accomplishments, challenges, next_steps, comments) VALUES (%s, %s, %s, %s, %s, %s);"
#                 data = (session['user_pk'], datetime.datetime.utcnow(), accomplishments_msg, challenges_msg, next_steps_msg, comments_msg)
#                 cur.execute(SQL, data)
#                 conn.commit()
#                 session['weekly_completed'] = True
#             else:
#                 SQL = "UPDATE weeklies s SET accomplishments=%s, challenges=%s, next_steps=%s, comments=%s FROM (SELECT * FROM weeklies WHERE user_fk=%s ORDER BY create_dt DESC LIMIT 1) sub WHERE s.create_dt = sub.create_dt;"
#                 data = (accomplishments_msg, challenges_msg, next_steps_msg, comments_msg, session['user_pk'])
#                 cur.execute(SQL, data)
#                 conn.commit()
#
#     # build the report
#     #   note: this could be done in the same query as above, but this seems safer
#     #         in case the tables change
#     SQL = "SELECT (create_dt-interval '6 hours')::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'PST', accomplishments, challenges, next_steps, comments FROM weeklies WHERE user_fk = %s;"
#     data = (session['user_pk'],)
#     cur.execute(SQL, data)
#     res = cur.fetchall()
#     app.logger.debug("user weekly entries: {}".format(str(res)))
#     weekly_report = []
#     for r in res:
#         e = dict()
#         e['timestamp']=r[0]
#         e['accomplishments']=r[1]
#         e['challenges']=r[2]
#         e['next_steps']=r[3]
#         e['comments']=r[4]
#         weekly_report.append(e)
#     weekly_report.sort(reverse=True, key=lambda entry: entry['timestamp'])
#     session['weekly_report'] = weekly_report
#     app.logger.debug("user weekly entries session object: {}".format(str(weekly_report)))
#
#     # in any event, display the weekly page
#     return render_template('weekly.html')
#
#
# # display code review
# @app.route('/code_review', methods=['GET', 'POST'])
# def code_review():
#     if not is_login_ok():
#         msg = "login failure: something is wrong with the session ... try logging in again"
#         return redirect(url_for("logout", logout_message = msg))
#
#     # if we are getting a POST, handle it
#     if request.method == 'POST':
#
#         # handle weekly status submission:
#         #   - strip the review_pk off the form name
#         #   - update the db with the current timestamp
#         review_pk = None
#         comments_msg = None
#         for key in request.form:
#             if key.startswith('review.'):
#                 review_pk = key.partition('.')[-1]
#                 comments_msg = request.form[key]
#
#         if review_pk is not None and comments_msg is not None:
#             SQL = "UPDATE code_reviews SET review_dt=%s, comments=%s WHERE (review_pk=%s);"
#             data = (datetime.datetime.utcnow(), comments_msg, review_pk)
#             cur.execute(SQL, data)
#             conn.commit()
#
#     # check for pending code reviews
#     check_pending_reviews()
#
#     # build the report
#     SQL = "SELECT review_dt, comments FROM code_reviews WHERE (reviewee_fk = %s AND released = true);"
#     data = (session['user_pk'],)
#     cur.execute(SQL, data)
#     res = cur.fetchall()
#     app.logger.debug("user code review entries: {}".format(str(res)))
#     review_report = []
#     for r in res:
#         review_report.append( dict(zip(('timestamp', 'comments'), r)) )
#     review_report.sort(reverse=True, key=lambda entry: entry['timestamp'])
#     session['review_report'] = review_report
#     app.logger.debug("code review report session object: {}".format(str(review_report)))
#
#     # in any event, display the weekly page
#     return render_template('code_review.html')
#
