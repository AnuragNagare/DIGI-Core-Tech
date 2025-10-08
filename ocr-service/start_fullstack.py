#!/usr/bin/env python3
"""
Full Stack Launcher
Starts both the Next.js frontend and all Python backend services
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Get project root (parent of ocr-service)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
BACKEND_DIR = PROJECT_ROOT / "ocr-service"

def main():
    """Start both frontend and backend services"""
    
    print("=" * 70)
    print("🚀 FULL STACK LAUNCHER")
    print("=" * 70)
    print("\n📦 Starting all services...")
    print("\n🌐 Services:")
    print("  Frontend (Next.js):         http://localhost:3000")
    print("  OCR Service:                http://localhost:8000")
    print("  Food Classification:        http://localhost:8001")
    print("  AI Shopping List:           http://localhost:8002")
    print("  AI Meal Generator:          http://localhost:8003")
    print("\n" + "=" * 70)
    print("\n⏳ Initializing...\n")
    
    processes = []
    
    try:
        # Start Python backend services
        print("🐍 Starting Python backend services...")
        backend_process = subprocess.Popen(
            [sys.executable, "start_all_services.py"],
            cwd=BACKEND_DIR,
            shell=False
        )
        processes.append(("Backend Services", backend_process))
        time.sleep(5)  # Give backend time to start
        
        # Start Next.js frontend
        print("\n⚛️  Starting Next.js frontend...")
        
        # Check if npm or pnpm is available
        try:
            subprocess.run(["pnpm", "--version"], capture_output=True, check=True)
            npm_cmd = "pnpm"
        except (subprocess.CalledProcessError, FileNotFoundError):
            npm_cmd = "npm"
        
        frontend_process = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=PROJECT_ROOT,
            shell=True  # Required for Windows to find npm/pnpm
        )
        processes.append(("Frontend", frontend_process))
        
        print("\n" + "=" * 70)
        print("✅ FULL STACK RUNNING")
        print("=" * 70)
        print("\n🌐 Open your browser to: http://localhost:3000")
        print("\n💡 Press Ctrl+C to stop all services\n")
        
        # Keep running
        while True:
            time.sleep(1)
            # Check if any process has died
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n⚠️  WARNING: {name} has stopped unexpectedly!")
                    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("🛑 SHUTTING DOWN ALL SERVICES")
        print("=" * 70)
        
        # Terminate all processes
        for name, proc in processes:
            if proc.poll() is None:
                print(f"  Stopping {name}...")
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"  Force killing {name}...")
                    proc.kill()
        
        print("\n✅ All services stopped successfully")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        for _, proc in processes:
            if proc.poll() is None:
                proc.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
