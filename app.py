# Carregar variáveis de ambiente do arquivo .env (se existir)
import dotenv_loader  # noqa: F401

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
