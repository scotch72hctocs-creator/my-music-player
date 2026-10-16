@echo off
cd /d "%~dp0"
chcp 65001 >nul
echo My Music Player - Free version
where py >nul 2>nul
if %errorlevel%==0 (
    py -m pip install -r requirements.txt
    if errorlevel 1 goto failed
    py app.py
) else (
    python -m pip install -r requirements.txt
    if errorlevel 1 goto failed
    python app.py
)
echo.
echo The program has stopped.
pause
exit /b
:failed
echo.
echo Installation failed. Please copy the error message.
pause
