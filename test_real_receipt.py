"""
Test the enhanced OCR service with a real receipt image.
This will verify that:
1. "Buy One, Get One" promotional text is FILTERED OUT
2. Line references ("Line 1", "Line 4", "Line 8") are REMOVED from names
3. Item codes and numbers in names are REMOVED
4. Non-food items ("Take-Out Total", "Change") are FILTERED OUT
5. Real food items are EXTRACTED CLEAN
"""

import sys
import os

# Add the ocr-service directory to Python path
sys.path.append(os.path.join(os.getcwd(), 'ocr-service'))

from intelligent_receipt_parser import IntelligentReceiptParser

# Simulate the OCR text from your actual receipt image
real_receipt_ocr_text = """485

KS# 4                              08:13:56 AM
QTY ITEM                           TOTAL
  1 Buy One, Get One Line 1        3.99
    1 Sausage Egg McMuffin Line 2
    1 Sausage Egg McMuffin Line 3
1 2 Burritos EVM Line 4            6.99
    1 S Coffee Line 5
      ADD Cream Line 6
    1 2 Hash Browns Line 7         0.80
1 M Iced Coffee Line 8             1.40
      NO Liquid Sugar Line 9

Subtotal                           13.18
GST                                0.66
Take-Out Total                     13.84
CREDIT CARD                        13.84
Change                             0.00

    Take our online survey,
    Receive a free coupon"""

print("=" * 70)
print("TESTING ENHANCED OCR WITH YOUR ACTUAL RECEIPT")
print("=" * 70)
print()

# Initialize parser
parser = IntelligentReceiptParser()

# Parse the receipt
items = parser.parse_receipt_items(real_receipt_ocr_text)

print(f"EXTRACTED ITEMS: {len(items)}")
print("-" * 50)

if len(items) == 0:
    print("⚠️  WARNING: No items extracted!")
    print()
    print("Expected items that should be extracted:")
    print("  - Sausage Egg McMuffin (should appear twice)")
    print("  - Burritos")
    print("  - S Coffee")
    print("  - Hash Browns")
    print("  - M Iced Coffee")
    print()
else:
    for i, item in enumerate(items, 1):
        print(f"{i}. {item['name']}")
        print(f"   Price: ${item['price']:.2f}")
        print(f"   Quantity: {item['quantity']}")
        print()

print("=" * 70)
print("VALIDATION CHECKS:")
print("=" * 70)

# Check that bad items are NOT in the results
bad_items_found = []
for item in items:
    name_lower = item['name'].lower()
    
    # Check for promotional text
    if 'buy one' in name_lower or 'get one' in name_lower:
        bad_items_found.append(f"❌ Found promotional text: {item['name']}")
    
    # Check for line references
    if 'line' in name_lower:
        bad_items_found.append(f"❌ Found line reference: {item['name']}")
    
    # Check for non-food items
    if 'take-out' in name_lower or 'takeout' in name_lower:
        bad_items_found.append(f"❌ Found non-food item: {item['name']}")
    
    if 'change' in name_lower and len(item['name']) < 20:  # "Change" alone
        bad_items_found.append(f"❌ Found non-food item: {item['name']}")
    
    # Check for item codes (numbers at start)
    if item['name'] and item['name'][0].isdigit():
        bad_items_found.append(f"❌ Found item code in name: {item['name']}")

if bad_items_found:
    print("PROBLEMS FOUND:")
    for problem in bad_items_found:
        print(f"  {problem}")
    print()
else:
    print("✅ All validation checks PASSED!")
    print("   - No promotional text in item names")
    print("   - No line references in item names")
    print("   - No non-food items extracted")
    print("   - No item codes in names")
    print()

# Expected results
print("EXPECTED CLEAN ITEMS:")
print("  1. Sausage Egg McMuffin (x2)")
print("  2. Burritos")
print("  3. S Coffee (or Coffee)")
print("  4. Hash Browns")
print("  5. M Iced Coffee")
print()

# Check if we got the expected items
expected_keywords = ['sausage', 'burrito', 'coffee', 'hash', 'brown']
found_keywords = []

for item in items:
    name_lower = item['name'].lower()
    for keyword in expected_keywords:
        if keyword in name_lower and keyword not in found_keywords:
            found_keywords.append(keyword)

print(f"Found {len(found_keywords)}/{len(expected_keywords)} expected food keywords")
print()

if len(found_keywords) >= 3:  # At least 3 out of 5 types of food
    print("✅ SUCCESS: System is extracting real food items!")
else:
    print("⚠️  WARNING: Not enough food items found. May need further tuning.")
