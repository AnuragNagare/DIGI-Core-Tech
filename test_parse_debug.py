import sys
import os
import logging
sys.path.insert(0, 'ocr-service')

# Capture all logs
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

from intelligent_receipt_parser import IntelligentReceiptParser

text = """Item Name         Qty    Rate    Amount
Pizza Large        1    430.0    430.0
Pasta             2    220.0    440.0"""

p = IntelligentReceiptParser()
result = p.parse_receipt_items(text)

print(f"\n==== RESULT ====")
print(f"Items: {len(result)}")
for item in result:
    print(f"  {item['name']} x{item['quantity']} = ${item['price']:.2f}")
