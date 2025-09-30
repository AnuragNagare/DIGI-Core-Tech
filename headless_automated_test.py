#!/usr/bin/env python3
"""
Headless Automated OCR Testing & Fixing System
Continuously tests and fixes OCR issues without user intervention
"""

import requests
import json
import time
import os
import sys
import subprocess
import threading
from datetime import datetime
import base64
from PIL import Image, ImageDraw, ImageFont
import io

class HeadlessOCRTester:
    def __init__(self):
        self.ocr_service_url = "http://localhost:8000"
        self.api_endpoint = "http://localhost:3000/api/ocr/receipt"
        self.test_results = []
        self.is_running = True
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        sys.stdout.flush()
    
    def check_services(self):
        """Check if all required services are running"""
        services = {
            "ocr_service": f"{self.ocr_service_url}/health",
            "api_endpoint": self.api_endpoint
        }
        
        for name, url in services.items():
            try:
                if name == "api_endpoint":
                    # Test API endpoint with simple POST
                    response = requests.post(url, json={"test": True}, timeout=5)
                else:
                    response = requests.get(url, timeout=5)
                
                if response.status_code < 400:
                    self.log(f"✅ {name} is responding")
                else:
                    self.log(f"❌ {name} returned status {response.status_code}", "ERROR")
                    return False
                    
            except requests.exceptions.ConnectionError:
                self.log(f"❌ {name} is not reachable", "ERROR")
                return False
            except Exception as e:
                self.log(f"❌ Error checking {name}: {str(e)}", "ERROR")
                return False
        
        return True
    
    def create_test_receipt(self, filename, content="Test Receipt"):
        """Create a synthetic test receipt image"""
        try:
            # Create a simple test receipt
            img = Image.new('RGB', (400, 300), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            # Draw receipt content
            draw.text((10, 10), "TEST RECEIPT", fill='black', font=font)
            draw.text((10, 40), f"Date: {datetime.now().strftime('%Y-%m-%d')}", fill='black', font=font)
            draw.text((10, 70), "Items:", fill='black', font=font)
            draw.text((10, 100), "1. Apples - $2.50", fill='black', font=font)
            draw.text((10, 120), "2. Milk - $3.00", fill='black', font=font)
            draw.text((10, 140), "3. Bread - $2.00", fill='black', font=font)
            draw.text((10, 170), f"Total: $7.50", fill='black', font=font)
            
            # Save to file
            img.save(filename, 'JPEG')
            self.log(f"✅ Created test receipt: {filename}")
            return True
            
        except Exception as e:
            self.log(f"❌ Error creating test receipt: {str(e)}", "ERROR")
            return False
    
    def test_ocr_direct(self):
        """Test OCR service directly"""
        try:
            # Create test image
            test_file = "test_direct.jpg"
            if not self.create_test_receipt(test_file):
                return False
            
            with open(test_file, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.ocr_service_url}/ocr", files=files)
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"✅ Direct OCR test successful: {result.get('text', '')[:50]}...")
                return True
            else:
                self.log(f"❌ Direct OCR failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Direct OCR test error: {str(e)}", "ERROR")
            return False
    
    def test_api_integration(self):
        """Test full API integration"""
        try:
            # Create test image
            test_file = "test_api.jpg"
            if not self.create_test_receipt(test_file):
                return False
            
            # Convert to base64
            with open(test_file, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Test API
            payload = {
                "imageDataUrl": f"data:image/jpeg;base64,{image_data}"
            }
            
            response = requests.post(self.api_endpoint, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.log(f"✅ API integration test successful: {len(result.get('data', {}).get('items', []))} items found")
                    return True
                else:
                    self.log(f"❌ API integration failed: {result.get('error', 'Unknown error')}", "ERROR")
                    return False
            else:
                self.log(f"❌ API integration HTTP error: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ API integration test error: {str(e)}", "ERROR")
            return False
    
    def restart_service(self, service_name):
        """Attempt to restart a service"""
        try:
            if service_name == "ocr":
                # Restart OCR service
                subprocess.run(["pkill", "-f", "app.py"], shell=True, capture_output=True)
                time.sleep(2)
                subprocess.Popen(["python", "ocr-service/app.py"], 
                               cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.log("🔄 Restarted OCR service")
                time.sleep(5)
                
            elif service_name == "nextjs":
                # Note: Next.js is managed by npm run dev, can't easily restart from here
                self.log("⚠️ Next.js restart requires manual intervention")
                
        except Exception as e:
            self.log(f"❌ Error restarting {service_name}: {str(e)}", "ERROR")
    
    def auto_fix_issues(self):
        """Attempt to automatically fix detected issues"""
        self.log("🔍 Running auto-fix checks...")
        
        # Check OCR service
        try:
            response = requests.get(f"{self.ocr_service_url}/health", timeout=3)
            if response.status_code != 200:
                self.log("⚠️ OCR service health check failed, attempting restart")
                self.restart_service("ocr")
        except:
            self.log("⚠️ OCR service not reachable, attempting restart")
            self.restart_service("ocr")
    
    def continuous_test(self):
        """Main continuous testing loop"""
        self.log("🚀 Starting headless OCR testing system")
        
        test_cycle = 0
        while self.is_running:
            test_cycle += 1
            self.log(f"📊 Test Cycle #{test_cycle}")
            
            # Check services
            services_ok = self.check_services()
            
            if services_ok:
                # Run tests
                direct_test = self.test_ocr_direct()
                api_test = self.test_api_integration()
                
                if direct_test and api_test:
                    self.log("✅ All tests passed")
                else:
                    self.log("⚠️ Some tests failed, attempting auto-fix")
                    self.auto_fix_issues()
            else:
                self.log("⚠️ Services not ready, attempting auto-fix")
                self.auto_fix_issues()
            
            # Wait before next cycle
            time.sleep(30)
    
    def stop(self):
        """Stop the testing system"""
        self.is_running = False
        self.log("🛑 Stopping headless OCR testing system")

if __name__ == "__main__":
    tester = HeadlessOCRTester()
    try:
        tester.continuous_test()
    except KeyboardInterrupt:
        tester.stop()