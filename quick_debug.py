"""Quick test with DEBUG logging"""
import sys
import logging
sys.path.insert(0, 'ocr-service')

logging.basicConfig(level=logging.DEBUG)

from intelligent_receipt_parser import receipt_parser

MCDONALDS_RECEIPT = """
485

KS# 4                           08:13:56 AM
QTY ITEM                        TOTAL
  1 Buy One, Get One             3.99
    1 Sausage Egg McMuffin
    1 Sausage Egg McMuffin
  1 2 Burritos EVM                6.99
    1 S Coffee
"""

items = receipt_parser.parse_receipt_items(MCDONALDS_RECEIPT)

print(f"\nExtracted {len(items)} items")
