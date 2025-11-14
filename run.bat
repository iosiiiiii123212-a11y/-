@echo off
echo Installing/Updating dependencies...
pip install -r requirements.txt --quiet
echo.
echo Starting WhatsApp Clone Server...
python server.py
pause
