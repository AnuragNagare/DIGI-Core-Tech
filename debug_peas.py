import sys
sys.path.insert(0, 'ocr-service')
from intelligent_receipt_parser import receipt_parser

# Test specific line
test_line = "PEAS SNOW 6.50"

print("Testing line:", test_line)
print("\\n1. Is blacklisted?", receipt_parser.is_blacklisted(test_line))

# Detailed blacklist check
text_lower = test_line.lower()
print(f"\\nChecking '{text_lower}' against blacklist:")
for keyword in sorted(receipt_parser.BLACKLIST_KEYWORDS):
    if keyword in text_lower:
        print(f"  Found keyword '{keyword}' in line")
        has_food = any(food in text_lower for food in receipt_parser.FOOD_CATEGORIES)
        print(f"     Has food word: {has_food}")
