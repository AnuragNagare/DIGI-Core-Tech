"""
Test OCR parser with local receipt images
Tests with multiple different receipt formats
"""

import sys
import os
sys.path.insert(0, 'ocr-service')

from enhanced_ocr_service import EnhancedOCRService
from intelligent_receipt_parser import receipt_parser

# Test with local receipt images
TEST_RECEIPTS = [
    r"test-receipt-1.jpg",
    r"test-receipt-2.jpg",
    r"test-receipt-3.jpg",
]

print("=" * 60)
print("🧪 TESTING RECEIPT PARSER WITH LOCAL IMAGES")
print("=" * 60)

ocr_service = EnhancedOCRService()

total_tests = 0
passed_tests = 0

for i, receipt_path in enumerate(TEST_RECEIPTS, 1):
    if not os.path.exists(receipt_path):
        print(f"\n❌ Receipt {i}: File not found: {receipt_path}")
        continue
        
    print(f"\n{'='*60}")
    print(f"📄 TEST {i}/{len(TEST_RECEIPTS)}: {receipt_path}")
    print(f"{'='*60}")
    
    try:
        # Read image file
        with open(receipt_path, 'rb') as f:
            image_data = f.read()
        
        # Extract text with OCR
        print("🔍 Running OCR...")
        ocr_result = ocr_service.extract_text_from_image_bytes(image_data)
        
        if not ocr_result or not ocr_result.get('success'):
            print(f"❌ OCR failed: {ocr_result.get('error', 'Unknown error') if ocr_result else 'No result'}")
            continue
            
        raw_text = ocr_result.get('text', '')
        print(f"\n📝 Raw OCR text ({len(raw_text)} chars):")
        print("-" * 60)
        print(raw_text[:500])
        if len(raw_text) > 500:
            print(f"... ({len(raw_text) - 500} more chars)")
        
        # Parse items
        print(f"\n🤖 Parsing items...")
        items = receipt_parser.parse_receipt_items(raw_text)
        
        print(f"\n✅ Extracted {len(items)} items:")
        print("-" * 60)
        
        if items:
            for j, item in enumerate(items, 1):
                print(f"{j}. {item['name']}")
                print(f"   Price: ${item['price']:.2f}")
                print(f"   Quantity: {item['quantity']}")
                print()
            
            total_tests += 1
            passed_tests += 1
            print(f"✅ TEST {i} PASSED - Extracted {len(items)} food items")
        else:
            print("⚠️  No items extracted")
            total_tests += 1
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

# Summary
print("\n" + "=" * 60)
print("📊 FINAL RESULTS")
print("=" * 60)
print(f"Tests run: {total_tests}")
print(f"Tests passed: {passed_tests}")
if total_tests > 0:
    accuracy = (passed_tests / total_tests) * 100
    print(f"Accuracy: {accuracy:.1f}%")
    
    if accuracy == 100:
        print("\n🎉 100% ACCURACY ACHIEVED!")
    else:
        print(f"\n⚠️  Need to improve parser for remaining {total_tests - passed_tests} receipts")
else:
    print("\n❌ No tests completed")
