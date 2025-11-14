@echo off
echo Installing SSL certificate generator...
pip install pyOpenSSL
echo.
echo Generating SSL certificate...
python generate_cert.py
echo.
echo Done! Now run the server with run.bat
pause
