"""
Test script to verify that the ocr_engine field is properly set in all OCR results.
This tests the fix for the 'ocr_engine' key error.
"""

import requests
import json
import io
from pathlib import Path
from PIL import Image

def test_ocr_engine_field():
    """Test that all OCR responses include the ocr_engine field"""
    
    # Use an existing test image
    test_image_path = Path("test_receipt.png")
    if not test_image_path.exists():
        print("❌ No test_receipt.png found in current directory")
        print("💡 Please ensure you have a test image file available")
        return False
    
    # Read the test image
    try:
        with open(test_image_path, 'rb') as f:
            img_bytes = f.read()
        print(f"✅ Using test image: {test_image_path} ({len(img_bytes)} bytes)")
    except Exception as e:
        print(f"❌ Failed to read test image: {e}")
        return False
    
    url = "http://localhost:8000/ocr"
    
    try:
        print("🧪 Testing OCR API endpoint...")
        print(f"URL: {url}")
        
        # Test with file upload (the correct API format)
        files = {
            'file': ('test.png', io.BytesIO(img_bytes), 'image/png')
        }
        
        response = requests.post(url, files=files, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response received successfully")
            print(f"📋 Response keys: {list(result.keys())}")
            
            # Check if ocr_engine field is present
            if 'ocr_engine' in result:
                print(f"✅ 'ocr_engine' field present: {result['ocr_engine']}")
                print("🎉 Fix verified: ocr_engine field is now included!")
                
                # Show more details about the response structure
                print(f"\n📊 Full response structure:")
                for key, value in result.items():
                    if isinstance(value, dict):
                        print(f"  {key}: {type(value)} with keys {list(value.keys())}")
                    elif isinstance(value, list):
                        print(f"  {key}: {type(value)} with {len(value)} items")
                    else:
                        print(f"  {key}: {type(value)} = {value}")
                
                return True
            else:
                print(f"❌ 'ocr_engine' field missing from response")
                print(f"🔍 Full response: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"❌ API returned error status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the OCR service running?")
        print("💡 Start the service with: python ocr-service/app.py")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("OCR ENGINE FIELD TEST")
    print("=" * 60)
    print("Testing fix for 'ocr_engine' key error...")
    print()
    
    success = test_ocr_engine_field()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS: ocr_engine field fix verified!")
    else:
        print("❌ FAILED: ocr_engine field still missing")
    print("=" * 60)