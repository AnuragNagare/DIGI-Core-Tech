"""Test hierarchical parsing with detailed logging"""
import sys
import logging
sys.path.append('ocr-service')

# Enable DEBUG logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from intelligent_receipt_parser import IntelligentReceiptParser

# Exact lines from McDonald's receipt
receipt_text = """KS# 4                           08:13:56 AM
QTY ITEM                                     TOTAL
  1 Buy One, Get One             3.99
    1 Sausage Egg McMuffin
    1 Sausage Egg McMuffin
  1 2 Burritos EVM               6.99
    1 S Coffee
      ADD Cream
  1 2 Hash Browns                 0.80
1 M Iced Coffee                  1.40
    NO Liquid Sugar
Subtotal                         13.18
GST                               0.66
Take-Out Total                   13.84"""

parser = IntelligentReceiptParser()
result = parser.parse_receipt_items(receipt_text)

print("\n" + "="*60)
print("FINAL RESULTS:")
print("="*60)
for item in result:
    print(f"✅ {item['name']} - ${item['price']:.2f}")
