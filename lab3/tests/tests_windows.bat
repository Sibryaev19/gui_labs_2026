@echo off
setlocal
cd /d %~dp0\..

rem Tests must run on the prepared virtual environment only.
if not exist .venv\Scripts\python.exe (
    echo Virtual environment not found: .venv\Scripts\python.exe
    echo Run start_windows.bat first - it creates .venv and installs the libraries.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo Library PyQt5 is missing in .venv.
    echo Run start_windows.bat first - it installs the required libraries.
    pause
    exit /b 1
)

set QT_QPA_PLATFORM=offscreen
".venv\Scripts\python.exe" tests\run_tests.py
set RC=%errorlevel%
pause
exit /b %RC%
