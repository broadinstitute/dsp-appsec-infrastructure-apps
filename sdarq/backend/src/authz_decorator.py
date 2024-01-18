from flask import request, abort
from functools import wraps

def iap_group_authz(allowed_groups):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_group = request.headers.get('X-User-Group')
            if user_group in allowed_groups:
                return f(*args, **kwargs)
            else:
                abort(403, description="Access denied: User not allowed to perform this action")
        return decorated_function
    return decorator