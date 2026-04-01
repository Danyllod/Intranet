from flask import Blueprint

senhas_bp = Blueprint('senhas', __name__, url_prefix='/senhas')

from . import routes
