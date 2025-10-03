"""
Test script to debug why blacklisting isn't working for problematic terms.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ocr-service'))

from intelligent_receipt_parser import IntelligentReceiptParser

def test_blacklisting():
    parser = IntelligentReceiptParser()
    
    # Test the problematic terms from the logs
    test_lines = [
        "Subtotal ($39.20)",
        "Loyalty ($15.00)", 
        "Net @ /Ko ($5.99)",
        "I 1.928Kq ($2.99)",
        "Subtotal",
        "Loyalty",
        "subtotal",
        "loyalty",
        "SUBTOTAL",
        "LOYALTY",
        "M SUBTOTAL $24.20",
        "L SUBTOTAL ($24.20)",
    ]
    
    print("=" * 60)
    print("BLACKLIST TESTING")
    print("=" * 60)
    
    for line in test_lines:
        is_blacklisted = parser.is_blacklisted(line)
        print(f"'{line}' -> {'❌ BLACKLISTED' if is_blacklisted else '✅ NOT blacklisted'}")
    
    print("\n" + "=" * 60)
    print("TESTING WITH ITEM NAME EXTRACTION")
    print("=" * 60)
    
    # Test how item names are extracted and if they would be blacklisted
    for line in test_lines:
        if '$' in line and any(char.isdigit() for char in line):
            try:
                quantity, price, item_name_raw = parser.extract_price_and_quantity(line)
                item_name = parser.clean_item_name(item_name_raw)
                is_item_blacklisted = parser.is_blacklisted(item_name)
                is_unit_descriptor = parser.is_unit_descriptor_only(item_name)
                is_likely_food = parser.is_likely_food_item(item_name)
                
                print(f"Line: '{line}'")
                print(f"  -> Raw name: '{item_name_raw}'")
                print(f"  -> Clean name: '{item_name}'")
                print(f"  -> Blacklisted: {'❌ YES' if is_item_blacklisted else '✅ NO'}")
                print(f"  -> Unit descriptor: {'❌ YES' if is_unit_descriptor else '✅ NO'}")
                print(f"  -> Likely food: {'✅ YES' if is_likely_food else '❌ NO'}")
                print()
            except Exception as e:
                print(f"Line: '{line}' -> ERROR: {e}")
        else:
            print(f"Line: '{line}' -> No price found")
    
    print("=" * 60)

if __name__ == "__main__":
    test_blacklisting()