from derp import app
from derp.account import get_session_user


@app.context_processor
def user_information_from_session():
    _user = get_session_user()
    if _user is not None:
        return dict(user=_user)

    return dict()
