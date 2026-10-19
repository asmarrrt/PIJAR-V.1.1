from functools import wraps
from flask import abort
from flask_login import current_user,login_required
def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        @login_required
        def wrapped(*a,**kw):
            if not current_user.is_authenticated or current_user.role not in roles or not current_user.is_active: abort(403)
            return fn(*a,**kw)
        return wrapped
    return deco
