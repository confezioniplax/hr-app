@echo off
:: ===============================
::  PLAX HR APP - Startup Script
::  (C) 2025 Riccardo Leonelli
:: ===============================

setlocal enabledelayedexpansion

set "APPDIR=C:\Users\Plax\Desktop\Apps\hr-app"
set "VENV=%APPDIR%\.venv"
set "LOGFILE=%APPDIR%\hr_app.log"

echo --------------------------------------
echo [PLAX HR] Avvio applicazione...
echo [%DATE% %TIME%] ==== AVVIO SCRIPT ==== >> "%LOGFILE%"

:: Vai nella cartella dell'app
cd /d "%APPDIR%"
if errorlevel 1 (
    echo [PLAX HR] ERRORE: impossibile fare CD in %APPDIR%.
    echo [%DATE% %TIME%] ERRORE: impossibile fare CD in %APPDIR%. >> "%LOGFILE%"
    pause
    exit /b 1
)

:: Crea il virtual env se non esiste
if not exist "%VENV%\Scripts\activate.bat" (
    echo [PLAX HR] Creazione virtual env...
    echo [%DATE% %TIME%] Creazione virtual env... >> "%LOGFILE%"
    py -3 -m venv "%VENV%"
)

:: Attiva il virtual environment
call "%VENV%\Scripts\activate.bat"

:: Controllo veloce che l'interprete del venv esista
if not exist "%VENV%\Scripts\python.exe" (
    echo [PLAX HR] ERRORE: python.exe non trovato nel venv.
    echo [%DATE% %TIME%] ERRORE: python.exe non trovato nel venv. >> "%LOGFILE%"
    pause
    exit /b 1
)

:: Installa o aggiorna requirements se modificati
if exist "%APPDIR%\requirements_installed.txt" (
    for %%A in ("%APPDIR%\requirements.txt") do set RQTIME=%%~tA
    for %%B in ("%APPDIR%\requirements_installed.txt") do set INSTTIME=%%~tB
    if "!RQTIME!" gtr "!INSTTIME!" (
        echo [PLAX HR] Aggiornamento pacchetti...
        echo [%DATE% %TIME%] Aggiornamento pacchetti... >> "%LOGFILE%"
        pip install --upgrade pip >> "%LOGFILE%" 2>&1
        pip install -r "%APPDIR%\requirements.txt" >> "%LOGFILE%" 2>&1
        copy /y "%APPDIR%\requirements.txt" "%APPDIR%\requirements_installed.txt" >nul
    ) else (
        echo [PLAX HR] Pacchetti aggiornati, nessuna reinstallazione necessaria.
        echo [%DATE% %TIME%] Pacchetti già aggiornati, nessuna reinstallazione. >> "%LOGFILE%"
    )
) else (
    echo [PLAX HR] Installazione iniziale pacchetti...
    echo [%DATE% %TIME%] Installazione iniziale pacchetti... >> "%LOGFILE%"
    pip install --upgrade pip >> "%LOGFILE%" 2>&1
    pip install -r "%APPDIR%\requirements.txt" >> "%LOGFILE%" 2>&1
    copy /y "%APPDIR%\requirements.txt" "%APPDIR%\requirements_installed.txt" >nul
)

:: Avvia l'app FastAPI
echo [PLAX HR] Avvio server...
echo [%DATE% %TIME%] Avvio Uvicorn... >> "%LOGFILE%"

"%VENV%\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 >> "%LOGFILE%" 2>&1

echo [PLAX HR] Server terminato.
echo [%DATE% %TIME%] Uvicorn terminato con codice %ERRORLEVEL%. >> "%LOGFILE%"
echo [PLAX HR] Codice uscita: %ERRORLEVEL%

echo --------------------------------------
echo Controlla il file di log:
echo   %LOGFILE%
pause
