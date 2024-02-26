from flask import request, abort
from functools import wraps
import parse_data as parse_json_data
import logging


def iap_group_authz(iap_allowlist_final):
    """
    Authorization decorator to be called in every API that needs authorization
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_email = request.headers.get('X-Goog-Authenticated-User-Email')

            logging.info(user_email)
            logging.info(parse_json_data.parse_user_email(user_email))
            logging.info(iap_allowlist_final)
            
            if parse_json_data.parse_user_email(user_email) in iap_allowlist_final:
                return f(*args, **kwargs)
            else:
                abort(403, description="Access is denied, this user is not authorized")
        return decorated_function
    return decorator