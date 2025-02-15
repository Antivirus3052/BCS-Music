REM filepath: /c:/Users/gaysu/Desktop/Music_BotVS/start.bat
@echo off
echo Starte Discord Music Bot...

REM Wechsle in das Verzeichnis, in dem sich die main.py befindet
cd /d "%~dp0"

REM Aktiviere das virtuelle Environment
call venv\Scripts\activate.bat

REM Prüfe ob venv aktiviert wurde
if errorlevel 1 (
    echo Fehler beim Aktivieren des virtuellen Environments.
    echo Stelle sicher, dass du ein venv mit "python -m venv venv" erstellt hast.
    pause
    exit /b 1
)

REM Starte den Bot
python main.py

REM Deaktiviere venv beim Beenden
deactivate

pause