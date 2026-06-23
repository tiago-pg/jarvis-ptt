@echo off
cd /d "%~dp0"
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo Iniciando Jarvis...
python main.py
pause
