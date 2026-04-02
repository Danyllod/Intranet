"""
Módulo para carregar variáveis de ambiente do arquivo .env

Este módulo tenta carregar o arquivo .env usando python-dotenv.
Se python-dotenv não estiver instalado, exibe instruções.

Para instalar:
    pip install python-dotenv
"""

from pathlib import Path

# Procurar por arquivo .env no diretório raiz do projeto
env_file = Path(__file__).resolve().parent / '.env'

try:
    from dotenv import load_dotenv
    
    if env_file.exists():
        load_dotenv(str(env_file), override=False)
        print(f"✅ Variáveis de ambiente carregadas de: {env_file}")
    else:
        print(f"⚠️  Arquivo .env não encontrado em: {env_file}")
        print(f"   Copie .env.example para .env e configure seus valores")
        
except ImportError:
    print("⚠️  python-dotenv não está instalado")
    print("   Para carregar .env automaticamente, instale:")
    print("   pip install python-dotenv")
    print()
    if env_file.exists():
        print(f"   Arquivo .env encontrado em: {env_file}")
    else:
        print(f"   Copie .env.example para .env:")
        print(f"   cp .env.example .env")

