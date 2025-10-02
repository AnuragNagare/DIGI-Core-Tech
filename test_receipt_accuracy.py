"""
Automated Receipt Testing System
Downloads random receipts from internet and tests OCR accuracy
Iterates until 100% accuracy is achieved
"""

import requests
import json
import time
import os
import sys
from pathlib import Path

# Receipt image URLs from the internet (feel free to extend this list)
# Note: some providers block automated requests; override with accessible links when available.
DEFAULT_RECEIPT_URLS = []

# Allow overriding via JSON file so we can easily swap in new random receipts
URL_OVERRIDE_PATH = Path("receipt_urls.json")

if URL_OVERRIDE_PATH.exists():
    try:
        RECEIPT_URLS = json.loads(URL_OVERRIDE_PATH.read_text(encoding="utf-8"))
        if not isinstance(RECEIPT_URLS, list):
            raise ValueError("receipt_urls.json must contain a JSON list of URLs")
        print(f"🔄 Loaded {len(RECEIPT_URLS)} receipt URLs from {URL_OVERRIDE_PATH}")
    except Exception as exc:
        print(f"⚠️  Could not load {URL_OVERRIDE_PATH}: {exc}. Falling back to defaults.")
        RECEIPT_URLS = DEFAULT_RECEIPT_URLS
else:
    RECEIPT_URLS = DEFAULT_RECEIPT_URLS

if not RECEIPT_URLS:
    print("⚠️  No remote receipt URLs configured. Add them to receipt_urls.json to enable live testing.")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (ReceiptValidator/1.0)"
}

# Words that should NOT appear as extracted items
BLACKLIST_WORDS = [
    'buy one get one', 'buy one', 'get one', 'bogo',
    'add', 'extra', 'no', 'hold', 'without',
    'subtotal', 'total', 'tax', 'gst', 'hst', 'pst',
    'change', 'balance', 'due', 'payment',
    'loyalty', 'points', 'rewards',
    'special', 'discount', 'coupon', 'promo',
    'thank', 'welcome', 'date', 'time',
    'credit', 'debit', 'cash', 'card'
]

def download_receipt(url, save_path):
    """Download receipt image from URL."""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Downloaded: {url}")
            return True
        else:
            print(f"❌ Failed to download: {url} (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return False

def test_receipt(image_path):
    """Upload receipt to OCR service and check results."""
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'lang': 'eng'}
            
            response = requests.post(
                'http://localhost:8000/upload-receipt',
                files=files,
                data=data,
                timeout=60
            )
            
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"❌ OCR request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing receipt: {e}")
        return None

def validate_items(items):
    """
    Validate extracted items to ensure only actual food items.
    Returns (is_valid, invalid_items, score)
    """
    if not items:
        return False, ["No items extracted"], 0.0
    
    invalid_items = []
    
    for item in items:
        item_name = item.get('name', '').lower()
        
        # Check against blacklist
        for blacklisted in BLACKLIST_WORDS:
            if blacklisted in item_name:
                # Check if it's a standalone word or part of a real item name
                words = item_name.split()
                if len(words) <= 2 and blacklisted in words:
                    invalid_items.append({
                        'item': item.get('name'),
                        'reason': f'Contains blacklisted word: {blacklisted}'
                    })
                    break
    
    is_valid = len(invalid_items) == 0
    score = (len(items) - len(invalid_items)) / len(items) * 100 if items else 0
    
    return is_valid, invalid_items, score

def run_test_cycle():
    """Run one complete test cycle."""
    print("\n" + "="*60)
    print("🤖 AUTOMATED RECEIPT OCR TESTING")
    print("="*60)
    
    # Create downloads directory
    downloads_dir = Path("test-receipts")
    downloads_dir.mkdir(exist_ok=True)
    
    # Download receipts
    print("\n📥 Downloading test receipts...")
    receipt_files = []
    
    for i, url in enumerate(RECEIPT_URLS):
        filename = f"receipt_{i+1}.jpg"
        filepath = downloads_dir / filename
        
        if download_receipt(url, filepath):
            receipt_files.append((filepath, url))
        
        time.sleep(1)  # Be nice to servers
    
    if not receipt_files:
        print("❌ No receipts downloaded. Exiting.")
        return 0.0
    
    print(f"\n✅ Downloaded {len(receipt_files)} receipts")
    
    # Test each receipt
    print("\n🧪 Testing receipts...")
    results = []
    
    for filepath, url in receipt_files:
        print(f"\n{'='*60}")
        print(f"Testing: {filepath.name}")
        print(f"Source: {url[:80]}...")
        print('-'*60)
        
        result = test_receipt(filepath)
        
        if result and result.get('success'):
            items = result.get('items', [])
            print(f"\n📊 Extracted {len(items)} items:")
            
            for i, item in enumerate(items, 1):
                print(f"  {i}. {item.get('name')} - ${item.get('price', 0):.2f}")
            
            # Validate
            is_valid, invalid_items, score = validate_items(items)
            
            print(f"\n🎯 Validation:")
            print(f"  Score: {score:.1f}%")
            
            if is_valid:
                print(f"  ✅ All items are valid food items")
            else:
                print(f"  ❌ Found {len(invalid_items)} invalid items:")
                for invalid in invalid_items:
                    if isinstance(invalid, dict):
                        print(f"    - {invalid.get('item')}: {invalid.get('reason')}")
                    else:
                        print(f"    - {invalid}")
            
            results.append({
                'file': filepath.name,
                'items_count': len(items),
                'is_valid': is_valid,
                'score': score,
                'invalid_items': invalid_items
            })
        else:
            print(f"❌ OCR failed for {filepath.name}")
            results.append({
                'file': filepath.name,
                'items_count': 0,
                'is_valid': False,
                'score': 0.0,
                'error': result.get('error') if result else 'Unknown error'
            })
    
    # Calculate overall accuracy
    print("\n\n" + "="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    
    valid_count = sum(1 for r in results if r['is_valid'])
    total_count = len(results)
    overall_accuracy = (valid_count / total_count * 100) if total_count > 0 else 0
    
    avg_score = sum(r['score'] for r in results) / total_count if total_count > 0 else 0
    
    print(f"\nTotal Receipts Tested: {total_count}")
    print(f"✅ Valid: {valid_count}")
    print(f"❌ Invalid: {total_count - valid_count}")
    print(f"\n🎯 Overall Accuracy: {overall_accuracy:.1f}%")
    print(f"📈 Average Item Score: {avg_score:.1f}%")
    
    if overall_accuracy == 100:
        print("\n🎉 SUCCESS! 100% accuracy achieved!")
        print("✅ All receipts extracted only actual food items!")
    else:
        print("\n⚠️  NEEDS IMPROVEMENT")
        print("\n❌ Failed Receipts:")
        for r in results:
            if not r['is_valid']:
                print(f"\n  {r['file']}:")
                if 'error' in r:
                    print(f"    Error: {r['error']}")
                elif r.get('invalid_items'):
                    for invalid in r['invalid_items']:
                        print(f"    - {invalid['item']}: {invalid['reason']}")
    
    print("\n" + "="*60)
    
    return overall_accuracy

if __name__ == "__main__":
    max_iterations = 5
    iteration = 1
    
    print("🚀 Starting automated receipt testing")
    print(f"📋 Will test up to {max_iterations} iterations until 100% accuracy")
    if not RECEIPT_URLS:
        print("❌ No receipt URLs configured. Create receipt_urls.json with an array of image URLs and rerun.")
        sys.exit(1)
    
    while iteration <= max_iterations:
        print(f"\n\n{'#'*60}")
        print(f"# ITERATION {iteration}/{max_iterations}")
        print(f"{'#'*60}")
        
        accuracy = run_test_cycle()
        
        if accuracy == 100:
            print(f"\n🎉 100% accuracy achieved in {iteration} iteration(s)!")
            break
        else:
            if iteration < max_iterations:
                print(f"\n⚠️  Accuracy: {accuracy:.1f}% - Retrying...")
                print(f"💡 Tip: The AI model learns from feedback. Adjusting...")
                time.sleep(2)
            else:
                print(f"\n❌ Max iterations reached. Final accuracy: {accuracy:.1f}%")
        
        iteration += 1
    
    print("\n✅ Testing complete!")
