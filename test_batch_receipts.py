"""
Batch Receipt Testing Script
Processes all receipt images in work/test_receipts/ through OCR and parser
"""

import os
import sys
import json
from pathlib import Path
import base64
import requests
from PIL import Image

# Add ocr-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ocr-service'))

from intelligent_receipt_parser import IntelligentReceiptParser

def process_receipt_with_ocr(image_path, ocr_service_url="http://localhost:5000"):
    """Process receipt through OCR service and parser"""
    try:
        # Read image
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Call OCR service
        files = {'image': (os.path.basename(image_path), image_data, 'image/jpeg')}
        response = requests.post(f"{ocr_service_url}/process-receipt", files=files, timeout=30)
        
        if response.status_code != 200:
            return None, f"OCR service error: {response.status_code}"
        
        ocr_result = response.json()
        
        # Parse the OCR text
        parser = IntelligentReceiptParser()
        parsed = parser.parse_receipt(ocr_result.get('text', ''))
        
        return {
            'ocr_text': ocr_result.get('text', ''),
            'parsed': parsed,
            'ocr_raw': ocr_result
        }, None
    
    except Exception as e:
        return None, str(e)

def process_receipt_direct(image_path):
    """Process receipt using direct OCR (fallback if service is down)"""
    try:
        import pytesseract
        from PIL import Image
        
        # Read and OCR the image
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        
        # Parse
        parser = IntelligentReceiptParser()
        parsed = parser.parse_receipt(text)
        
        return {
            'ocr_text': text,
            'parsed': parsed
        }, None
    
    except Exception as e:
        return None, str(e)

def main():
    test_dir = Path("work/test_receipts")
    
    if not test_dir.exists():
        print(f"❌ Directory {test_dir} does not exist")
        return
    
    # Find all image files
    image_files = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png")) + list(test_dir.glob("*.jpeg"))
    
    if not image_files:
        print(f"❌ No image files found in {test_dir}")
        print("Please save the receipt images to work/test_receipts/ folder")
        return
    
    print(f"🔍 Found {len(image_files)} receipt images")
    print("=" * 80)
    
    results = []
    failures = []
    
    for idx, img_path in enumerate(sorted(image_files), 1):
        print(f"\n📋 [{idx}/{len(image_files)}] Processing: {img_path.name}")
        print("-" * 80)
        
        # Try OCR service first, fall back to direct
        result, error = process_receipt_with_ocr(str(img_path))
        
        if error and "Connection" in error:
            print("⚠️  OCR service not running, using direct Tesseract...")
            result, error = process_receipt_direct(str(img_path))
        
        if error:
            print(f"❌ Error: {error}")
            failures.append({
                'file': img_path.name,
                'error': error
            })
            continue
        
        # Display results
        parsed = result['parsed']
        print(f"\n📄 OCR Text Preview (first 500 chars):")
        print(result['ocr_text'][:500])
        print("\n" + "=" * 40)
        
        print(f"\n✅ Parsed Results:")
        print(f"   Items found: {len(parsed.get('items', []))}")
        print(f"   Total: ${parsed.get('total', 0):.2f}")
        print(f"   Date: {parsed.get('date', 'Not found')}")
        print(f"   Merchant: {parsed.get('merchant_name', 'Not found')}")
        
        print(f"\n📦 Items:")
        for item in parsed.get('items', []):
            name = item.get('name', 'Unknown')
            qty = item.get('quantity', 1)
            price = item.get('price', 0)
            unit_price = item.get('unit_price', 0)
            
            qty_str = f"{qty}x" if qty > 1 else "  "
            unit_str = f" (@${unit_price:.2f})" if unit_price > 0 else ""
            print(f"   {qty_str} {name:40s} ${price:7.2f}{unit_str}")
        
        results.append({
            'file': img_path.name,
            'parsed': parsed,
            'ocr_text': result['ocr_text']
        })
        
        print("=" * 80)
    
    # Summary
    print(f"\n\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successful: {len(results)}/{len(image_files)}")
    print(f"❌ Failed: {len(failures)}/{len(image_files)}")
    
    if failures:
        print(f"\n❌ Failures:")
        for fail in failures:
            print(f"   - {fail['file']}: {fail['error']}")
    
    # Save detailed results
    output_file = "work/batch_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'results': results,
            'failures': failures,
            'summary': {
                'total': len(image_files),
                'successful': len(results),
                'failed': len(failures)
            }
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    main()
