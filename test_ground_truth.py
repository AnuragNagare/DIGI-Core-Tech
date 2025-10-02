"""
Ground Truth Test Cases for Receipt Parser
Based on the 15 receipt images provided
"""

import sys
import os

RECEIPT_GROUND_TRUTH = [
    {
        "name": "Family Restaurant",
        "text": """Vijay Nagar, Near by C21 Mall Indore Madhya
Pradesh
Mobile No.: 9879042519

Invoice No. 10                           Date: May 11, 2019

Item Name         Qty    Rate    Amount
Pizza Large        1    430.0    430.0
Pasta             2    220.0    440.0
Pizza Makhaani - Full  1    190.0    190.0
                           Additional Tax On:      0.0
                           Additional Take On:     0.0
                                        Total:  1,060.0

Thank You, Visit again!!!!""",
        "expected": {
            "merchant_name": "Family Restaurant",
            "date": "2019-05-11",
            "items": [
                {"name": "Pizza Large", "quantity": 1, "price": 430.0, "unit_price": 430.0},
                {"name": "Pasta", "quantity": 2, "price": 440.0, "unit_price": 220.0},
                {"name": "Pizza Makhaani - Full", "quantity": 1, "price": 190.0, "unit_price": 190.0}
            ],
            "total": 1060.0
        }
    },
    {
        "name": "Liquor Brand (GOLDEN DREAMS)",
        "text": """Liquor Brand
(GOLDEN DREAMS LIMITED)
Bandra (East)
Faridabad-121003
Ph. No. 0129-1111111115
E-MAIL: GIJ@RRRE@D
GSTIN: 06AEMDE111151Z6
Invoice Number:         INW01001759
Invoice Date:           20-May-18 22:55
Cash Memo

Item                  Qty    Rate    Total
Tandoori Chicken       1    300.00  300.00
Lasoon Tikka Dry       1    275.05  236.75
Kadhai Paneer          1    275.05  275.05
BIRYANI                1    93.93
Tandoori Roti all food 2    30.00   93.90
Rumali Roti            1    30.00   30.00
Tandoori Roti                30.00   31.60

Item Total                      1,036.00
Sub Total                       1,036.00
cess @ 3%                          52.90
SGST @ 2.5                         51.80
Total:                          1,183.60

Thanks For Visit..""",
        "expected": {
            "merchant_name": "Liquor Brand",
            "date": "2018-05-20",
            "items": [
                {"name": "Tandoori Chicken", "quantity": 1, "price": 300.00},
                {"name": "Lasoon Tikka Dry", "quantity": 1, "price": 236.75},
                {"name": "Kadhai Paneer", "quantity": 1, "price": 275.05},
                {"name": "BIRYANI", "quantity": 1, "price": 93.93},
                {"name": "Tandoori Roti all food", "quantity": 2, "price": 93.90},
                {"name": "Rumali Roti", "quantity": 1, "price": 30.00},
                {"name": "Tandoori Roti", "quantity": 1, "price": 31.60}
            ],
            "total": 1183.60,
            "subtotal": 1036.00
        }
    },
    {
        "name": "MVR Restaurant",
        "text": """MVR RESTAURANT
2424 Connecticut Ave NW
Washington DC 20008
+1-202-242-2424

23 June 2022                                    4:56 PM

Item                                          Amount ($)
Pizza                                              $103
Cookie                                              $12
Sandwich                                            $12
Subtotal                                          $127
Tea                                             $ 187.00
Total:                                          $ 187.00

Card                                            XXXXXXXX
Card Type                                          Visa

Invoice#                   432259523543""",
        "expected": {
            "merchant_name": "MVR Restaurant",
            "date": "2022-06-23",
            "items": [
                {"name": "Pizza", "quantity": 1, "price": 103.0},
                {"name": "Cookie", "quantity": 1, "price": 12.0},
                {"name": "Sandwich", "quantity": 1, "price": 12.0},
                {"name": "Tea", "quantity": 1, "price": 187.0}
            ],
            "total": 187.0,
            "subtotal": 127.0
        }
    },
    {
        "name": "Good Foods Market & Cafe",
        "text": """Good Foods
Market & Cafe
1602 South Ave
Missoula, MT 59801
(406) 541-3663

11/02/2006                   4:25 PM         040597

OSTBARDACRAKG               2  0.36 11 @ 1.20 A  2.40
ARENEWBUTTCRCH I            1  0.45 P @           0.45
                            0  0.36 11 @ 3.20 N  1.14
                            0  0.03 P @           0.03
OTCESISWEETC I              1  0.45 C @           0.45
SESTSWEETBRDCRNBLCNL.       1  0.50 P @           0.50
                            0  0.50 C @           0.50
                            0  0.00 11 @ N2.00 P 10.00
Tender Sub (CASH)                                10.00
TOTAL TENDERED                                   10.00
CHANGE                                            5.45
SUBTOTAL                                          4.55""",
        "expected": {
            "merchant_name": "Good Foods Market & Cafe",
            "date": "2006-11-02",
            "items": [
                {"name": "OSTBARDACRAKG", "quantity": 2, "price": 2.40},
                {"name": "ARENEWBUTTCRCH", "quantity": 1, "price": 0.45},
                {"name": "OTCESISWEETC", "quantity": 1, "price": 0.45},
                {"name": "SESTSWEETBRDCRNBLCNL", "quantity": 1, "price": 0.50}
            ],
            "total": 4.55,
            "subtotal": 4.55
        }
    },
    {
        "name": "McDonald's #485",
        "text": """485

KS# 4                                      08:13:56 AM
QTY ITEM                                         TOTAL
  1 Buy One, Get One                              3.99
    1 Sausage Egg McMuffin
    1 Sausage Egg McMuffin
  1 2 Burritos EVM                                6.99
    1 S Coffee
      ADD Cream
    1 2 Hash Browns                               0.80
  1 M Iced Coffee                                 1.40
      NO Liquid Sugar

Subtotal                                         13.18
GST                                               0.66
Take-Out Total                                   13.84
CREDIT CARD                                      13.84
Change                                            0.00

Take our online survey,
Receive a free coupon""",
        "expected": {
            "merchant_name": "McDonald's",
            "date": None,  # No date on receipt
            "items": [
                {"name": "Buy One, Get One", "quantity": 1, "price": 3.99},
                {"name": "Sausage Egg McMuffin", "quantity": 1, "price": 0.0},  # Part of BOGO
                {"name": "Sausage Egg McMuffin", "quantity": 1, "price": 0.0},  # Part of BOGO
                {"name": "2 Burritos EVM", "quantity": 1, "price": 6.99},
                {"name": "S Coffee", "quantity": 1, "price": 0.0},  # Part of combo
                {"name": "ADD Cream", "quantity": 1, "price": 0.0},  # Modifier
                {"name": "2 Hash Browns", "quantity": 1, "price": 0.80},
                {"name": "M Iced Coffee", "quantity": 1, "price": 1.40},
                {"name": "NO Liquid Sugar", "quantity": 1, "price": 0.0}  # Modifier
            ],
            "total": 13.84,
            "subtotal": 13.18
        }
    },
    {
        "name": "Grocery with Weights",
        "text": """DATE                     08/01/2016                    WED
**************************************************

ZUCHINNI GREEN                                    $4.66
0.778kg NET @ $5.99/kg
BANANA CAVENDISH                                  $1.32
0.442kg NET @ $2.99/kg
SPECIAL                                           $0.99
SPECIAL                                           $1.50
POTATOES BRUSHED                                  $3.97
1.328kg NET @ $2.99/kg
BROCCOLI                                          $4.84
0.808kg NET @ $5.99/kg
BRUSSEL SPROUTS                                   $5.15
0.322kg NET @ $15.99/kg
SPECIAL                                           $0.99
GRAPES GREEN                                      $7.03
1.174kg NET @ $5.99/kg
PEAS SNOW                                         $3.27
0.218kg NET @ $14.99/kg
TOMATOES GRAPE                                    $2.99
LETTUCE ICEBERG                                   $2.49
                  SUBTOTAL                       $39.20
                  LOYALTY                        -15.00
                  SUBTOTAL                       $24.20
                  SUBTOTAL                       $24.20
---------------------------------------------------
                  SUBTOTAL                       $24.20
                  TOTAL                          $24.20
CASH                                             $50.00
CHANGE                                           $25.80""",
        "expected": {
            "date": "2016-08-01",
            "items": [
                {"name": "ZUCHINNI GREEN", "quantity": 0.778, "price": 4.66, "unit_price": 5.99},
                {"name": "BANANA CAVENDISH", "quantity": 0.442, "price": 1.32, "unit_price": 2.99},
                {"name": "SPECIAL", "quantity": 1, "price": 0.99},
                {"name": "SPECIAL", "quantity": 1, "price": 1.50},
                {"name": "POTATOES BRUSHED", "quantity": 1.328, "price": 3.97, "unit_price": 2.99},
                {"name": "BROCCOLI", "quantity": 0.808, "price": 4.84, "unit_price": 5.99},
                {"name": "BRUSSEL SPROUTS", "quantity": 0.322, "price": 5.15, "unit_price": 15.99},
                {"name": "SPECIAL", "quantity": 1, "price": 0.99},
                {"name": "GRAPES GREEN", "quantity": 1.174, "price": 7.03, "unit_price": 5.99},
                {"name": "PEAS SNOW", "quantity": 0.218, "price": 3.27, "unit_price": 14.99},
                {"name": "TOMATOES GRAPE", "quantity": 1, "price": 2.99},
                {"name": "LETTUCE ICEBERG", "quantity": 1, "price": 2.49}
            ],
            "total": 24.20,
            "subtotal": 39.20
        }
    },
    {
        "name": "Lorem Shop",
        "text": """LOREM SHOP

1  9275  bi qrat mayn           2.99
2  0230  Salami                 4.99
3  0642  Red magnat             1.70
4  0257  Monay nigh             6.99
5  3860  Bread                  3.49
6  9463  Naturam zriet          9.10
7  2656  Amazimad               7.49
8  5688  Koleny mu              4.99

                    TOTAL       $34.50""",
        "expected": {
            "merchant_name": "Lorem Shop",
            "items": [
                {"name": "bi qrat mayn", "quantity": 1, "price": 2.99},
                {"name": "Salami", "quantity": 1, "price": 4.99},
                {"name": "Red magnat", "quantity": 1, "price": 1.70},
                {"name": "Monay nigh", "quantity": 1, "price": 6.99},
                {"name": "Bread", "quantity": 1, "price": 3.49},
                {"name": "Naturam zriet", "quantity": 1, "price": 9.10},
                {"name": "Amazimad", "quantity": 1, "price": 7.49},
                {"name": "Koleny mu", "quantity": 1, "price": 4.99}
            ],
            "total": 34.50
        }
    },
    {
        "name": "Target",
        "text": """TARGET
Greenwood C1tg - 888-888-8888
1234 Main Street
Anywhere, STATE 12345
06/01/16

ELECTRONICS                         1    $12.49 K
MARIO KART 7 FOR 3DS   T
RESISTANT DESIGN       N             $43.99
BIOSHOCK      INFINITE T             $39.75
NAIL POLISH            N
DENIM Jeans Skinny     N             $2.98
DAFT PUNK              N             $9.78

                       SUBTOTAL      $35.85
                       T = CA TAX 7% 75003 =  $32.30
                                   1         $35.85
REDEC485< -3235-7285-951-2 DB20-20< >XX    $35.85

Thank You!""",
        "expected": {
            "merchant_name": "Target",
            "date": "2016-06-01",
            "items": [
                {"name": "ELECTRONICS", "quantity": 1, "price": 12.49},
                {"name": "MARIO KART 7 FOR 3DS", "quantity": 1, "price": 43.99},
                {"name": "RESISTANT DESIGN", "quantity": 1, "price": 43.99},
                {"name": "BIOSHOCK INFINITE", "quantity": 1, "price": 39.75},
                {"name": "NAIL POLISH", "quantity": 1, "price": 2.98},
                {"name": "DENIM Jeans Skinny", "quantity": 1, "price": 9.78}
            ],
            "total": 35.85
        }
    },
    {
        "name": "Nigiri Restaurant",
        "text": """Guest Count: 1                                9/3/24 6:35

Ordered:

Carafe Sofo Jummai                             $24.00
Nigiri1 Otoro Duties                          $42.00
Nigiri1 Spanish Mackerel (Aji)                $42.00
Nigiri1 Sweet Shrimp (Amaebi)                 $12.00
Nigiri1 Amberjack (Hamachi)                   $15.00
Nigiri1 Salmon Hand Roll        (4.50%)        $5.44

                                Subtotal      $126.44
                                Tax            $12.00
                                Total         $163.61""",
        "expected": {
            "date": "2024-09-03",
            "items": [
                {"name": "Carafe Sofo Jummai", "quantity": 1, "price": 24.00},
                {"name": "Nigiri1 Otoro Duties", "quantity": 1, "price": 42.00},
                {"name": "Nigiri1 Spanish Mackerel (Aji)", "quantity": 1, "price": 42.00},
                {"name": "Nigiri1 Sweet Shrimp (Amaebi)", "quantity": 1, "price": 12.00},
                {"name": "Nigiri1 Amberjack (Hamachi)", "quantity": 1, "price": 15.00},
                {"name": "Nigiri1 Salmon Hand Roll", "quantity": 1, "price": 5.44}
            ],
            "total": 163.61,
            "subtotal": 126.44
        }
    },
    {
        "name": "Cosmopolitan",
        "text": """COSMOPOLITAN
33 ST MARKS PL CHELEY
NJ NJ 07392 08790
            
10-20-2019    10:00-2:00 11    N: 001
CHEK NO.115                   COVE06

1  BEEF GYRO                              40.80
1  LAMB                                   40.00
2  GYRO                                   50.00
1  OPEN FOOD                              £75.16
   PITA                                    5.00
   EAT IN2                                 0.00

                       FOOD      435.16+

THANK YOU FOR YOUR CUSTOM
HAVE A GREAT DAY. ****-INCLUDED""",
        "expected": {
            "merchant_name": "Cosmopolitan",
            "date": "2019-10-20",
            "items": [
                {"name": "BEEF GYRO", "quantity": 1, "price": 40.80},
                {"name": "LAMB", "quantity": 1, "price": 40.00},
                {"name": "GYRO", "quantity": 2, "price": 50.00},
                {"name": "OPEN FOOD", "quantity": 1, "price": 75.16},
                {"name": "PITA", "quantity": 1, "price": 5.00},
                {"name": "EAT IN2", "quantity": 1, "price": 0.00}
            ],
            "total": 435.16
        }
    },
    {
        "name": "Purgatory 777",
        "text": """PURGATORY 777
25 MAIN AVENUE, FLORIDA
1234-123-12345
VANYA CUSTOMER 9090002000

CUSTOMER CODE :  EB06W8V8000
MEMO CODE WEE

Date: Feb-03-sep                   Token No:25

Item Name       Qty    Rate    Amount
MOMO            1.00   548.00   548.00
Sada Dosa       1.00   500.0    500.0

                     Sub Total    1048.00
                        Round       0.00
                   Grand Total    1119.50
                  Service Tax      71.50

Even Split (4)?

Rs. No.           9             User: RANGAN

Thanking you .""",
        "expected": {
            "merchant_name": "Purgatory 777",
            "date": None,  # Date format unclear
            "items": [
                {"name": "MOMO", "quantity": 1, "price": 548.00, "unit_price": 548.00},
                {"name": "Sada Dosa", "quantity": 1, "price": 500.0, "unit_price": 500.0}
            ],
            "total": 1119.50,
            "subtotal": 1048.00
        }
    }
]


def run_ground_truth_tests():
    """Test parser against ground truth data"""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ocr-service'))
    
    from intelligent_receipt_parser import IntelligentReceiptParser
    
    parser = IntelligentReceiptParser()
    
    total_tests = len(RECEIPT_GROUND_TRUTH)
    passed = 0
    failures = []
    
    print(f"Running {total_tests} ground truth tests...")
    print("=" * 80)
    
    for idx, test_case in enumerate(RECEIPT_GROUND_TRUTH, 1):
        print(f"\n[{idx}/{total_tests}] Testing: {test_case['name']}")
        print("-" * 80)
        
        # Parse the receipt text
        result = parser.parse_receipt(test_case['text'])
        expected = test_case['expected']
        
        # Check results
        issues = []
        
        # Check merchant name
        if 'merchant_name' in expected:
            if result.get('merchant_name', '').lower() != expected['merchant_name'].lower():
                issues.append(f"  [X] Merchant: got '{result.get('merchant_name')}', expected '{expected['merchant_name']}'")
        
        # Check date
        if expected.get('date'):
            if result.get('date') != expected['date']:
                issues.append(f"  [X] Date: got '{result.get('date')}', expected '{expected['date']}'")
        
        # Check total
        result_total = result.get('total', 0)
        expected_total = expected.get('total', 0)
        if abs(result_total - expected_total) > 0.01:
            issues.append(f"  [X] Total: got ${result_total:.2f}, expected ${expected_total:.2f}")
        
        # Check item count
        result_items = len(result.get('items', []))
        expected_items = len(expected.get('items', []))
        if result_items != expected_items:
            issues.append(f"  [X] Item count: got {result_items}, expected {expected_items}")
        
        # Check individual items
        for exp_item in expected.get('items', []):
            # Find matching item by name
            found = False
            for res_item in result.get('items', []):
                if exp_item['name'].lower() in res_item.get('name', '').lower():
                    found = True
                    # Check price
                    res_price = res_item.get('price') or 0.0
                    exp_price = exp_item.get('price', 0)
                    if abs(res_price - exp_price) > 0.01:
                        issues.append(f"  [X] Item '{exp_item['name']}': price ${res_price:.2f} != ${exp_price:.2f}")
                    # Check quantity if specified
                    if 'quantity' in exp_item:
                        if abs(res_item.get('quantity', 1) - exp_item.get('quantity', 1)) > 0.01:
                            issues.append(f"  [X] Item '{exp_item['name']}': qty {res_item.get('quantity')} != {exp_item['quantity']}")
                    break
            
            if not found:
                issues.append(f"  [X] Missing item: '{exp_item['name']}'")
        
        # Report results
        if not issues:
            print(f"  [OK] PASSED")
            passed += 1
        else:
            print(f"  [FAIL] FAILED:")
            for issue in issues:
                print(issue)
            
            failures.append({
                'name': test_case['name'],
                'issues': issues
            })
        
        print(f"\n  Found {len(result.get('items', []))} items, total ${result.get('total', 0):.2f}")
    
    # Summary
    print(f"\n\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"[OK] Passed: {passed}/{total_tests} ({100*passed//total_tests}%)")
    print(f"[FAIL] Failed: {len(failures)}/{total_tests}")
    
    if failures:
        print(f"\n[FAIL] Failed Tests:")
        for fail in failures:
            print(f"\n  {fail['name']}:")
            for issue in fail['issues']:
                print(f"    {issue}")
    
    return passed == total_tests


if __name__ == "__main__":
    success = run_ground_truth_tests()
    sys.exit(0 if success else 1)
