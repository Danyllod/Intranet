import os
from flask import Flask
from .extensions import db


def create_app():
    # Get the root directory (parent of 'app' folder)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    app = Flask(__name__, 
                template_folder=os.path.join(root_dir, 'templates'),
                static_folder=os.path.join(root_dir, 'static'))
    app.config['SECRET_KEY'] = 'teste@9090.w'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservas.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensões
    db.init_app(app)
    
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
    
    # Criar tabelas
    with app.app_context():
        db.create_all()
    
    return app
