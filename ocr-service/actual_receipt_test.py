import requests
import re
import json
import os
from PIL import Image, ImageDraw, ImageFont

def create_actual_receipt_image():
    """Create a realistic store receipt for testing with better formatting"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Realistic receipt content with proper formatting
    receipt_content = [
        "WALMART SUPERCENTER",
        "1234 MAIN STREET",
        "ANYTOWN, ST 12345",
        "",
        "TEL: (555) 123-4567",
        "",
        "TRANSACTION #: 1234567890",
        "CASHIER: JANE D",
        "DATE: 01/15/2024",
        "TIME: 14:32:15",
        "",
        "ITEMS SOLD: 5",
        "",
        "MILK 2% GAL        3.49",
        "BREAD WHT          2.29",
        "EGGS DOZ LG        4.99",
        "CHEESE CHED        5.99",
        "BANANAS LB         1.99",
        "",
        "SUBTOTAL          17.75",
        "TAX               1.42",
        "TOTAL             19.17",
        "",
        "CASH             20.00",
        "CHANGE            0.83",
        "",
        "THANK YOU FOR SHOPPING!",
        "",
        "RECEIPT # 123456789012345"
    ]
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    y_position = 30
    for line in receipt_content:
        if line.strip() == "":
            y_position += 15
            continue
        draw.text((30, y_position), line, fill='black', font=font)
        y_position += 25

    img_path = os.path.join(os.getcwd(), 'actual_receipt.png')
    img.save(img_path)
    return img_path

def ocr_space_file(filename, api_key='helloworld', language='eng'):
    """Send file to OCR.space API and get JSON response"""
    payload = {
        'apikey': api_key,
        'language': language,
        'isOverlayRequired': True
    }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image', files={filename: f}, data=payload)
    return r.json()

def parse_actual_receipt_text(text_lines):
    """Parse actual receipt text to extract items and total"""
    items = []
    total = None
    
    print("=== Raw OCR Text ===")
    for line in text_lines:
        print(f"'{line}'")
    
    # Clean up the text lines
    cleaned_lines = [line.strip() for line in text_lines if line.strip()]
    
    # Skip patterns for headers/footers
    skip_patterns = [
        'WALMART', 'SUPERCENTER', 'MAIN STREET', 'ANYTOWN', 'TEL:', 'TRANSACTION',
        'CASHIER:', 'DATE:', 'TIME:', 'ITEMS SOLD:', 'SUBTOTAL', 'TAX', 'CASH',
        'CHANGE', 'THANK YOU', 'RECEIPT #'
    ]
    
    # More sophisticated parsing for split-line format
    i = 0
    while i < len(cleaned_lines):
        line = cleaned_lines[i]
        
        # Skip header/footer lines
        should_skip = any(pattern.upper() in line.upper() for pattern in skip_patterns)
        if should_skip or not line:
            i += 1
            continue
        
        # Method 1: Item and price on same line
        item_price_match = re.search(r'^(.+?)\s+(\d+\.\d{2})$', line)
        if item_price_match:
            item_name = item_price_match.group(1).strip()
            price = float(item_price_match.group(2))
            if item_name and len(item_name) > 2:
                items.append({"name": item_name, "price": price})
                i += 1
                continue
        
        # Method 2: Item on one line, price on next line
        if i + 1 < len(cleaned_lines):
            current_line = cleaned_lines[i]
            next_line = cleaned_lines[i + 1]
            
            # Check if current line looks like an item name and next line is a price
            price_match = re.match(r'^\s*(\d+\.\d{2})\s*$', next_line)
            if price_match:
                price = float(price_match.group(1))
                
                # Check if current line doesn't match skip patterns and looks like an item
                should_skip_current = any(pattern.upper() in current_line.upper() for pattern in skip_patterns)
                if not should_skip_current and len(current_line) > 2:
                    items.append({"name": current_line.strip(), "price": price})
                    i += 2
                    continue
        
        i += 1
    
    # Find total amount
    for line in cleaned_lines:
        line_upper = line.upper().strip()
        
        # Look for TOTAL patterns
        total_patterns = [
            r'TOTAL\s+(\d+\.\d{2})',
            r'TOTAL\s*:\s*(\d+\.\d{2})',
            r'TOTAL\s*\$\s*(\d+\.\d{2})'
        ]
        
        for pattern in total_patterns:
            total_match = re.search(pattern, line_upper)
            if total_match:
                total = float(total_match.group(1))
                break
        
        if total:
            break
    
    # Fallback: find the largest amount in the receipt
    if not total:
        amounts = []
        for line in cleaned_lines:
            # Find all amounts in the line
            amount_matches = re.findall(r'(\d+\.\d{2})', line)
            for amount_str in amount_matches:
                amount = float(amount_str)
                if 5 <= amount <= 200:  # Reasonable receipt total range
                    amounts.append(amount)
        
        if amounts:
            # The largest amount is likely the total
            total = max(amounts)
    
    return {"items": items, "total": total}

def test_actual_receipt():
    """Test OCR with actual receipt image"""
    # Create realistic receipt image
    img_path = create_actual_receipt_image()
    print(f"Created actual receipt image at: {img_path}")
    
    # Run OCR
    result = ocr_space_file(img_path, api_key='helloworld')
    
    if result['OCRExitCode'] == 1:
        text_lines = []
        for parsed in result['ParsedResults']:
            text_lines.extend(parsed['ParsedText'].splitlines())
        
        print("\n=== OCR Text Lines ===")
        for i, line in enumerate(text_lines):
            print(f"{i+1}: '{line.strip()}'")
        
        parsed_receipt = parse_actual_receipt_text(text_lines)
        print("\n=== Parsed Receipt ===")
        print(json.dumps(parsed_receipt, indent=4))
        
        return parsed_receipt
    else:
        print("Error:", result.get('ErrorMessage', 'Unknown error'))
        return None

if __name__ == "__main__":
    test_actual_receipt()