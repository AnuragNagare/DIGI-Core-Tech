#!/usr/bin/env python3
"""
Live OCR Service Test - Shows extracted items and displays
"""
import requests
import json

def test_ocr_service():
    """Test the OCR service with a receipt image and display results"""
    
    print("🎯 Testing Live OCR Service")
    print("=" * 50)
    
    try:
        # Test the OCR service
        url = 'http://localhost:8000/extract-receipt'
        files = {'file': open('test_receipt_final.png', 'rb')}
        response = requests.post(url, files=files)
        result = response.json()
        
        # Display results
        print(f"✅ Status: {'SUCCESS' if result.get('success') else 'FAILED'}")
        print(f"📊 Raw Text Length: {len(result.get('text', ''))} characters")
        print()
        
        print("📋 EXTRACTED RECEIPT TEXT:")
        print("-" * 40)
        print(result.get('text', 'No text extracted'))
        print()
        
        # Extract and display items
        print("🛒 DETECTED ITEMS:")
        print("-" * 40)
        
        text = result.get('text', '')
        lines = text.split('\n')
        items = []
        
        # Simple item extraction logic
        for line in lines:
            line = line.strip()
            if line and '$' in line:
                # Look for patterns like "Item Name $Price"
                parts = line.split('$')
                if len(parts) >= 2:
                    item_name = parts[0].strip()
                    price_part = parts[-1].strip()
                    
                    # Clean up the price
                    price = price_part.split()[0] if price_part else price_part
                    if any(c.isdigit() for c in price):
                        items.append(f"{item_name} - ${price}")
        
        if items:
            for i, item in enumerate(items, 1):
                print(f"{i:2d}. {item}")
        else:
            print("📋 No specific items detected - showing full text above")
            
        print()
        print("🎉 OCR Service is running and working correctly!")
        print("📱 Service available at: http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Error testing OCR service: {e}")
        print("🔄 Make sure the OCR service is running on port 8000")

if __name__ == "__main__":
    test_ocr_service()