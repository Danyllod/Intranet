"""
Decoradores para controle de acesso baseado em hierarquias de usuário
"""

from functools import wraps
from flask import redirect, url_for, abort
from flask_login import current_user


def login_required_custom(f):
    """Decorator para requer login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator para requer que seja administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


def basico_required(f):
    """Decorator para requer que seja usuário básico ou admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not (current_user.is_basico() or current_user.is_admin()):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def admin_or_basico_required(f):
    """Alias para basico_required"""
    return basico_required(f)
