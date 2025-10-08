# Unified Service Launchers

This directory contains unified launcher scripts that simplify running all backend services and optionally the frontend.

## 🚀 Quick Start

### Option 1: Backend Services Only
Run all 4 Python backend services with a single command:

```bash
cd ocr-service
python start_all_services.py
```

This starts:
- **OCR Service** (port 8000) - Receipt OCR processing
- **Food Classification** (port 8001) - Food categorization & calorie calculation
- **AI Shopping List** (port 8002) - Intelligent shopping list generation
- **AI Meal Generator** (port 8003) - AI-powered meal planning

### Option 2: Full Stack (Backend + Frontend)
Run both the Python backend services AND the Next.js frontend:

```bash
cd ocr-service
python start_fullstack.py
```

This starts everything above plus:
- **Next.js Frontend** (port 3000) - Main web application

Then open your browser to: `http://localhost:3000`

## 📋 Service Details

| Service | Port | Purpose |
|---------|------|---------|
| OCR Service | 8000 | Enhanced OCR with Tesseract & OCR.space |
| Food Classification | 8001 | Food category detection & calorie calculation |
| AI Shopping List | 8002 | ML-powered shopping list generation |
| AI Meal Generator | 8003 | Personalized meal planning |
| Next.js Frontend | 3000 | User interface (full stack only) |

## 🛑 Stopping Services

Press **Ctrl+C** in the terminal to gracefully shut down all services.

## 📝 Notes

- The backend launcher (`start_all_services.py`) uses multiprocessing to run all services simultaneously
- The full stack launcher (`start_fullstack.py`) runs both Python and Node.js processes
- All services support hot-reload for development (backend services reload on code changes)
- Logs from all services appear in the same terminal for easy monitoring

## 🔧 Troubleshooting

### Port Already in Use
If you get "port already in use" errors:
1. Stop any existing instances of the services
2. On Windows, run: `netstat -ano | findstr :<PORT>` to find the process using the port
3. Kill the process or use `taskkill /F /PID <PID>`

### Module Not Found
Make sure you're in the `ocr-service` directory when running the scripts:
```bash
cd ocr-service
python start_all_services.py
```

### Frontend Not Starting
The full stack launcher will try to use `pnpm` first, then fall back to `npm`. Make sure you have Node.js and your package manager installed.

## 🆚 Old vs New Method

### Old Method (Manual)
```bash
# Terminal 1
cd ocr-service
python app.py

# Terminal 2
cd ocr-service
python food_service.py

# Terminal 3
cd ocr-service
python ai_shopping_api.py

# Terminal 4
cd ocr-service
python ai_meal_service.py

# Terminal 5 (if running frontend)
npm run dev
```

### New Method (Automated)
```bash
# Option 1: Backend only
cd ocr-service
python start_all_services.py

# Option 2: Full stack
cd ocr-service
python start_fullstack.py
```

Much simpler! 🎉
