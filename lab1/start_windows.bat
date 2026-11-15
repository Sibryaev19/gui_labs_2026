@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

rem Minimum required version: Python 3.8
set MINVER=308
set PY=

call :find_python
if "!PY!"=="" (
    echo Python 3.8+ not found on this computer.
    echo Install Python 3.8 or newer from https://www.python.org/downloads/
    echo and run this file again.
    pause
    exit /b 1
)

echo Using Python: !PY!
"!PY!" setup\setup.py || exit /b 1

if exist .venv\Scripts\python.exe (
    set "PY=.venv\Scripts\python.exe"
)
"!PY!" start.py
pause
goto :eof

:find_python
rem 1) python in PATH
for %%c in (python.exe python3.exe) do (
    for /f "delims=" %%p in ('where %%c 2^>nul') do call :check "%%p"
    if not "!PY!"=="" goto :eof
)

rem 2) py launcher
where py >nul 2>nul
if not errorlevel 1 (
    for /f "usebackq delims=" %%p in (`py -c "import sys;print(sys.executable)" 2^>nul`) do call :check "%%p"
    if not "!PY!"=="" goto :eof
)

rem 3) standard install locations
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do if exist "%%D\python.exe" call :check "%%D\python.exe"
if not "!PY!"=="" goto :eof
for /d %%D in ("C:\Python*") do if exist "%%D\python.exe" call :check "%%D\python.exe"
for /d %%D in ("%ProgramFiles%\Python*") do if exist "%%D\python.exe" call :check "%%D\python.exe"
for /d %%D in ("%ProgramFiles(x86)%\Python*") do if exist "%%D\python.exe" call :check "%%D\python.exe"
goto :eof

:check
if defined PY goto :eof
pushd "%~dp1"
for /f "usebackq delims=" %%v in (`%~nx1 -c "import sys;print(sys.version_info[0]*100+sys.version_info[1])" 2^>nul`) do (
    if %%v geq %MINVER% set "PY=%~1"
)
popd
goto :eof
