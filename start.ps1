# Start the Smart Traffic Light System

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Smart Traffic Light System - Starting..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Start Django server
Write-Host ""
Write-Host "Starting Django web server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Dashboard will be available at:" -ForegroundColor Green
Write-Host "  http://localhost:8000" -ForegroundColor White
Write-Host "  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver 0.0.0.0:8000
