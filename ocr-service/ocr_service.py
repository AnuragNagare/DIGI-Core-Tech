import os
import re
import logging
import time
import requests
from typing import Dict, Any, Optional, List
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRSpaceService:
    """OCR.space API service for text extraction from images and PDFs."""
    
    def __init__(self):
        self.api_key = os.getenv("OCR_SPACE_API_KEY", "K83171300288957")
        self.base_url = "https://api.ocr.space/parse/imageurl"
        
    def extract_text_from_image_bytes(self, image_bytes: bytes, language='eng') -> Dict[str, Any]:
        """
        Extract text from image using OCR.space API with optimized processing.
        
        Args:
            image_bytes: Raw image bytes
            language: Language code for OCR (eng, spa, fra, deu, chi_sim, chi_tra, jpn, kor, etc.)
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
                
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Ensure image is in RGB mode
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Simple resize if image is too large to speed up processing
            max_size = (2000, 2000)
            if image.width > max_size[0] or image.height > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to JPEG for OCR.space
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr.seek(0)
            
            files = {
                'file': ('receipt.jpg', img_byte_arr.getvalue(), 'image/jpeg')
            }
            
            # Optimized OCR parameters for speed
            data = {
                'apikey': self.api_key,
                'language': language,
                'isOverlayRequired': 'false',
                'detectOrientation': 'true',
                'scale': 'true',
                'OCREngine': '2',
                'isTable': 'true'
            }
            
            # Make request with shorter timeout
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files=files,
                data=data,
                timeout=15  # Reduced timeout
            )
            
            result = response.json()
            
            if not result.get('IsErroredOnProcessing'):
                parsed_text = result.get('ParsedResults', [{}])[0].get('ParsedText', '').strip()
                if parsed_text:
                    return {
                        'success': True,
                        'text': parsed_text,
                        'rawResult': result
                    }
                else:
                    return {
                        'success': False,
                        'text': '',
                        'error': 'No text found in image'
                    }
            else:
                error_msg = result.get('ErrorMessage', 'OCR processing failed')
                return {
                    'success': False,
                    'text': '',
                    'error': error_msg
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'text': '',
                'error': 'OCR request timed out (15s)'
            }
        except Exception as e:
            return {
                'success': False,
                'text': '',
                'error': f'OCR processing failed: {str(e)}'
            }

    def parse_receipt_text(self, text: str) -> Dict[str, Any]:
        """
        Parse receipt text to extract structured data.
        
        Args:
            text: Raw OCR text from receipt
            
        Returns:
            Dictionary with parsed receipt data
        """
        if not text:
            return {"items": [], "totalAmount": None, "purchaseDate": None}
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        items = []
        total_amount = None
        purchase_date = None
        
        # Simple item detection patterns
        item_patterns = [
            r'([A-Za-z\s]+)\s+\$?(\d+\.\d{2})',  # Item Name $price
            r'([A-Za-z\s]+)\s+(\d+\.\d{2})\s*$',  # Item Name price
        ]
        
        # Look for items
        for line in lines:
            for pattern in item_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    item_name = match.group(1).strip()
                    price = float(match.group(2))
                    
                    # Skip if it looks like a total
                    if 'total' not in item_name.lower() and price < 1000:
                        items.append({
                            "name": item_name,
                            "price": price,
                            "quantity": 1
                        })
        
        # Look for total amount
        total_patterns = [
            r'total[\s:]*\$?(\d+\.\d{2})',
            r'amount[\s:]*\$?(\d+\.\d{2})',
            r'balance[\s:]*\$?(\d+\.\d{2})',
        ]
        
        for line in lines:
            for pattern in total_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    total_amount = float(match.group(1))
                    break
        
        # If no total found, use highest item price
        if not total_amount and items:
            total_amount = sum(item["price"] for item in items)
        
        return {
            "items": items,
            "totalAmount": total_amount,
            "purchaseDate": purchase_date,
            "rawText": text
        }