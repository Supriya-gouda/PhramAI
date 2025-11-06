Set-Location "d:\AI Medical Prescription\project"
Write-Host "Starting PharmAI Backend Server..." -ForegroundColor Green
Write-Host "URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
