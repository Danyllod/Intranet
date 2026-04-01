from flask import Blueprint

salas_bp = Blueprint('salas', __name__, url_prefix='/agenda-salas')

from . import routes
