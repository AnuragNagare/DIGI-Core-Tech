#!/usr/bin/env python3
"""
Unified Backend Service Launcher
Starts all 4 backend services on their respective ports
"""

import multiprocessing
import uvicorn
import sys
import os
import time
import signal
from pathlib import Path

# Get the directory of this script
SCRIPT_DIR = Path(__file__).parent.resolve()

# Add the ocr-service directory to Python path
sys.path.insert(0, str(SCRIPT_DIR))

def run_ocr_service():
    """Run the main OCR service on port 8000"""
    print(f"🔍 Starting OCR Service on port 8000...")
    os.chdir(SCRIPT_DIR)
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

def run_food_service():
    """Run the food classification service on port 8001"""
    print(f"🍎 Starting Food Classification Service on port 8001...")
    os.chdir(SCRIPT_DIR)
    uvicorn.run(
        "food_service:app",
        host="0.0.0.0",
        port=8001,
        reload=False,  # Disable reload for subprocess
        log_level="info"
    )

def run_ai_shopping_service():
    """Run the AI shopping list service on port 8002"""
    print(f"🛒 Starting AI Shopping List Service on port 8002...")
    os.chdir(SCRIPT_DIR)
    uvicorn.run(
        "ai_shopping_api:app",
        host="0.0.0.0",
        port=8002,
        reload=False,  # Disable reload for subprocess
        log_level="info"
    )

def run_ai_meal_service():
    """Run the AI meal generator service on port 8003"""
    print(f"🍽️  Starting AI Meal Generator Service on port 8003...")
    os.chdir(SCRIPT_DIR)
    uvicorn.run(
        "ai_meal_service:app",
        host="0.0.0.0",
        port=8003,
        reload=False,  # Disable reload for subprocess
        log_level="info"
    )

def main():
    """Start all services using multiprocessing"""
    
    print("=" * 70)
    print("🚀 UNIFIED BACKEND LAUNCHER")
    print("=" * 70)
    print("\nStarting all backend services...")
    print("\n📋 Service Ports:")
    print("  • OCR Service:              http://localhost:8000")
    print("  • Food Classification:      http://localhost:8001")
    print("  • AI Shopping List:         http://localhost:8002")
    print("  • AI Meal Generator:        http://localhost:8003")
    print("\n" + "=" * 70)
    print("\n⏳ Initializing services...\n")
    
    # Create processes for each service
    processes = []
    
    try:
        # Start OCR service
        p1 = multiprocessing.Process(target=run_ocr_service, name="OCR-Service")
        p1.start()
        processes.append(p1)
        time.sleep(2)  # Give it time to start
        
        # Start Food Classification service
        p2 = multiprocessing.Process(target=run_food_service, name="Food-Service")
        p2.start()
        processes.append(p2)
        time.sleep(2)
        
        # Start AI Shopping service
        p3 = multiprocessing.Process(target=run_ai_shopping_service, name="Shopping-Service")
        p3.start()
        processes.append(p3)
        time.sleep(2)
        
        # Start AI Meal service
        p4 = multiprocessing.Process(target=run_ai_meal_service, name="Meal-Service")
        p4.start()
        processes.append(p4)
        time.sleep(2)
        
        print("\n" + "=" * 70)
        print("✅ ALL SERVICES RUNNING")
        print("=" * 70)
        print("\n💡 Press Ctrl+C to stop all services\n")
        
        # Keep the main process running
        while True:
            time.sleep(1)
            # Check if any process has died
            for i, proc in enumerate(processes):
                if not proc.is_alive():
                    print(f"\n⚠️  WARNING: {proc.name} has stopped unexpectedly!")
                    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("🛑 SHUTTING DOWN ALL SERVICES")
        print("=" * 70)
        
        # Terminate all processes
        for proc in processes:
            if proc.is_alive():
                print(f"  Stopping {proc.name}...")
                proc.terminate()
                proc.join(timeout=5)
                if proc.is_alive():
                    print(f"  Force killing {proc.name}...")
                    proc.kill()
        
        print("\n✅ All services stopped successfully")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        for proc in processes:
            if proc.is_alive():
                proc.terminate()
        sys.exit(1)

if __name__ == "__main__":
    # Required for Windows multiprocessing
    multiprocessing.freeze_support()
    main()
