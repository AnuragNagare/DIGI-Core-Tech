"""Check exact indentation of McDonald's receipt"""

MCDONALDS_RECEIPT = """
485

KS# 4                           08:13:56 AM
QTY ITEM                        TOTAL
  1 Buy One, Get One             3.99
    1 Sausage Egg McMuffin
    1 Sausage Egg McMuffin
  1 2 Burritos EVM                6.99
    1 S Coffee
      ADD Cream
    1 2 Hash Browns                0.80
  1 M Iced Coffee                  1.40
      NO Liquid Sugar

Subtotal                         13.18
GST                               0.66
Take-Out Total                   13.84
CREDIT CARD                      13.84
Change                            0.00
"""

lines = MCDONALDS_RECEIPT.split('\n')

print("Line-by-line analysis:")
print("="*60)
for i, line in enumerate(lines):
    if line.strip():
        indent = len(line) - len(line.lstrip())
        print(f"Line {i:2d} (indent={indent:2d}): '{line[:50]}'")
