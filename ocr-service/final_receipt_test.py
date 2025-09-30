import requests
import re
import json
import os
from PIL import Image, ImageDraw, ImageFont

def create_clean_receipt_image():
    """Create a clean, simple receipt for better OCR accuracy"""
    width, height = 600, 500
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Simple receipt format
    receipt_content = [
        "GROCERY STORE",
        "123 MAIN ST",
        "",
        "MILK          3.49",
        "BREAD         2.29", 
        "EGGS          4.99",
        "CHEESE        5.99",
        "BANANAS       1.99",
        "",
        "TOTAL        19.17"
    ]
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    y_position = 30
    for line in receipt_content:
        if line.strip() == "":
            y_position += 15
            continue
        draw.text((30, y_position), line, fill='black', font=font)
        y_position += 30

    img_path = os.path.join(os.getcwd(), 'clean_receipt.png')
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

def parse_clean_receipt(text_lines):
    """Parse clean receipt text"""
    items = []
    total = None
    
    print("=== OCR Text ===")
    for i, line in enumerate(text_lines):
        print(f"{i+1}: '{line.strip()}'")
    
    # Parse items and total
    for line in text_lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse items (ITEM_NAME PRICE)
        item_match = re.match(r'^([A-Z\s]+)\s+(\d+\.\d{2})$', line.strip())
        if item_match:
            item_name = item_match.group(1).strip()
            price = float(item_match.group(2))
            items.append({"name": item_name, "price": price})
        
        # Parse total
        total_match = re.match(r'^TOTAL\s+(\d+\.\d{2})$', line.strip())
        if total_match:
            total = float(total_match.group(1))
    
    return {"items": items, "total": total}

def test_final_receipt():
    """Test OCR with clean receipt"""
    # Create clean receipt image
    img_path = create_clean_receipt_image()
    print(f"Created clean receipt at: {img_path}")
    
    # Run OCR
    result = ocr_space_file(img_path, api_key='helloworld')
    
    if result['OCRExitCode'] == 1:
        text_lines = []
        for parsed in result['ParsedResults']:
            text_lines.extend(parsed['ParsedText'].splitlines())
        
        parsed_receipt = parse_clean_receipt(text_lines)
        print("\n=== Final Parsed Receipt ===")
        print(json.dumps(parsed_receipt, indent=4))
        
        return parsed_receipt
    else:
        print("Error:", result.get('ErrorMessage', 'Unknown error'))
        return None

if __name__ == "__main__":
    test_final_receipt()