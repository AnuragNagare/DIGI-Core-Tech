"""
Debug specifically why "Aeuismod" is being blacklisted
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ocr-service'))

from intelligent_receipt_parser import IntelligentReceiptParser

def debug_aeuismod():
    parser = IntelligentReceiptParser()
    
    test_line = "5: 1095 Aeuismod                    $10.00"
    
    print(f"Testing line: '{test_line}'")
    print()
    
    # Test full line blacklisting
    full_blacklisted = parser.is_blacklisted(test_line)
    print(f"Full line blacklisted: {'❌ YES' if full_blacklisted else '✅ NO'}")
    
    # Extract item name
    quantity, price, item_name_raw = parser.extract_price_and_quantity(test_line)
    item_name = parser.clean_item_name(item_name_raw)
    
    print(f"Raw name: '{item_name_raw}'")
    print(f"Clean name: '{item_name}'")
    
    # Test extracted name
    name_blacklisted = parser.is_blacklisted(item_name)
    is_unit_descriptor = parser.is_unit_descriptor_only(item_name)
    is_likely_food = parser.is_likely_food_item(item_name)
    
    print(f"Name blacklisted: {'❌ YES' if name_blacklisted else '✅ NO'}")
    print(f"Unit descriptor: {'❌ YES' if is_unit_descriptor else '✅ NO'}")
    print(f"Likely food: {'✅ YES' if is_likely_food else '❌ NO'}")
    
    # Test individual words
    print("\nTesting individual components:")
    for word in test_line.split():
        word_blacklisted = parser.is_blacklisted(word)
        print(f"  '{word}': {'❌ BLACKLISTED' if word_blacklisted else '✅ OK'}")

if __name__ == "__main__":
    debug_aeuismod()