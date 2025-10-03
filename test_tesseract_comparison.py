"""
Comprehensive Testing Script: Tesseract OCR vs OCR.space
========================================================

This script tests the OCR service with multiple receipt samples
and compares the results from Tesseract and OCR.space engines.

Author: DIGI Team
Date: 2024
"""

import requests
import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# API endpoint
OCR_API_URL = "http://localhost:8000/ocr"

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_section(text: str):
    """Print a formatted section header"""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'-'*len(text)}{Colors.ENDC}")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def test_receipt_image(image_path: str, receipt_name: str) -> Dict[str, Any]:
    """
    Test a receipt image with the OCR API.
    
    Args:
        image_path: Path to the receipt image
        receipt_name: Descriptive name for the receipt
        
    Returns:
        Dictionary with test results
    """
    print_section(f"Testing: {receipt_name}")
    print_info(f"Image: {image_path}")
    
    if not os.path.exists(image_path):
        print_error(f"Image not found: {image_path}")
        return {
            'receipt_name': receipt_name,
            'success': False,
            'error': 'File not found'
        }
    
    try:
        # Read the image
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            data = {'language': 'eng'}
            
            # Send request
            print_info("Sending request to OCR API...")
            response = requests.post(OCR_API_URL, files=files, data=data, timeout=60)
            
            if response.status_code != 200:
                print_error(f"API returned status code: {response.status_code}")
                return {
                    'receipt_name': receipt_name,
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
            
            result = response.json()
            
            if not result.get('success'):
                print_error(f"OCR failed: {result.get('error', 'Unknown error')}")
                return {
                    'receipt_name': receipt_name,
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }
            
            # Extract key information
            ocr_engine = result.get('ocrEngine', 'unknown')
            ocr_confidence = result.get('ocrConfidence', 0)
            items = result.get('items', [])
            total = result.get('total')
            text_length = len(result.get('text', ''))
            
            # Print results
            print_success(f"OCR Engine: {Colors.BOLD}{ocr_engine.upper()}{Colors.ENDC}")
            
            if ocr_confidence:
                confidence_color = Colors.OKGREEN if ocr_confidence > 80 else Colors.WARNING if ocr_confidence > 60 else Colors.FAIL
                print_info(f"OCR Confidence: {confidence_color}{ocr_confidence:.1f}%{Colors.ENDC}")
            
            print_info(f"Text Length: {text_length} characters")
            print_info(f"Items Extracted: {Colors.BOLD}{len(items)}{Colors.ENDC}")
            
            if items:
                print("\n  Extracted Items:")
                for idx, item in enumerate(items, 1):
                    name = item.get('name', 'Unknown')
                    price = item.get('price', 0)
                    quantity = item.get('quantity', 1)
                    print(f"    {idx}. {name}")
                    print(f"       Price: ${price:.2f} | Quantity: {quantity}")
            else:
                print_warning("  No items extracted!")
            
            if total:
                print(f"\n  {Colors.BOLD}Total: ${total:.2f}{Colors.ENDC}")
            else:
                print_warning("  Total not detected")
            
            # Show sample of extracted text
            text_sample = result.get('text', '')[:200].replace('\n', ' ')
            print(f"\n  Text Sample: {text_sample}...")
            
            return {
                'receipt_name': receipt_name,
                'success': True,
                'ocr_engine': ocr_engine,
                'ocr_confidence': ocr_confidence,
                'items_count': len(items),
                'items': items,
                'total': total,
                'text_length': text_length,
                'full_result': result
            }
            
    except requests.exceptions.Timeout:
        print_error("Request timed out after 60 seconds")
        return {
            'receipt_name': receipt_name,
            'success': False,
            'error': 'Timeout'
        }
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return {
            'receipt_name': receipt_name,
            'success': False,
            'error': str(e)
        }


def generate_comparison_report(results: List[Dict[str, Any]]):
    """
    Generate a comprehensive comparison report.
    
    Args:
        results: List of test results
    """
    print_header("COMPREHENSIVE TEST RESULTS SUMMARY")
    
    # Separate results by OCR engine
    tesseract_results = [r for r in results if r.get('success') and r.get('ocr_engine') == 'tesseract']
    ocrspace_results = [r for r in results if r.get('success') and r.get('ocr_engine') == 'ocrspace']
    failed_results = [r for r in results if not r.get('success')]
    
    print_section("Overall Statistics")
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {Colors.OKGREEN}{len([r for r in results if r.get('success')])}{Colors.ENDC}")
    print(f"Failed: {Colors.FAIL}{len(failed_results)}{Colors.ENDC}")
    
    print_section("OCR Engine Usage")
    print(f"Tesseract OCR: {Colors.OKGREEN}{len(tesseract_results)} receipts{Colors.ENDC}")
    print(f"OCR.space: {Colors.OKBLUE}{len(ocrspace_results)} receipts{Colors.ENDC}")
    
    if tesseract_results:
        print_section("Tesseract OCR Performance")
        avg_confidence = sum(r.get('ocr_confidence', 0) for r in tesseract_results) / len(tesseract_results)
        avg_items = sum(r.get('items_count', 0) for r in tesseract_results) / len(tesseract_results)
        avg_text_length = sum(r.get('text_length', 0) for r in tesseract_results) / len(tesseract_results)
        
        print(f"Average Confidence: {avg_confidence:.1f}%")
        print(f"Average Items Extracted: {avg_items:.1f}")
        print(f"Average Text Length: {avg_text_length:.0f} characters")
        
        print("\nReceipts processed by Tesseract:")
        for r in tesseract_results:
            print(f"  • {r['receipt_name']}: {r['items_count']} items, {r.get('ocr_confidence', 0):.1f}% confidence")
    
    if ocrspace_results:
        print_section("OCR.space Performance")
        avg_items = sum(r.get('items_count', 0) for r in ocrspace_results) / len(ocrspace_results)
        avg_text_length = sum(r.get('text_length', 0) for r in ocrspace_results) / len(ocrspace_results)
        
        print(f"Average Items Extracted: {avg_items:.1f}")
        print(f"Average Text Length: {avg_text_length:.0f} characters")
        
        print("\nReceipts processed by OCR.space:")
        for r in ocrspace_results:
            print(f"  • {r['receipt_name']}: {r['items_count']} items")
    
    if failed_results:
        print_section("Failed Tests")
        for r in failed_results:
            print(f"  • {r['receipt_name']}: {r.get('error', 'Unknown error')}")
    
    # Item extraction comparison
    print_section("Item Extraction Comparison")
    
    # Create comparison table
    print(f"\n{'Receipt Name':<30} | {'OCR Engine':<12} | {'Items':<6} | {'Total':<10} | {'Confidence':<12}")
    print("-" * 85)
    
    for r in results:
        if r.get('success'):
            name = r['receipt_name'][:28]
            engine = r.get('ocr_engine', 'N/A')[:10]
            items = r.get('items_count', 0)
            total = f"${r.get('total', 0):.2f}" if r.get('total') else "N/A"
            confidence = f"{r.get('ocr_confidence', 0):.1f}%" if r.get('ocr_confidence') else "N/A"
            
            print(f"{name:<30} | {engine:<12} | {items:<6} | {total:<10} | {confidence:<12}")
    
    # Determine winner
    print_section("Winner Analysis")
    
    if tesseract_results and ocrspace_results:
        tesseract_avg_items = sum(r.get('items_count', 0) for r in tesseract_results) / len(tesseract_results)
        ocrspace_avg_items = sum(r.get('items_count', 0) for r in ocrspace_results) / len(ocrspace_results)
        
        if tesseract_avg_items > ocrspace_avg_items:
            print_success(f"WINNER: Tesseract OCR ({tesseract_avg_items:.1f} items vs {ocrspace_avg_items:.1f} items)")
            print_info("Tesseract extracted more items on average!")
        elif ocrspace_avg_items > tesseract_avg_items:
            print_success(f"WINNER: OCR.space ({ocrspace_avg_items:.1f} items vs {tesseract_avg_items:.1f} items)")
            print_info("OCR.space extracted more items on average!")
        else:
            print_info("TIE: Both engines performed equally well!")
    elif tesseract_results:
        print_success("Only Tesseract OCR was used (primary engine)")
        print_info("All receipts were successfully processed by Tesseract!")
    elif ocrspace_results:
        print_warning("Only OCR.space was used (fallback engine)")
        print_info("Tesseract may have failed or not been available")
    
    # Save detailed results to JSON
    print_section("Saving Detailed Results")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"ocr_test_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'total_tests': len(results),
            'successful_tests': len([r for r in results if r.get('success')]),
            'tesseract_count': len(tesseract_results),
            'ocrspace_count': len(ocrspace_results),
            'results': results
        }, f, indent=2)
    
    print_success(f"Detailed results saved to: {output_file}")


def main():
    """Main testing function"""
    print_header("OCR SERVICE COMPREHENSIVE TESTING")
    print_info(f"Testing API at: {OCR_API_URL}")
    print_info(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define test receipts
    test_receipts = [
        ("test_mcdonalds_sample.png", "McDonald's Receipt"),
        ("test_grocery_sample.png", "Grocery Store Receipt"),
        ("test_restaurant_sample.png", "Restaurant Receipt"),
        ("test_receipt.png", "Original Test Receipt"),
        ("test_receipt_final.png", "Final Test Receipt"),
    ]
    
    # Find available receipt images
    available_receipts = []
    for image_path, receipt_name in test_receipts:
        if os.path.exists(image_path):
            available_receipts.append((image_path, receipt_name))
    
    if not available_receipts:
        print_error("No test receipt images found!")
        print_info("Please place test receipt images in the current directory:")
        for image_path, receipt_name in test_receipts:
            print(f"  • {image_path}")
        return
    
    print_info(f"Found {len(available_receipts)} test receipts")
    
    # Test each receipt
    results = []
    for image_path, receipt_name in available_receipts:
        result = test_receipt_image(image_path, receipt_name)
        results.append(result)
    
    # Generate comparison report
    if results:
        generate_comparison_report(results)
    
    print_header("TESTING COMPLETE")
    print_success(f"Tested {len(results)} receipts")
    print_info(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
