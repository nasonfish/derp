from derp import app
from derp.account import get_session_user


@app.context_processor
def user_information_from_session():
    """A decorated function to give the templates a user object if we're logged in."""
    _user = get_session_user()
    if _user is not None:
        return dict(user=_user)

    return dict()