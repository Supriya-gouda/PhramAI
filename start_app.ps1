# PharmAI Application Startup Script
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "   PharmAI Application Startup   " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location "d:\AI Medical Prescription\project"

# Check Python installation
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host "`n[2/5] Checking dependencies..." -ForegroundColor Yellow
python -c "import fastapi, uvicorn, streamlit, pandas, pydantic; print('✅ All core packages installed')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Missing dependencies! Run: pip install -r requirements.txt" -ForegroundColor Red
    exit 1
}

# Check data files
Write-Host "`n[3/5] Checking data files..." -ForegroundColor Yellow
if (Test-Path "backend\data\processed\interactions.parquet") {
    Write-Host "✅ Data files found" -ForegroundColor Green
} else {
    Write-Host "❌ Data files missing!" -ForegroundColor Red
    exit 1
}

# Start Backend Server
Write-Host "`n[4/5] Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\AI Medical Prescription\project'; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
Write-Host "✅ Backend starting on http://127.0.0.1:8000" -ForegroundColor Green
Start-Sleep -Seconds 5

# Verify backend is running
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 3 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        $backendRunning = $true
        Write-Host "✅ Backend is online!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Backend starting (may take a moment)..." -ForegroundColor Yellow
}

# Start Frontend
Write-Host "`n[5/5] Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\AI Medical Prescription\project\frontend'; streamlit run app.py --server.headless=true"
Write-Host "✅ Frontend starting on http://localhost:8501" -ForegroundColor Green
Start-Sleep -Seconds 5

# Final status
Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "   Application Status             " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Backend:  http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:8501" -ForegroundColor Green
Write-Host "API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "`nOpen http://localhost:8501 in your browser!" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Cyan
