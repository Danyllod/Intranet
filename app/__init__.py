import os
from pathlib import Path
from flask import Flask
from .extensions import db, login_manager


def create_app(config=None):
    """
    Application Factory Pattern
    
    Cria e configura a instância da aplicação Flask com blueprints e extensões.
    
    Args:
        config: Classe de configuração customizada (opcional).
                Se None, carrega CONFIG de config.py
    
    Returns:
        Flask: Instância da aplicação configurada
    """
    # Diretório raiz do projeto
    root_dir = Path(__file__).resolve().parent.parent
    
    # Criar app com instance_relative_config para melhor gestão de dados locais
    app = Flask(
        __name__,
        template_folder=str(root_dir / 'templates'),
        static_folder=str(root_dir / 'static'),
        instance_relative_config=True
    )
    
    # Garantir que pasta instance/ existe
    Path(app.instance_path).mkdir(exist_ok=True)
    
    # Carregar configuração
    if config is None:
        from config import CONFIG
        app.config.from_object(CONFIG)
    else:
        app.config.from_object(config)
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    # Carregar usuário para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from . import models
        return models.User.query.get(int(user_id))
    
    # Registrar blueprints
    from app.main import main_bp
    from app.revista import revista_bp
    from app.salas import salas_bp
    from app.senhas import senhas_bp
    from app.auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(revista_bp)
    app.register_blueprint(salas_bp)
    app.register_blueprint(senhas_bp)
    app.register_blueprint(auth_bp)
    
    # Context processor para variáveis globais de template
    @app.context_processor
    def inject_globals():
        """Injeta variáveis globais em todos os templates"""
        return {
            'include_navbar': True  # Padrão: mostrar navbar
        }
    
    # Criar tabelas do banco de dados
    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()
    
    return app
