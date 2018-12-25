import datetime

from derp import app
from derp.account import get_session_user

from flask import request, url_for


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


@app.template_filter('relative_date')
def relative_date(epoch):
    """
    :param epoch: Integer representation of a date
    :return: A string describing the date
    """
    return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d (%A %B %d)')
    # TODO revisit this and show, perhaps, "fourth tuesday" or "in 3 days/3 days ago"



@app.context_processor
def user_information_from_session():
    _user = get_session_user()
    if _user is not None:
        return dict(user=_user)
    return dict()


def breadcrumb(endpoint, page, **kwargs):
    if request.url_rule.endpoint == endpoint:
        return '<li class="breadcrumb-item active" aria-current="page">{page}</li>'.format(page=page)
    return '<li class="breadcrumb-item"><a href="{url}">{page}</a></li>'.format(url=url_for(endpoint, **kwargs), page=page)
