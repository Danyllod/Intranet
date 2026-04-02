#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para reinicializar o banco de dados com o novo schema.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
import shutil

# Criar aplicação
app = create_app()

with app.app_context():
    # Tentar remover arquivo de banco de dados
    db_path = 'instance/reservas.db'
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"✅ Arquivo de banco de dados removido: {db_path}")
        except Exception as e:
            print(f"❌ Erro ao remover banco: {e}")
            print(f"   Tentando com backup...")
            try:
                shutil.move(db_path, db_path + '.backup')
                print(f"✅ Banco movido para backup: {db_path}.backup")
            except Exception as e2:
                print(f"❌ Erro ao mover: {e2}")
    
    # Criar novo banco de dados  
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
        for col in columns:
            print(f"   - {col['name']}: {col['type']}")
