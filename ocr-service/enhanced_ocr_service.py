import os
import re
import logging
import time
import requests
from typing import Dict, Any, Optional, List
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io
import base64
import json
from datetime import datetime
import cv2
import numpy as np

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedOCRService:
    """Enhanced OCR service with advanced text detection and parsing capabilities."""
    
    def __init__(self):
        self.api_key = os.getenv("OCR_SPACE_API_KEY", "K83171300288957")
        self.base_url = "https://api.ocr.space/parse/imageurl"
        
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Advanced image preprocessing for better OCR accuracy.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            max_size = (2000, 2000)
            if image.width > max_size[0] or image.height > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up text
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL Image
            processed_image = Image.fromarray(cleaned)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(processed_image)
            enhanced = enhancer.enhance(2.0)
            
            # Enhance sharpness
            sharpener = ImageEnhance.Sharpness(enhanced)
            sharpened = sharpener.enhance(1.5)
            
            return sharpened
            
        except Exception as e:
            logger.warning(f"Preprocessing failed: {e}, using original image")
            return image
    
    def detect_text_regions(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detect text regions using OpenCV for better OCR targeting.
        
        Args:
            image: PIL Image object
            
        Returns:
            List of text regions with bounding boxes
        """
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                
                # Filter small regions (likely noise)
                if area > 1000 and w > 50 and h > 20:
                    text_regions.append({
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'area': area
                    })
            
            return sorted(text_regions, key=lambda r: r['area'], reverse=True)
            
        except Exception as e:
            logger.warning(f"Text region detection failed: {e}")
            return []
    
    def extract_text_from_image_bytes(self, image_bytes: bytes, language='eng') -> Dict[str, Any]:
        """
        Enhanced text extraction with preprocessing and multiple detection strategies.
        
        Args:
            image_bytes: Raw image bytes
            language: Language code for OCR
            
        Returns:
            Dictionary with extracted text and detailed metadata
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Detect text regions
            text_regions = self.detect_text_regions(processed_image)
            
            # Convert to JPEG for OCR.space
            img_byte_arr = io.BytesIO()
            processed_image.save(img_byte_arr, format='JPEG', quality=95)
            img_byte_arr.seek(0)
            
            files = {
                'file': ('receipt.jpg', img_byte_arr.getvalue(), 'image/jpeg')
            }
            
            # Enhanced OCR parameters
            data = {
                'apikey': self.api_key,
                'language': language,
                'isOverlayRequired': 'true',  # Get bounding boxes
                'detectOrientation': 'true',
                'scale': 'true',
                'OCREngine': '2',
                'isTable': 'true',
                'detectCheckbox': 'false'
            }
            
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files=files,
                data=data,
                timeout=30
            )
            
            result = response.json()
            
            if not result.get('IsErroredOnProcessing'):
                parsed_text = result.get('ParsedResults', [{}])[0].get('ParsedText', '').strip()
                overlay = result.get('ParsedResults', [{}])[0].get('TextOverlay', {})
                
                if parsed_text:
                    return {
                        'success': True,
                        'text': parsed_text,
                        'text_regions': text_regions,
                        'overlay': overlay,
                        'rawResult': result,
                        'confidence': self.calculate_confidence(parsed_text)
                    }
                else:
                    return {
                        'success': False,
                        'text': '',
                        'error': 'No text found in image',
                        'text_regions': text_regions
                    }
            else:
                error_msg = result.get('ErrorMessage', 'OCR processing failed')
                return {
                    'success': False,
                    'text': '',
                    'error': error_msg,
                    'text_regions': text_regions
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'text': '',
                'error': 'OCR request timed out (30s)',
                'text_regions': []
            }
        except Exception as e:
            return {
                'success': False,
                'text': '',
                'error': f'OCR processing failed: {str(e)}',
                'text_regions': []
            }
    
    def calculate_confidence(self, text: str) -> float:
        """Calculate confidence score based on text characteristics."""
        if not text:
            return 0.0
        
        # Basic confidence factors
        has_numbers = bool(re.search(r'\d', text))
        has_currency = bool(re.search(r'[$€£¥₹]', text))
        has_line_items = bool(re.search(r'\n.*\$?\d+\.\d{2}', text))
        
        confidence = 0.5  # Base confidence
        
        if has_numbers:
            confidence += 0.2
        if has_currency:
            confidence += 0.15
        if has_line_items:
            confidence += 0.15
        
        return min(confidence, 1.0)
    
    def advanced_parse_receipt_text(self, text: str) -> Dict[str, Any]:
        """
        Advanced receipt parsing with multiple strategies and confidence scoring.
        
        Args:
            text: Raw OCR text from receipt
            
        Returns:
            Dictionary with detailed parsed receipt data
        """
        if not text:
            return {
                "items": [],
                "totalAmount": None,
                "subtotal": None,
                "tax": None,
                "purchaseDate": None,
                "storeName": None,
                "paymentMethod": None,
                "confidence": 0.0,
                "rawText": text
            }
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Initialize results
        items = []
        total_amount = None
        subtotal = None
        tax = None
        purchase_date = None
        store_name = None
        payment_method = None
        
        # Advanced item detection patterns
        item_patterns = [
            r'^(.*?)\s+(\d+(?:\.\d{1,2})?)\s*@?\s*\$?(\d+(?:\.\d{2}))',  # Item Qty Price
            r'^(.*?)\s+\$?(\d+\.\d{2})',  # Item Price
            r'^(.*?)\s+(\d+(?:\.\d{1,2})?)\s*x\s*\$?(\d+(?:\.\d{2}))',  # Item QtyxPrice
        ]
        
        # Look for items
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            for pattern in item_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    if len(groups) == 3:
                        # Item with quantity and price
                        item_name = groups[0].strip()
                        quantity = float(groups[1])
                        price = float(groups[2])
                        
                        if 'total' not in item_name.lower() and price < 1000:
                            items.append({
                                "name": item_name,
                                "price": price,
                                "quantity": quantity,
                                "total": quantity * price
                            })
                    elif len(groups) == 2:
                        # Simple item with price
                        item_name = groups[0].strip()
                        price = float(groups[1])
                        
                        if 'total' not in item_name.lower() and price < 1000:
                            items.append({
                                "name": item_name,
                                "price": price,
                                "quantity": 1,
                                "total": price
                            })
                    break
        
        # Advanced total detection
        total_patterns = [
            r'total[\s:]*\$?(\d+(?:\.\d{2}))',
            r'amount\s+due[\s:]*\$?(\d+(?:\.\d{2}))',
            r'balance[\s:]*\$?(\d+(?:\.\d{2}))',
            r'grand\s+total[\s:]*\$?(\d+(?:\.\d{2}))',
            r'subtotal[\s:]*\$?(\d+(?:\.\d{2}))',
            r'tax[\s:]*\$?(\d+(?:\.\d{2}))',
        ]
        
        for line in lines:
            line_lower = line.lower()
            for pattern in total_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    amount = float(match.group(1))
                    if 'tax' in line_lower:
                        tax = amount
                    elif 'subtotal' in line_lower:
                        subtotal = amount
                    elif total_amount is None or amount > total_amount:
                        total_amount = amount
        
        # Date detection
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',
        ]
        
        for line in lines:
            for pattern in date_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    purchase_date = match.group(0)
                    break
        
        # Store name detection (usually at top)
        if lines:
            # Look for store-like names in first few lines
            for i, line in enumerate(lines[:3]):
                line = line.strip()
                if len(line) > 3 and len(line) < 50:
                    # Common store indicators
                    store_indicators = ['mart', 'store', 'shop', 'grocery', 'market', 'super', 'pharmacy']
                    if any(indicator in line.lower() for indicator in store_indicators):
                        store_name = line
                        break
            
            # If no store indicators, use first non-empty line
            if not store_name and lines[0]:
                store_name = lines[0]
        
        # Payment method detection
        payment_patterns = [
            r'(cash|credit|debit|visa|mastercard|amex|paypal|check)',
            r'(paid\s+with\s+.*)',
        ]
        
        for line in lines:
            line_lower = line.lower()
            for pattern in payment_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    payment_method = match.group(1) if match.group(1) else match.group(0)
                    break
        
        # Calculate confidence based on parsed data
        confidence = self.calculate_parsing_confidence(items, total_amount, subtotal, tax)
        
        return {
            "items": items,
            "totalAmount": total_amount,
            "subtotal": subtotal,
            "tax": tax,
            "purchaseDate": purchase_date,
            "storeName": store_name,
            "paymentMethod": payment_method,
            "confidence": confidence,
            "rawText": text,
            "totalItems": len(items),
            "calculatedTotal": sum(item["total"] for item in items) if items else None
        }
    
    def calculate_parsing_confidence(self, items: List[Dict], total: float, subtotal: float, tax: float) -> float:
        """Calculate confidence score for parsed receipt data."""
        confidence = 0.0
        
        if items:
            confidence += 0.3
            
            # Check if calculated total matches detected total
            calculated_total = sum(item["total"] for item in items)
            if total and abs(calculated_total - total) < 0.1:
                confidence += 0.3
            elif total and abs(calculated_total - total) < 1.0:
                confidence += 0.2
        
        if total:
            confidence += 0.2
        
        if subtotal:
            confidence += 0.1
        
        if tax:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def format_receipt_display(self, parsed_data: Dict[str, Any]) -> str:
        """
        Format parsed receipt data for display.
        
        Args:
            parsed_data: Parsed receipt data
            
        Returns:
            Formatted string for display
        """
        if not parsed_data.get('items'):
            return "No items detected in receipt."
        
        lines = []
        lines.append("=" * 50)
        
        if parsed_data.get('storeName'):
            lines.append(f"Store: {parsed_data['storeName']}")
        
        if parsed_data.get('purchaseDate'):
            lines.append(f"Date: {parsed_data['purchaseDate']}")
        
        lines.append("-" * 50)
        lines.append("Items:")
        lines.append("-" * 50)
        
        for i, item in enumerate(parsed_data['items'], 1):
            name = item.get('name', 'Unknown Item')
            quantity = item.get('quantity', 1)
            price = item.get('price', 0.0)
            total = item.get('total', price)
            
            if quantity > 1:
                lines.append(f"{i:2d}. {name} ({quantity}x ${price:.2f}) = ${total:.2f}")
            else:
                lines.append(f"{i:2d}. {name} = ${total:.2f}")
        
        lines.append("-" * 50)
        
        if parsed_data.get('subtotal'):
            lines.append(f"Subtotal: ${parsed_data['subtotal']:.2f}")
        
        if parsed_data.get('tax'):
            lines.append(f"Tax: ${parsed_data['tax']:.2f}")
        
        if parsed_data.get('totalAmount'):
            lines.append(f"TOTAL: ${parsed_data['totalAmount']:.2f}")
        
        if parsed_data.get('paymentMethod'):
            lines.append(f"Payment: {parsed_data['paymentMethod'].title()}")
        
        lines.append("=" * 50)
        lines.append(f"Confidence: {parsed_data.get('confidence', 0.0) * 100:.1f}%")
        
        return "\n".join(lines)