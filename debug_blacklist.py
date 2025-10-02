"""Debug why 'M Iced Coffee' is being blacklisted"""
import sys
import logging
sys.path.append('ocr-service')

# Enable DEBUG logging
logging.basicConfig(level=logging.DEBUG)

from intelligent_receipt_parser import IntelligentReceiptParser

parser = IntelligentReceiptParser()

test_lines = [
    "1 Buy One, Get One             3.99",
    "  1 Sausage Egg McMuffin",
    "1 2 Burritos EVM               6.99",
    "  1 S Coffee",
    "1 2 Hash Browns                 0.80",
    "1 M Iced Coffee                  1.40",
]

print("Testing blacklist detection:")
print("=" * 60)
for line in test_lines:
    print(f"\nTesting: {line}")
    is_bl = parser.is_blacklisted(line)
    print(f"Result: Blacklisted = {is_bl}")
