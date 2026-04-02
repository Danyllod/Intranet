"""
Blueprint para módulo de Painel de Senhas
Gerencia fila de atendimento, chamada de senhas e relatórios.
"""

from flask import Blueprint

senhas_bp = Blueprint(
    "senhas",
    __name__,
    url_prefix="/senhas"
)

# Importar rotas para registrar no blueprint
from . import routes  # noqa: F401
