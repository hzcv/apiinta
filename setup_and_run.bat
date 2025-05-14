@echo off

REM Install dependencies
echo [*] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Run the bot script
echo [*] Running bot...
python login.py

REM Keep console open after running
pause
