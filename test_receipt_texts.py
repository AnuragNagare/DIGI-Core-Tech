"""Validate parser across multiple textual receipt samples"""
import sys
sys.path.insert(0, 'ocr-service')

from intelligent_receipt_parser import receipt_parser

SAMPLES = {
    "walmart": open('test-receipt-1.jpg', 'r', encoding='utf-8').read(),
    "target": open('test-receipt-2.jpg', 'r', encoding='utf-8').read(),
    "restaurant": open('test-receipt-3.jpg', 'r', encoding='utf-8').read(),
}

for name, text in SAMPLES.items():
    print(f"\n=== Testing {name} receipt ===")
    items = receipt_parser.parse_receipt_items(text)
    for item in items:
        print(f"- {item['name']} (${item['price']}) [qty {item['quantity']}]")
    if not items:
        print("(no items extracted)")
