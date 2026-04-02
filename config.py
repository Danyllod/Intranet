import os
from pathlib import Path

# Diretório raiz do projeto
BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Configuração base para a aplicação Flask"""
    
    # Segurança - Chave secreta
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this-in-production')
    
    # Banco de dados
    INSTANCE_PATH = BASE_DIR / 'instance'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{INSTANCE_PATH / 'reservas.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask - Configurações gerais
    JSON_SORT_KEYS = False
    PREFERRED_URL_SCHEME = 'http'
    
    # Segurança de sessão e cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    # SESSION_COOKIE_SECURE = True  # Descomente em produção com HTTPS


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    TESTING = False
    
    # Em produção, SECRET_KEY DEVE ser definida via variável de ambiente
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production environment")
    
    # Em produção com HTTPS, habilitar secure cookies
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Mapa de configurações
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Selecionar configuração baseado em FLASK_CONFIG (padrão: development)
CONFIG = config_map.get(os.environ.get('FLASK_CONFIG', 'default'), DevelopmentConfig)
