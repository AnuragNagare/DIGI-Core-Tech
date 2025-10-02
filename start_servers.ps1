# Start all servers for YUH Smart Grocery App

# Get the current directory
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host "🚀 Starting YUH Smart Grocery App Servers..." -ForegroundColor Green
Write-Host "📁 Project Directory: $projectDir" -ForegroundColor Yellow

# Start OCR Service (Port 8000)
Write-Host "`n🔍 Starting OCR Service on port 8000..." -ForegroundColor Cyan
$ocrProcess = Start-Process python -ArgumentList "app.py" -WorkingDirectory "$projectDir\ocr-service" -PassThru -WindowStyle Minimized
Write-Host "✅ OCR Service started (PID: $($ocrProcess.Id))" -ForegroundColor Green

# Wait a moment
Start-Sleep -Seconds 3

# Start Food Classification Service (Port 8001)
Write-Host "`n🍎 Starting Food Classification Service on port 8001..." -ForegroundColor Cyan
$foodProcess = Start-Process python -ArgumentList "food_service.py" -WorkingDirectory "$projectDir\ocr-service" -PassThru -WindowStyle Minimized
Write-Host "✅ Food Classification Service started (PID: $($foodProcess.Id))" -ForegroundColor Green

# Wait a moment
Start-Sleep -Seconds 3

# Start Next.js App (Port 3000)
Write-Host "`n⚛️ Starting Next.js Frontend on port 3000..." -ForegroundColor Cyan
$nextProcess = Start-Process npm -ArgumentList "run", "dev" -WorkingDirectory "$projectDir" -PassThru -WindowStyle Minimized
Write-Host "✅ Next.js App started (PID: $($nextProcess.Id))" -ForegroundColor Green

Write-Host "`n🎉 All servers started successfully!" -ForegroundColor Green
Write-Host "`n📱 Access the application at:" -ForegroundColor Yellow
Write-Host "   • Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   • OCR API: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Food API: http://localhost:8001/docs" -ForegroundColor White

Write-Host "`n⚠️  Press Ctrl+C to stop all servers" -ForegroundColor Red

# Keep the script running and monitor the processes
try {
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Check if processes are still running
        $ocrRunning = Get-Process -Id $ocrProcess.Id -ErrorAction SilentlyContinue
        $foodRunning = Get-Process -Id $foodProcess.Id -ErrorAction SilentlyContinue
        $nextRunning = Get-Process -Id $nextProcess.Id -ErrorAction SilentlyContinue
        
        if (-not $ocrRunning) { Write-Host "❌ OCR Service stopped" -ForegroundColor Red }
        if (-not $foodRunning) { Write-Host "❌ Food Service stopped" -ForegroundColor Red }
        if (-not $nextRunning) { Write-Host "❌ Next.js App stopped" -ForegroundColor Red }
    }
}
catch {
    Write-Host "`n🛑 Stopping all servers..." -ForegroundColor Yellow
    
    # Stop all processes
    Stop-Process -Id $ocrProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $foodProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $nextProcess.Id -Force -ErrorAction SilentlyContinue
    
    Write-Host "✅ All servers stopped" -ForegroundColor Green
}