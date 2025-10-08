# 🚀 Quick Reference Card

## How to Run Everything

### Option 1: Backend Only (Recommended for testing)
```powershell
cd ocr-service
python start_all_services.py
```
Then in another terminal:
```powershell
npm run dev
```

### Option 2: Full Stack (Everything at once)
```powershell
cd ocr-service
python start_fullstack.py
```
Then open: http://localhost:3000

### Stop All Services
Press `Ctrl+C` in the terminal

---

## How to Use Manual Selection

1. **Go to Tracking page** in the app
2. **Click "Scan Receipt"** button
3. **Upload a receipt** from `sample_images/` folder
4. **Wait for OCR** to extract items (2-3 seconds)
5. **Review items** - all are selected by default
6. **Deselect unwanted items** by clicking them
7. **Click "Add X Items to Inventory"**
8. **Done!** Selected items are now in inventory

---

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| OCR | 8000 | http://localhost:8000/docs |
| Food Classification | 8001 | http://localhost:8001/docs |
| AI Shopping | 8002 | http://localhost:8002/docs |
| AI Meal Generator | 8003 | http://localhost:8003/docs |

---

## Files Changed

### Modified
- ✏️ `app/page.tsx` - Added manual selection UI

### New
- ⭐ `ocr-service/start_all_services.py` - Backend launcher
- ⭐ `ocr-service/start_fullstack.py` - Full stack launcher
- ⭐ `ocr-service/LAUNCHER_README.md` - Documentation
- ⭐ `FEATURE_UPDATE_SUMMARY.md` - Detailed summary
- ⭐ `VISUAL_GUIDE.md` - Visual diagrams
- ⭐ `QUICK_REFERENCE.md` - This file

---

## Troubleshooting

### Port 8000 already in use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /F /PID <PID>
```

### Frontend won't start
```powershell
# Install dependencies
npm install
# or
pnpm install

# Then start
npm run dev
```

### Backend services crash
```powershell
# Make sure you're in the right directory
cd ocr-service

# Check Python version (should be 3.8+)
python --version

# Install dependencies
pip install -r requirements.txt
```

---

## Git Commands (When Ready)

```bash
# Stage changes
git add app/page.tsx ocr-service/*.py ocr-service/*.md *.md

# Commit
git commit -m "feat: Add manual item selection + unified launchers"

# Push
git push origin main
```

---

## Key Features

### ✨ Manual Selection
- All items selected by default
- Click items to toggle selection
- Green border = selected
- Shows: name, quantity, unit, category, expiry
- "Select All" / "Deselect All" buttons
- Dynamic "Add X Items" button
- Cancel without adding

### ✨ Unified Launchers
- Start all 4 backend services with one command
- Optional: Start frontend + backend together
- Graceful shutdown with Ctrl+C
- Logs from all services in one terminal
- Hot-reload enabled (changes auto-reload)

---

## What's Next?

1. **Test the manual selection:**
   - Upload various receipt images
   - Try selecting/deselecting items
   - Verify correct items are added

2. **Test the launchers:**
   - Try backend-only launcher
   - Try full-stack launcher
   - Verify all services start correctly
   - Test graceful shutdown

3. **Approve and commit:**
   - Once everything works, approve the changes
   - Use git commands above to commit & push

---

**Need Help?** Check:
- `FEATURE_UPDATE_SUMMARY.md` - Detailed explanation
- `VISUAL_GUIDE.md` - Visual diagrams
- `ocr-service/LAUNCHER_README.md` - Launcher docs

**Status:** ✅ Ready for testing
**Git Status:** 🔒 Not committed (awaiting approval)
