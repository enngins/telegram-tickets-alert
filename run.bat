@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Creare venv...
    python -m venv .venv
    if errorlevel 1 ( py -3.11 -m venv .venv )
    if not exist ".venv\Scripts\python.exe" ( echo Nu s-a putut crea venv. & exit /b 1 )
)
echo Instalare pachete...
.venv\Scripts\python.exe -m pip install telethon requests python-dotenv
if errorlevel 1 ( echo Eroare la instalare. & exit /b 1 )
set DOTENV_PATH=%cd%\.env
.venv\Scripts\python.exe main.py --once
