import sys
import os
import logging
sys.path.insert(0, 'ocr-service')

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

from intelligent_receipt_parser import IntelligentReceiptParser

# Test single line
p = IntelligentReceiptParser()

test_line = "Pizza Large        1    430.0    430.0"
print(f"Testing line: '{test_line}'")
print(f"Has multiple spaces: {('  ' in test_line)}")

qty, price, name = p.extract_price_and_quantity(test_line)
print(f"Extracted: qty={qty}, price={price}, name='{name}'")

clean_name = p.clean_item_name(name)
print(f"Cleaned name: '{clean_name}'")

is_blacklisted = p.is_blacklisted(test_line)
print(f"Is blacklisted: {is_blacklisted}")

is_food = p.is_likely_food_item(clean_name)
print(f"Is food item: {is_food}")
