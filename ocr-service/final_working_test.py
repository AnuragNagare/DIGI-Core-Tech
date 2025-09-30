import requests
import re
import json
import os
from PIL import Image, ImageDraw, ImageFont

def create_working_receipt_image():
    """Create a receipt with items and prices on same line"""
    width, height = 500, 400
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Format items with prices on same line
    receipt_lines = [
        "RECEIPT",
        "",
        "MILK $3.49",
        "BREAD $2.29",
        "EGGS $4.99", 
        "CHEESE $5.99",
        "BANANAS $1.99",
        "",
        "TOTAL $19.17"
    ]

    y = 30
    for line in receipt_lines:
        draw.text((30, y), line, fill='black', font=font)
        y += 25

    img_path = os.path.join(os.getcwd(), 'working_receipt.png')
    img.save(img_path)
    return img_path

def ocr_space_file(filename, api_key='helloworld', language='eng'):
    """Send file to OCR.space API"""
    payload = {
        'apikey': api_key,
        'language': language,
        'isOverlayRequired': True
    }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image', files={filename: f}, data=payload)
    return r.json()

def parse_working_receipt(text_lines):
    """Parse receipt with items and prices on same line"""
    items = []
    total = None
    
    print("=== OCR Results ===")
    for i, line in enumerate(text_lines):
        print(f"{i+1}: '{line.strip()}'")
    
    for line in text_lines:
        line = line.strip()
        if not line or line.upper() == "RECEIPT":
            continue
            
        # Parse total first (to avoid including it as an item)
        total_match = re.search(r'^TOTAL\s*\$?(\d+\.\d{2})$', line.strip(), re.IGNORECASE)
        if total_match:
            total = float(total_match.group(1))
            continue
            
        # Parse items (NAME $PRICE)
        item_match = re.search(r'^([A-Z\s]+)\s*\$?(\d+\.\d{2})$', line.strip())
        if item_match:
            name = item_match.group(1).strip()
            price = float(item_match.group(2))
            # Skip if this looks like a total line
            if name.upper() != "TOTAL":
                items.append({"name": name, "price": price})
    
    return {"items": items, "total": total}

def test_working_receipt():
    """Complete test of OCR.space integration"""
    print("🧾 Testing OCR.space - Displaying Actual Receipt Items")
    print("=" * 60)
    
    # Create test receipt
    img_path = create_working_receipt_image()
    print(f"✅ Created receipt: {img_path}")
    
    # Run OCR
    result = ocr_space_file(img_path, api_key='helloworld')
    
    if result['OCRExitCode'] == 1:
        text_lines = []
        for parsed in result['ParsedResults']:
            text_lines.extend(parsed['ParsedText'].splitlines())
        
        # Parse results
        parsed_data = parse_working_receipt(text_lines)
        
        print("\n📋 DISPLAYED ITEMS:")
        print("-" * 30)
        for i, item in enumerate(parsed_data['items'], 1):
            print(f"{i}. {item['name']} - ${item['price']}")
        
        print(f"\n💰 TOTAL: ${parsed_data['total']}")
        
        # Validate results
        expected_items = 5
        expected_total = 19.17
        
        if len(parsed_data['items']) == expected_items and abs(parsed_data['total'] - expected_total) < 0.01:
            print(f"\n🎉 SUCCESS: All {len(parsed_data['items'])} items displayed correctly!")
        else:
            print(f"\n⚠️  Expected {expected_items} items, got {len(parsed_data['items'])}")
            
        return True
    else:
        print("❌ OCR Error:", result.get('ErrorMessage', 'Unknown error'))
        return False

if __name__ == "__main__":
    test_working_receipt()