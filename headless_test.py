#!/usr/bin/env python3
"""
Headless OCR Testing - Quick Test
Tests OCR service with file upload to identify and fix issues
"""

import requests
import json
import time
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """Create a simple test receipt image"""
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    # Simple receipt content
    content = [
        "RECEIPT",
        "Store: Test Store",
        "Date: 12/15/2024",
        "",
        "Apples: $2.99",
        "Bread: $1.49",
        "Milk: $3.29",
        "",
        "Total: $7.77"
    ]
    
    y = 20
    for line in content:
        draw.text((20, y), line, fill='black', font=font)
        y += 20
    
    img.save("test_receipt.png")
    return "test_receipt.png"

def test_ocr_service():
    """Test the OCR service with file upload"""
    print("Testing OCR service in headless mode...")
    
    # Create test image
    image_path = create_test_image()
    print(f"Created test image: {image_path}")
    
    # Test health endpoint
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Health check: {health_response.status_code} - {health_response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test OCR endpoint
    try:
        with open(image_path, 'rb') as f:
            files = {'file': ('receipt.png', f, 'image/png')}
            response = requests.post("http://localhost:8000/ocr", files=files, timeout=30)
        
        print(f"OCR Response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("OCR Result:")
            print(json.dumps(result, indent=2))
            
            # Basic validation
            if 'text' in result and 'items' in result:
                print("✅ OCR test successful!")
                return True
            else:
                print("❌ Invalid response structure")
                return False
        else:
            print(f"❌ OCR failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OCR test error: {e}")
        return False

def run_continuous_tests():
    """Run tests in a loop until stable"""
    print("Starting continuous headless OCR testing...")
    
    success_count = 0
    failure_count = 0
    
    for cycle in range(20):  # Max 20 cycles
        print(f"\n--- Test Cycle {cycle + 1} ---")
        
        if test_ocr_service():
            success_count += 1
            failure_count = 0
            print(f"✅ Cycle {cycle + 1} passed")
            
            # If we get 3 consecutive successes, stop
            if success_count >= 3:
                print("🎉 Service is stable!")
                break
        else:
            failure_count += 1
            success_count = 0
            print(f"❌ Cycle {cycle + 1} failed")
            
            # If too many failures, stop
            if failure_count >= 5:
                print("🔥 Too many failures - stopping")
                break
        
        time.sleep(2)  # Wait between tests
    
    print(f"\nFinal Results:")
    print(f"Successful cycles: {success_count}")
    print(f"Failed cycles: {failure_count}")

if __name__ == "__main__":
    run_continuous_tests()