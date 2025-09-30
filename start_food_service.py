#!/usr/bin/env python3
"""
Startup script for Food Classification Service
Run this to start the food classification service
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🍎 Starting Food Classification Service...")
    print("📱 Service will be available at: http://localhost:8001")
    print("🔍 Health check: http://localhost:8001/health")
    print("📚 API docs: http://localhost:8001/docs")
    print("\nPress Ctrl+C to stop the service")
    
    # Change to the ocr-service directory
    service_dir = Path(__file__).parent / "ocr-service"
    os.chdir(service_dir)
    
    try:
        # Start the service
        subprocess.run([
            sys.executable, "food_service.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except Exception as e:
        print(f"❌ Error starting service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
