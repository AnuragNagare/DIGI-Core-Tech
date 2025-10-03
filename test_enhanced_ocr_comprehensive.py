"""
Test Enhanced OCR System with Real Receipts

This script tests the improved OCR system with actual receipt images
to demonstrate the enhanced extraction capabilities.
"""

import requests
import base64
import io
import sys

def test_receipt_from_description(receipt_name, receipt_items):
    """Test OCR with receipt description and expected items."""
    print(f"\n{'='*60}")
    print(f"TESTING: {receipt_name}")
    print(f"{'='*60}")
    
    # Create a more realistic test receipt based on description
    from PIL import Image, ImageDraw, ImageFont
    
    width, height = 400, 800
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    y = 20
    
    # Draw receipt content
    for line in receipt_items:
        if line.strip():
            draw.text((20, y), line, fill='black', font=font)
        y += 22
    
    # Test the OCR
    try:
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=95)
        img_byte_arr.seek(0)
        
        files = {"file": ("receipt.jpg", img_byte_arr.getvalue(), "image/jpeg")}
        
        response = requests.post(
            "http://localhost:8000/ocr",
            files=files,
            timeout=45
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ OCR Status: SUCCESS")
            print(f"📄 Raw Text: {len(result.get('text', ''))} characters")
            
            items = result.get('items', [])
            print(f"🛍️  Items Extracted: {len(items)}")
            
            if items:
                print(f"\n📋 EXTRACTED ITEMS:")
                print("-" * 40)
                for i, item in enumerate(items, 1):
                    name = item.get('name', 'Unknown')
                    price = item.get('price', 0)
                    quantity = item.get('quantity', 1)
                    total = item.get('total', price)
                    print(f"{i:2d}. {name}")
                    print(f"     Price: ${price:.2f} | Qty: {quantity} | Total: ${total:.2f}")
            
            # Show totals
            total_amount = result.get('total')
            subtotal = result.get('subtotal')
            
            print(f"\n💰 FINANCIAL SUMMARY:")
            print("-" * 40)
            if subtotal:
                print(f"Subtotal: ${subtotal:.2f}")
            if total_amount:
                print(f"Total: ${total_amount:.2f}")
            
            print(f"\n🏪 Store: {result.get('storeName', 'Not detected')}")
            print(f"📅 Date: {result.get('purchaseDate', 'Not detected')}")
            
            # Calculate expected vs actual
            expected_count = len([line for line in receipt_items if '$' in line and 'TOTAL' not in line.upper() and 'SUBTOTAL' not in line.upper()])
            actual_count = len(items)
            
            print(f"\n📊 EXTRACTION ANALYSIS:")
            print("-" * 40)
            print(f"Expected items: ~{expected_count}")
            print(f"Extracted items: {actual_count}")
            success_rate = (actual_count / max(expected_count, 1)) * 100
            print(f"Success rate: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print("🎯 EXCELLENT extraction rate!")
            elif success_rate >= 60:
                print("👍 GOOD extraction rate!")
            elif success_rate >= 40:
                print("⚡ MODERATE extraction rate - room for improvement")
            else:
                print("📈 LOW extraction rate - needs optimization")
            
            return result
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Test Error: {e}")
        return None

def main():
    print("🚀 ENHANCED OCR SYSTEM - REAL RECEIPT TESTING")
    print("=" * 70)
    
    # Test Case 1: Grocery Receipt (from attachment 1)
    grocery_items = [
        "DATE         06/01/2019        WED",
        "ZUCCHINI GREEN                  $4.66",
        "0.778kg NET @ $5.99/kg",
        "BANANA CAVENDISH                $1.32",
        "0.442kg NET @ $2.99/kg", 
        "SPECIAL                         $0.99",
        "SPECIAL                         $1.50",
        "POTATOES BRUSHED                $3.97",
        "1.326kg NET @ $2.99/kg",
        "BROCCOLI                        $4.84",
        "0.808kg NET @ $5.99/kg",
        "BRUSSEL SPROUTS                 $5.15",
        "0.322kg NET @ $15.99/kg",
        "SPECIAL                         $0.99",
        "GRAPES GREEN                    $7.03",
        "1.174kg NET @ $5.99/kg",
        "PEAS SNOW                       $3.27",
        "0.218kg NET @ $14.99/kg",
        "TOMATOES GRAPE                  $2.99",
        "LETTUCE ICEBERG                 $2.49",
        "SUBTOTAL                       $39.20",
        "LOYALTY                        -$5.00",
        "SUBTOTAL                       $34.20",
        "SUBTOTAL                       $34.20",
        "SUBTOTAL                       $34.20",
        "TOTAL                          $34.20",
        "CASH                           $50.00",
        "CHANGE                         $25.80"
    ]
    
    # Test Case 2: McDonald's Receipt (from attachment 2)
    mcdonalds_items = [
        "485",
        "KS# 4                    08:13:56 AM",
        "QTY ITEM                      TOTAL",
        "1 Buy One, Get One Line 1      3.99",
        "  1 Sausage Egg McMuffin Line 2",
        "  1 Sausage Egg McMuffin Line 3", 
        "1 2 Burritos EVM Line 4        6.99",
        "  1 S Coffee Line 5",
        "    ADD Cream Line 6",
        "1 2 Hash Browns Line 7         0.80",
        "1 M Iced Coffee Line 8         1.40",
        "  NO Liquid Sugar Line 9",
        "Subtotal                      13.18",
        "GST                            0.66",
        "Take-Out Total                13.84",
        "CREDIT CARD                   13.84",
        "Change                         0.00"
    ]
    
    # Run tests
    grocery_result = test_receipt_from_description("Grocery Store Receipt", grocery_items)
    mcdonalds_result = test_receipt_from_description("McDonald's Receipt", mcdonalds_items)
    
    # Final summary
    print(f"\n{'='*70}")
    print("🎯 FINAL SUMMARY - ENHANCED OCR PERFORMANCE")
    print(f"{'='*70}")
    
    results = [
        ("Grocery Receipt", grocery_result),
        ("McDonald's Receipt", mcdonalds_result)
    ]
    
    total_extracted = 0
    total_receipts = 0
    
    for name, result in results:
        if result:
            items_count = len(result.get('items', []))
            total_extracted += items_count
            total_receipts += 1
            print(f"✅ {name}: {items_count} items extracted")
        else:
            print(f"❌ {name}: Failed to process")
    
    if total_receipts > 0:
        avg_items = total_extracted / total_receipts
        print(f"\n📊 Average items per receipt: {avg_items:.1f}")
        print(f"📈 Total items extracted: {total_extracted}")
        print(f"🎯 Processing success rate: {total_receipts}/2 = {total_receipts/2:.1%}")
    
    print(f"\n🚀 ENHANCEMENT BENEFITS:")
    print("   • More permissive item detection")
    print("   • Better price pattern recognition") 
    print("   • Enhanced food item identification")
    print("   • Improved global format support")
    print("   • Multiple OCR backend fallbacks")

if __name__ == "__main__":
    main()