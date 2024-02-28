from flask import request, abort
from functools import wraps
import parse_data as parse_json_data
from iap_userinfo import validate_iap_jwt
import logging

def iap_group_authz(iap_allowlist_final):
    """
    Authorization decorator to be called in every API 
    that needs authorization to be enforced
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            iap_jwt = request.headers.get('X-Goog-IAP-JWT-Assertion')
            expected_audience = '/projects/497778860653/global/backendServices/456958800953465934'
            user_id, user_email, error_str = validate_iap_jwt(iap_jwt, expected_audience)

            logging.info(user_id, user_email, error_str)

            if parse_json_data.parse_user_email(user_email) in iap_allowlist_final:
                return f(*args, **kwargs)
            else:
                abort(403, description="Access is denied, this user is not authorized")
        return decorated_function
    return decorator