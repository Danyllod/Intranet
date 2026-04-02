#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para recria o banco de dados completamente.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Remover arquivos antigos de banco de dados se possível
db_path = 'instance/reservas.db'
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"✅ Arquivo antigo removido")
    except:
        pass

from app import create_app, db

# Criar aplicação
app = create_app()

with app.app_context():
    print("🔄 Dropando todas as tabelas...")
    try:
        db.drop_all()
        print("✅ Tabelas removidas")
    except Exception as e:
        print(f"⚠️  Erro ao dropar: {e}")
    
    print("\n📊 Criando novo banco de dados com o novo schema...")
    db.create_all()
    print("✅ Banco de dados criado com sucesso!")
    
    # Verificar tabelas
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\n📋 Tabelas criadas: {tables}")
    
    # Verificar colunas da tabela senhas
    if 'senhas' in tables:
        columns = inspector.get_columns('senhas')
        print(f"\n📝 Colunas da tabela 'senhas':")
        colnames = []
        for col in columns:
            colnames.append(col['name'])
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"   - {col['name']}: {col['type']} ({nullable})")
        
        # Verificar se is_prioridade existe
        if 'is_prioridade' in colnames:
            print("\n✅ Coluna 'is_prioridade' encontrada!")
        else:
            print("\n❌ Coluna 'is_prioridade' NOT FOUND!")
