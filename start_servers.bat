@echo off
echo.
echo 🚀 Starting YUH Smart Grocery App Servers...
echo.

REM Get the directory where this batch file is located
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo 📁 Project Directory: %PROJECT_DIR%
echo.

echo 🔍 Starting OCR Service on port 8000...
start "OCR Service" cmd /k "cd /d "%PROJECT_DIR%ocr-service" && python app.py"
timeout /t 3 > nul

echo 🍎 Starting Food Classification Service on port 8001...
start "Food Service" cmd /k "cd /d "%PROJECT_DIR%ocr-service" && python food_service.py"
timeout /t 3 > nul

echo ⚛️ Starting Next.js Frontend on port 3000...
start "Next.js App" cmd /k "cd /d "%PROJECT_DIR%" && npm run dev"
timeout /t 3 > nul

echo.
echo 🎉 All servers are starting up!
echo.
echo 📱 Access the application at:
echo    • Frontend: http://localhost:3000
echo    • OCR API: http://localhost:8000/docs  
echo    • Food API: http://localhost:8001/docs
echo.
echo ⚠️  Close the individual terminal windows to stop the servers
echo.
pause