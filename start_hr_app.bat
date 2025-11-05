@echo off
:: ===============================
::  PLAX HR APP - Startup Script
::  (C) 2025 Riccardo Leonelli
:: ===============================

setlocal enabledelayedexpansion

set APPDIR=C:\Users\Plax\Desktop\Apps\hr-app
set VENV=%APPDIR%\.venv

echo --------------------------------------
echo [PLAX HR] Avvio applicazione...
cd /d %APPDIR%

:: Attiva il virtual environment
if not exist "%VENV%\Scripts\activate.bat" (
    echo [PLAX HR] Creazione virtual env...
    py -3 -m venv "%VENV%"
)

call "%VENV%\Scripts\activate.bat"

:: Installa o aggiorna requirements se modificati
if exist "%APPDIR%\requirements_installed.txt" (
    for %%A in ("%APPDIR%\requirements.txt") do set RQTIME=%%~tA
    for %%B in ("%APPDIR%\requirements_installed.txt") do set INSTTIME=%%~tB
    if "!RQTIME!" gtr "!INSTTIME!" (
        echo [PLAX HR] Aggiornamento pacchetti...
        pip install --upgrade pip >nul
        pip install -r "%APPDIR%\requirements.txt"
        copy /y "%APPDIR%\requirements.txt" "%APPDIR%\requirements_installed.txt" >nul
    ) else (
        echo [PLAX HR] Pacchetti aggiornati, nessuna reinstallazione necessaria.
    )
) else (
    echo [PLAX HR] Installazione iniziale pacchetti...
    pip install --upgrade pip >nul
    pip install -r "%APPDIR%\requirements.txt"
    copy /y "%APPDIR%\requirements.txt" "%APPDIR%\requirements_installed.txt" >nul
)

:: Avvia l'app FastAPI
echo [PLAX HR] Avvio server...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

echo [PLAX HR] Server terminato.
pause
