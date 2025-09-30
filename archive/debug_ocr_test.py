#!/usr/bin/env python3
"""
Debug OCR API testing to identify exact issues
"""

import requests
import json
import base64
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def create_test_receipt():
    """Create a simple test receipt"""
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
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
    
    img.save("debug_test.jpg", 'JPEG')
    return "debug_test.jpg"

def test_api_direct():
    """Test the API directly with detailed debugging"""
    print("🔍 Starting OCR API Debug Test")
    
    # Create test image
    test_file = create_test_receipt()
    print(f"✅ Created test image: {test_file}")
    
    # Convert to base64
    with open(test_file, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    payload = {
        "imageDataUrl": f"data:image/jpeg;base64,{image_data}"
    }
    
    print("📤 Testing API endpoint...")
    
    try:
        response = requests.post(
            "http://localhost:3000/api/ocr/receipt",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False

def test_ocr_service_direct():
    """Test OCR service directly"""
    print("🔍 Testing OCR Service Directly...")
    
    test_file = create_test_receipt()
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post("http://localhost:8000/ocr", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ OCR Service Response: {result}")
            return result.get('text', '')
        else:
            print(f"❌ OCR Service Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ OCR Service Exception: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 OCR Debug Testing Started")
    
    # Test OCR service first
    ocr_text = test_ocr_service_direct()
    if ocr_text:
        print(f"📄 OCR Text: {ocr_text[:200]}...")
    
    # Test API
    success = test_api_direct()
    
    if success:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Tests failed - check logs above")