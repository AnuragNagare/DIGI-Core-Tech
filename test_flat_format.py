import sys
import os
sys.path.insert(0, 'ocr-service')

from intelligent_receipt_parser import IntelligentReceiptParser

# Test flat format
text = """Invoice No. 10                           Date: May 11, 2019

Item Name         Qty    Rate    Amount
Pizza Large        1    430.0    430.0
Pasta             2    220.0    440.0
Pizza Makhaani - Full  1    190.0    190.0
                           Total:  1,060.0"""

p = IntelligentReceiptParser()
result = p.parse_receipt(text)

print(f"Items found: {len(result['items'])}")
print(f"Total: ${result['total']:.2f}")
print(f"Date: {result['date']}")

for item in result['items']:
    print(f"  {item['name']} x{item['quantity']} = ${item['price']:.2f}")
