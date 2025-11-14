@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════
echo     🔍 בדיקת קבצים לפני העלאה
echo ═══════════════════════════════════════════════════════
echo.

echo ✅ בדיקת server.py...
findstr /C:"eventlet.monkey_patch()" server.py >nul
if %errorlevel%==0 (
    echo    ✓ eventlet.monkey_patch^(^) נמצא!
) else (
    echo    ✗ eventlet.monkey_patch^(^) לא נמצא!
)

echo.
echo ✅ בדיקת קבצי templates...
if exist "templates\login.html" (
    echo    ✓ login.html קיים
) else (
    echo    ✗ login.html חסר!
)

if exist "templates\register.html" (
    echo    ✓ register.html קיים
) else (
    echo    ✗ register.html חסר!
)

if exist "templates\chat.html" (
    echo    ✓ chat.html קיים
) else (
    echo    ✗ chat.html חסר!
)

echo.
echo ✅ בדיקת קבצי static...
if exist "static\style.css" (
    echo    ✓ style.css קיים
) else (
    echo    ✗ style.css חסר!
)

if exist "static\app.js" (
    echo    ✓ app.js קיים
) else (
    echo    ✗ app.js חסר!
)

echo.
echo ✅ בדיקת requirements.txt...
if exist "requirements.txt" (
    echo    ✓ requirements.txt קיים
) else (
    echo    ✗ requirements.txt חסר!
)

echo.
echo ═══════════════════════════════════════════════════════
echo     ✅ בדיקה הושלמה!
echo ═══════════════════════════════════════════════════════
echo.
echo אם כל הקבצים מסומנים ב-✓, אתה מוכן להעלות!
echo הרץ: fix_and_deploy.bat
echo.
pause
