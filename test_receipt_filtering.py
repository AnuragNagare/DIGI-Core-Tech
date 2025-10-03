"""
Test script to verify the actual OCR parser with problematic terms.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ocr-service'))

from intelligent_receipt_parser import IntelligentReceiptParser

def test_receipt_parsing():
    parser = IntelligentReceiptParser()
    
    # Create a test receipt with the problematic terms
    test_receipt = """
Lorem Shop
123 Main Street

1: 0275 Ut wisi enim                $2.99
2: 0758 Nibh euismod                $1.30
3: 2563 Mnhnonuy nibh               $6.99
4: 0164 Taliquam erat               $5.10
5: 1095 Aeuismod                    $10.00
6: 3556. Knonuy nib                 $4.99

Subtotal                            $39.20
Loyalty                             $15.00
M Subtotal                          $24.20

Net @ /Ko                           $5.99
I 1.928Kq                           $2.99

TOTAL                               $34.50
CASH                                $50.00
CHANGE                              $15.50
"""

    print("=" * 60)
    print("TESTING ACTUAL RECEIPT PARSING")
    print("=" * 60)
    
    items = parser.parse_receipt_items(test_receipt)
    
    print(f"\n📊 RESULTS: Extracted {len(items)} items")
    print("-" * 40)
    
    expected_items = [
        "Ut Wisi Enim",
        "Nibh Euismod", 
        "Mnhnonuy Nibh",
        "Taliquam Erat",
        "Aeuismod",
        "Knonuy Nib"
    ]
    
    unwanted_terms = [
        "Subtotal",
        "Loyalty", 
        "M Subtotal",
        "Net @ /Ko",
        "I 1.928Kq",
        "Total",
        "Cash",
        "Change"
    ]
    
    extracted_names = [item['name'] for item in items]
    
    print("✅ EXTRACTED ITEMS:")
    for item in items:
        print(f"  - {item['name']} (${item['price']:.2f})")
    
    print(f"\n🎯 EXPECTED ITEMS CHECK:")
    for expected in expected_items:
        found = any(expected.lower() in name.lower() for name in extracted_names)
        status = "✅ FOUND" if found else "❌ MISSING"
        print(f"  {expected}: {status}")
    
    print(f"\n🚫 UNWANTED TERMS CHECK:")
    for unwanted in unwanted_terms:
        found = any(unwanted.lower() in name.lower() for name in extracted_names)
        status = "❌ FOUND (BAD)" if found else "✅ FILTERED OUT"
        print(f"  {unwanted}: {status}")
    
    # Calculate success rate
    expected_found = sum(1 for expected in expected_items 
                        if any(expected.lower() in name.lower() for name in extracted_names))
    unwanted_found = sum(1 for unwanted in unwanted_terms 
                        if any(unwanted.lower() in name.lower() for name in extracted_names))
    
    success_rate = (expected_found / len(expected_items)) * 100 if expected_items else 100
    filter_rate = ((len(unwanted_terms) - unwanted_found) / len(unwanted_terms)) * 100 if unwanted_terms else 100
    
    print(f"\n📈 PERFORMANCE:")
    print(f"  Expected items found: {expected_found}/{len(expected_items)} ({success_rate:.1f}%)")
    print(f"  Unwanted terms filtered: {len(unwanted_terms) - unwanted_found}/{len(unwanted_terms)} ({filter_rate:.1f}%)")
    
    overall_success = success_rate >= 90 and filter_rate >= 90
    print(f"\n🎯 OVERALL: {'✅ SUCCESS' if overall_success else '❌ NEEDS IMPROVEMENT'}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_receipt_parsing()