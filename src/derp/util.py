from derp import app
from derp.account import get_session_user

from flask import request, url_for


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
