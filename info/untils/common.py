from flask import session, g
from info.models import User
import logging
from functools import wraps


def do_rank(index):
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''


def get_data_user(viewfun):
    @wraps(viewfun)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id', None)
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                logging.error(e)
        g.user = user
        return viewfun(*args, **kwargs)

    return wrapper
