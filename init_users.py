#!/usr/bin/env python
"""
Script para inicializar usuários de teste no banco de dados
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz do projeto ao path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configurar variáveis de ambiente
os.chdir(project_root)

from app import create_app
from app.models import db, User

def init_users():
    """Inicializa usuários de teste"""
    app = create_app()
    
    with app.app_context():
        # Verificar se o usuário admin já existe
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("✓ Usuário administrador 'admin' já existe")
        else:
            # Criar usuário admin
            admin = User(
                username='admin',
                email='admin@cresm.local',
                role='admin',
                ativo=True
            )
            admin.set_password('admin123')  # Padrão de teste
            db.session.add(admin)
            db.session.commit()
            print("✓ Usuário administrador 'admin' criado com sucesso")
            print("  - Email: admin@cresm.local")
            print("  - Senha: admin123")
        
        # Criar alguns usuários básicos de teste
        test_users = [
            ('recepcao', 'recepcao@cresm.local', 'recepcao123'),
            ('atendimento', 'atendimento@cresm.local', 'atendimento123'),
        ]
        
        for username, email, password in test_users:
            user = User.query.filter_by(username=username).first()
            if user:
                print(f"✓ Usuário '{username}' já existe")
            else:
                user = User(
                    username=username,
                    email=email,
                    role='basico',
                    ativo=True
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                print(f"✓ Usuário '{username}' criado com sucesso")
                print(f"  - Email: {email}")
                print(f"  - Senha: {password}")
        
        print("\n" + "="*50)
        print("✓ Inicialização de usuários concluída!")
        print("="*50)

if __name__ == '__main__':
    init_users()
