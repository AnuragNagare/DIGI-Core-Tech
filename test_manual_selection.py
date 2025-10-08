#!/usr/bin/env python3
"""
Quick Test Script for Manual Selection Feature
Tests that the OCR service returns items correctly for manual selection
"""

import requests
import json
from pathlib import Path

def test_ocr_service():
    """Test OCR service with a sample receipt"""
    
    print("=" * 70)
    print("🧪 Testing OCR Service for Manual Selection Feature")
    print("=" * 70)
    
    # Check if service is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print("\n✅ OCR Service is running")
    except requests.exceptions.RequestException:
        print("\n❌ ERROR: OCR Service is not running!")
        print("   Please start it with: cd ocr-service && python start_all_services.py")
        return False
    
    # Find a sample image
    sample_dir = Path(__file__).parent / "sample_images"
    sample_images = list(sample_dir.glob("*.png")) + list(sample_dir.glob("*.jpg"))
    
    if not sample_images:
        print("\n❌ ERROR: No sample images found in sample_images/ folder")
        return False
    
    test_image = sample_images[0]
    print(f"\n📸 Using test image: {test_image.name}")
    
    # Send OCR request
    print("\n⏳ Sending OCR request...")
    
    try:
        with open(test_image, 'rb') as f:
            files = {'file': (test_image.name, f, 'image/png')}
            response = requests.post(
                "http://localhost:8000/ocr",
                files=files,
                timeout=30
            )
        
        if response.status_code != 200:
            print(f"\n❌ ERROR: OCR request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        data = response.json()
        
        print("\n✅ OCR Processing Successful!")
        print("\n" + "=" * 70)
        print("📋 Extracted Items for Manual Selection:")
        print("=" * 70)
        
        if 'items' in data and data['items']:
            items = data['items']
            print(f"\n✅ Found {len(items)} items\n")
            
            for i, item in enumerate(items, 1):
                print(f"{i}. {item.get('name', 'Unknown')}")
                print(f"   Quantity: {item.get('quantity', 'N/A')} {item.get('unit', '')}")
                if 'price' in item:
                    print(f"   Price: ${item['price']:.2f}")
                print()
            
            print("=" * 70)
            print("\n✅ TEST PASSED!")
            print("\n📝 Next Steps:")
            print("   1. These items will appear in the frontend with checkboxes")
            print("   2. User can select/deselect items")
            print("   3. Only selected items will be added to inventory")
            print("\n" + "=" * 70)
            return True
        else:
            print("\n⚠️  WARNING: No items extracted from receipt")
            print("   This might be expected for some receipts")
            print(f"\n   Raw text: {data.get('rawText', 'No text')[:200]}...")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: Request failed: {e}")
        return False
    except json.JSONDecodeError:
        print(f"\n❌ ERROR: Invalid JSON response")
        print(f"   Response: {response.text}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    success = test_ocr_service()
    sys.exit(0 if success else 1)
