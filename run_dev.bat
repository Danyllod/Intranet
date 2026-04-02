@echo off
REM Script para rodar a aplicação em modo desenvolvimento

echo Ativando venv...
call venv\Scripts\activate.bat

echo Iniciando servidor Flask...
python app.py

pause
