import sys
sys.path.insert(0, 'ocr-service')
from intelligent_receipt_parser import IntelligentReceiptParser
import re

test_line = "Pizza Large        1    430.0    430.0"
print(f"Line: '{test_line}'")
print(f"Has \\t: {('\t' in test_line)}")
print(f"Has 2+ spaces: {('  ' in test_line)}")

# Test the split
parts = re.split(r'\s{2,}|\t+', test_line.strip())
print(f"Split result: {parts}")

p = IntelligentReceiptParser()
qty, price, name = p.extract_price_and_quantity(test_line)
print(f"\nExtracted:")
print(f"  Quantity: {qty}")
print(f"  Price: {price}")
print(f"  Name: '{name}'")
