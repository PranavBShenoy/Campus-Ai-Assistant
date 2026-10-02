# CampusAI Startup Script
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "       CampusAI Startup Script         " -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "[1/3] Checking Backend..." -ForegroundColor Yellow
Set-Location "backend"
$backendCheck = py -3.9 -c "import main" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Backend failed to load. Please fix the error below:" -ForegroundColor Red
    Write-Host $backendCheck
    Read-Host "Press Enter to exit"
    exit 1
}
Set-Location ..

Write-Host "[2/3] Checking Frontend..." -ForegroundColor Yellow
Set-Location "frontend"
if (!(Test-Path "node_modules")) {
    Write-Host "[INFO] node_modules not found. Installing frontend dependencies..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] npm install failed." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}
Set-Location ..

Write-Host "[3/3] Starting Services..." -ForegroundColor Yellow

# Start backend in a new window
Start-Process -FilePath "cmd.exe" -ArgumentList "/c title CampusAI Backend && cd /d `"$ScriptDir\backend`" && py -3.9 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 || pause"

Start-Sleep -Seconds 3

# Start frontend in a new window
Start-Process -FilePath "cmd.exe" -ArgumentList "/c title CampusAI Frontend && cd /d `"$ScriptDir\frontend`" && npm run dev || pause"

Write-Host ""
Write-Host "Both services have been started in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Keep those terminal windows open while you use CampusAI."
Write-Host "To stop, simply close the terminal windows."
Write-Host ""
