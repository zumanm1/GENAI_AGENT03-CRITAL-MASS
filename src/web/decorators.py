from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(role_name):
    """
    Decorator that checks if a user has a specific role.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized

            # Check if user has the required role
            has_role = any(
                role.name == role_name for role in current_user.roles)

            if not has_role:
                abort(403)  # Forbidden

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def roles_required(*role_names):
    """
    Decorator that checks if a user has any of the specified roles.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized

            # Check if user has any of the required roles
            has_any_role = any(
                role.name in role_names for role in current_user.roles)

            if not has_any_role:
                abort(403)  # Forbidden

            return f(*args, **kwargs)
        return decorated_function
    return decorator
