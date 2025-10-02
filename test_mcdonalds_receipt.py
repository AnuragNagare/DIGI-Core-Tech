"""
Test with the McDonald's receipt the user provided
Expected items:
- Sausage Egg McMuffin (appears 2x, lines 2-3)
- 2 Burritos EVM
- S Coffee
- 2 Hash Browns  
- M Iced Coffee

Should NOT extract:
- Buy One, Get One (promotion)
- ADD Cream (modifier)
- NO Liquid Sugar (modifier)
"""

import sys
sys.path.insert(0, 'ocr-service')

from intelligent_receipt_parser import receipt_parser

# Simulated OCR text from McDonald's receipt
MCDONALDS_RECEIPT = """
485

KS# 4                           08:13:56 AM
QTY ITEM                        TOTAL
  1 Buy One, Get One             3.99
    1 Sausage Egg McMuffin
    1 Sausage Egg McMuffin
  1 2 Burritos EVM                6.99
    1 S Coffee
      ADD Cream
  1 2 Hash Browns                 0.80
  1 M Iced Coffee                  1.40
      NO Liquid Sugar

Subtotal                         13.18
GST                               0.66
Take-Out Total                   13.84
CREDIT CARD                      13.84
Change                            0.00
"""

print("Testing McDonald's Receipt:")
print("="*60)

items = receipt_parser.parse_receipt_items(MCDONALDS_RECEIPT)

print(f"\nExtracted {len(items)} items:\n")
for i, item in enumerate(items, 1):
    print(f"{i}. {item['name']}")
    print(f"   Price: ${item['price']:.2f}")
    print(f"   Quantity: {item['quantity']}")
    print()

# Expected items
expected = [
    "Sausage Egg McMuffin",
    "Burritos Evm",
    "S Coffee",
    "Hash Browns",
    "M Iced Coffee"
]

# Should NOT be extracted
should_not_extract = [
    "Buy One",
    "Get One", 
    "ADD Cream",
    "NO Liquid Sugar"
]

print("\n" + "="*60)
print("VALIDATION:")
print("="*60)

extracted_names = [item['name'] for item in items]

# Check missing
missing = []
for exp in expected:
    found = any(exp.lower() in name.lower() for name in extracted_names)
    if not found:
        missing.append(exp)

# Check false positives
false_positives = []
for item_name in extracted_names:
    for bad in should_not_extract:
        if bad.lower() in item_name.lower():
            false_positives.append(item_name)
            break

if not missing and not false_positives:
    print("✅ SUCCESS! All items extracted correctly!")
else:
    if missing:
        print(f"\n❌ Missing items: {missing}")
    if false_positives:
        print(f"\n❌ False positives: {false_positives}")
