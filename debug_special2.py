import sys
import re
sys.path.insert(0, 'ocr-service')

text = "SPECIAL 2.50"
text_lower = text.lower()

# Extract just the item name (before price) for checking
item_name_only = re.sub(r'\s*\$?\d+\.\d{2}\s*$', '', text).strip().lower()

print(f"Testing: {text}")
print(f"Item name only: '{item_name_only}'")

BLACKLIST_KEYWORDS = {
    'subtotal', 'sub-total', 'sub total', 'total', 'change', 'cash', 'credit',
    'debit', 'card', 'payment', 'amount', 'balance', 'due', 'paid', 'tender',
    'loyalty', 'points', 'rewards', 'member', 'savings', 'discount', 'coupon',
    'promo', 'promotion',
    'receipt', 'invoice', 'order', 'transaction', 'ref', 'reference',
    'store', 'location', 'address', 'phone', 'tel', 'email',
    'date', 'time', 'day', 'month', 'year',
    'net', 'gross', '@', 'ea', 'each', 'per', 'pkg', 'pack', 'package',
    'number', 'no', '#', 'id', 'code', 'sku', 'barcode',
    'tax', 'gst', 'pst', 'hst', 'vat', 'duty', 'fee', 'surcharge',
    'thank', 'welcome', 'hello', 'goodbye', 'please', 'visit',
    'come', 'again', 'see you', 'have a', 'enjoy',
}

# Add 'special' if missing
BLACKLIST_KEYWORDS.add('special')

print(f"\nIs 'special' in blacklist? {'special' in BLACKLIST_KEYWORDS}")

# Test the loop
for keyword in BLACKLIST_KEYWORDS:
    if keyword in text_lower:
        print(f"\nFound keyword: '{keyword}'")
        
        if keyword in ['special', 'discount', 'promo']:
            print(f"  It's a special keyword")
            print(f"  item_name_only == keyword? {item_name_only == keyword}")
            if item_name_only == keyword:
                print(f"  -> Should BLACKLIST")
                break
