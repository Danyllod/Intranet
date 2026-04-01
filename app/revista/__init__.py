from flask import Blueprint

revista_bp = Blueprint('revista', __name__, url_prefix='/revista')

from . import routes
