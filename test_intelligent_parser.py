"""
Quick test of intelligent receipt parser
Tests with sample receipt text to verify it extracts only food items
"""

import sys
sys.path.insert(0, 'ocr-service')

from intelligent_receipt_parser import receipt_parser

# Sample receipt text (simulating what OCR might extract)
SAMPLE_RECEIPT = """
COLES SUPERMARKET
123 MAIN ST
MELBOURNE VIC 3000

TAX INVOICE
DATE: 15/05/2024
TIME: 14:30:25

ZUCHINNI GREEN 2.98
BANANA CAVENDISH 5.98
0.442kg NET @ $2.99/kg
POTATOES BRUSHED 3.00
BROCCOLI 3.98
SPECIAL 2.50
BRUSSEL SPROUTS 4.98
0.322kg NET @ $4.99/kg
GRAPES GREEN 8.99
PEAS SNOW 6.50
TOMATOES GRAPE 5.49
LETTUCE ICEBERG 2.50

SUBTOTAL $47.88
GST $4.35
TOTAL $52.23

LOYALTY POINTS: 52
CHANGE $25.80

THANK YOU FOR SHOPPING
VISIT US AT COLES.COM.AU
"""

def test_intelligent_parser():
    print("=" * 60)
    print("TESTING INTELLIGENT RECEIPT PARSER")
    print("=" * 60)
    print("\nRAW RECEIPT TEXT:")
    print("-" * 60)
    print(SAMPLE_RECEIPT)
    print("-" * 60)
    
    # Parse receipt
    items = receipt_parser.parse_receipt_items(SAMPLE_RECEIPT)
    
    print(f"\n✅ EXTRACTED {len(items)} FOOD ITEMS:")
    print("=" * 60)
    
    for i, item in enumerate(items, 1):
        print(f"\n{i}. {item['name']}")
        print(f"   Quantity: {item['quantity']:.3f}")
        print(f"   Price: ${item['price']:.2f}")
        print(f"   Original: {item['original_line']}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION:")
    print("-" * 60)
    
    # Expected items (actual food products)
    expected_foods = [
        'ZUCHINNI GREEN',
        'BANANA CAVENDISH', 
        'POTATOES BRUSHED',
        'BROCCOLI',
        'BRUSSEL SPROUTS',
        'GRAPES GREEN',
        'PEAS SNOW',
        'TOMATOES GRAPE',
        'LETTUCE ICEBERG'
    ]
    
    # Items that should be filtered out
    excluded_items = [
        'SPECIAL',
        'NET',
        'SUBTOTAL',
        'TOTAL',
        'GST',
        'LOYALTY',
        'CHANGE',
        'THANK YOU',
        'DATE',
        'TIME'
    ]
    
    extracted_names = [item['name'].upper() for item in items]
    
    print(f"\n✅ Expected to extract: {len(expected_foods)} items")
    print(f"✅ Actually extracted: {len(items)} items")
    
    # Check if we got all the expected items
    missing = []
    for food in expected_foods:
        if not any(food.upper() in name for name in extracted_names):
            missing.append(food)
    
    if missing:
        print(f"\n❌ MISSING ITEMS: {missing}")
    else:
        print(f"\n✅ ALL EXPECTED ITEMS EXTRACTED!")
    
    # Check if we accidentally included excluded items
    false_positives = []
    for item in items:
        name = item['name'].upper()
        for excluded in excluded_items:
            if excluded in name:
                false_positives.append(item['name'])
                break
    
    if false_positives:
        print(f"\n❌ INCORRECTLY EXTRACTED: {false_positives}")
    else:
        print(f"✅ NO UNWANTED ITEMS EXTRACTED!")
    
    # Calculate accuracy
    correct = len(items) - len(false_positives)
    accuracy = (correct / len(expected_foods) * 100) if expected_foods else 0
    
    print(f"\n{'=' * 60}")
    print(f"ACCURACY: {accuracy:.1f}%")
    print(f"{'=' * 60}")
    
    if accuracy >= 90 and not false_positives:
        print("\n🎉 SUCCESS! Parser is working correctly!")
        return True
    else:
        print("\n⚠️  NEEDS IMPROVEMENT")
        return False

if __name__ == "__main__":
    test_intelligent_parser()
