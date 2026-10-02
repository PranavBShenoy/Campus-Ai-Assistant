@echo off
setlocal
echo =======================================
echo        CampusAI Startup Script
echo =======================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Backend...
cd backend
py -3.9 -c "import main" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Backend failed to load. There might be a syntax error or missing dependency.
    echo Running check to show the error:
    py -3.9 -c "import main"
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
cd ..

echo [2/3] Checking Frontend...
cd frontend
if not exist "node_modules\" (
    echo [INFO] node_modules not found. Installing frontend dependencies...
    call npm install
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] npm install failed.
        pause
        exit /b 1
    )
)
cd ..

echo [3/3] Starting Services...
echo.
start "CampusAI Backend" cmd /k "title CampusAI Backend && cd /d "%~dp0backend" && py -3.9 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

start "CampusAI Frontend" cmd /k "title CampusAI Frontend && cd /d "%~dp0frontend" && npm run dev"

echo.
echo Both services have been started in separate windows!
echo.
echo Frontend: http://localhost:3000
echo Backend API Docs: http://localhost:8000/docs
echo.
echo Keep those terminal windows open while you use CampusAI.
echo To stop, simply close the terminal windows.
echo.
pause
