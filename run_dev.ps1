# Script PowerShell para rodar a aplicação em modo desenvolvimento

Write-Host "Ativando venv..." -ForegroundColor Cyan
. .\venv\Scripts\Activate.ps1

Write-Host "Iniciando servidor Flask..." -ForegroundColor Green
python app.py
