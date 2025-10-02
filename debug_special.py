import sys
import re
sys.path.insert(0, 'ocr-service')
from intelligent_receipt_parser import receipt_parser

test_line = "SPECIAL 2.50"

print("Testing line:", test_line)

# Extract item name only
text = test_line
item_name_only = re.sub(r'\s*\$?\d+\.\d{2}\s*$', '', text).strip().lower()
print(f"Item name only (after removing price): '{item_name_only}'")

# Check if it equals 'special'
print(f"Does '{item_name_only}' == 'special'? {item_name_only == 'special'}")

# Now test the full blacklist function
print(f"Is blacklisted? {receipt_parser.is_blacklisted(test_line)}")

# Check if has food word
text_lower = test_line.lower()
has_food = any(food in text_lower for food in receipt_parser.FOOD_CATEGORIES)
print(f"Has food word? {has_food}")
