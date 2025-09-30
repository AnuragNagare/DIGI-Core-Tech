from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import Optional
import base64
import io
import os
import tempfile
import requests
from PIL import Image
import fitz  # PyMuPDF for PDF handling
import re
import json
from enhanced_ocr_service import EnhancedOCRService
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ocr_service = EnhancedOCRService()

app = FastAPI()

# Configure CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ocr")
async def process_ocr(file: UploadFile = File(...), lang: str = "en"):
    """Process uploaded image/PDF with OCR.space API"""
    try:
        # Read file content
        contents = await file.read()
        
        # Convert PDF to image if needed
        if file.content_type == "application/pdf":
            try:
                # Create temporary PDF file
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                    temp_pdf.write(contents)
                    temp_pdf_path = temp_pdf.name
                
                try:
                    # Open PDF with PyMuPDF
                    doc = fitz.open(temp_pdf_path)
                    page = doc[0]
                    
                    # Convert to image
                    mat = fitz.Matrix(2.0, 2.0)  # 2x scale = 144 DPI
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Convert to PIL Image
                    img_data = pix.tobytes("ppm")
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Convert to RGB if necessary
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Convert to base64 for OCR.space
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=95)
                    image_base64 = base64.b64encode(buffer.getvalue()).decode()
                    
                    doc.close()
                    
                finally:
                    os.unlink(temp_pdf_path)
                    
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"PDF processing failed: {str(e)}")
        else:
            # Handle image files directly
            try:
                img = Image.open(io.BytesIO(contents))
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=95)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Image processing failed: {str(e)}")
        
        # Map language codes
        language_mapping = {
            "en": "eng", "english": "eng",
            "es": "spa", "spanish": "spa",
            "fr": "fra", "french": "fra", 
            "de": "deu", "german": "deu",
            "it": "ita", "italian": "ita",
            "pt": "por", "portuguese": "por",
            "ru": "rus", "russian": "rus",
            "zh": "chi_sim", "chinese": "chi_sim", "chinese_simplified": "chi_sim",
            "zh-tw": "chi_tra", "chinese_traditional": "chi_tra",
            "ja": "jpn", "japanese": "jpn",
            "ko": "kor", "korean": "kor",
            "ar": "ara", "arabic": "ara",
            "hi": "hin", "hindi": "hin",
            "th": "tha", "thai": "tha",
            "vi": "vie", "vietnamese": "vie"
        }
        
        ocr_language = language_mapping.get(lang.lower(), lang.lower())
        
        # Use enhanced OCR service
        ocr_result = ocr_service.extract_text_from_image_bytes(contents, language=ocr_language)
        
        if ocr_result.get('success'):
            # Parse receipt text with advanced parsing
            parsed_data = ocr_service.advanced_parse_receipt_text(ocr_result.get('text', ''))
            
            # Format for display
            formatted_display = ocr_service.format_receipt_display(parsed_data)
            
            return {
                "success": True,
                "text": ocr_result.get('text', ''),
                "items": parsed_data.get('items', []),
                "total": parsed_data.get('totalAmount'),
                "subtotal": parsed_data.get('subtotal'),
                "tax": parsed_data.get('tax'),
                "purchaseDate": parsed_data.get('purchaseDate'),
                "storeName": parsed_data.get('storeName'),
                "paymentMethod": parsed_data.get('paymentMethod'),
                "confidence": parsed_data.get('confidence'),
                "formattedDisplay": formatted_display,
                "detected_language": lang,
                "rawResult": ocr_result,
                "textRegions": ocr_result.get('text_regions', []),
                "processingStats": {
                    "textLength": len(ocr_result.get('text', '')),
                    "itemCount": len(parsed_data.get('items', [])),
                    "confidenceScore": parsed_data.get('confidence', 0.0)
                }
            }
        else:
            return {
                "success": False,
                "error": ocr_result.get('error', 'OCR processing failed'),
                "text": "",
                "items": [],
                "confidence": 0.0
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"OCR processing failed: {str(e)}",
            "text": "",
            "items": []
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OCR Service"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Enhanced OCR Service is running",
        "endpoints": {
            "/ocr": "POST - Process uploaded image/PDF with enhanced OCR detection",
            "/test": "GET - Test OCR with sample receipt",
            "/health": "GET - Health check"
        },
        "features": [
            "Advanced image preprocessing",
            "Text region detection",
            "Enhanced receipt parsing",
            "Confidence scoring",
            "Formatted display output"
        ]
    }

@app.get("/test")
async def test_ocr():
    """Test endpoint with sample receipt"""
    try:
        # Create a sample receipt text
        sample_text = """
        WELCOME TO CITY MART
        123 Main Street, Anytown, USA
        
        01/15/2024  2:34 PM
        
        Milk 1% Gallon    $3.49
        Bread Whole Wheat  $2.99
        Eggs Large Dozen   $4.29
        Apples Red 3lb     $5.99
        
        SUBTOTAL          $16.76
        TAX               $1.34
        TOTAL             $18.10
        
        PAID WITH CARD
        THANK YOU FOR SHOPPING!
        """
        
        # Parse the sample
        parsed_data = ocr_service.advanced_parse_receipt_text(sample_text)
        formatted_display = ocr_service.format_receipt_display(parsed_data)
        
        return {
            "success": True,
            "sampleText": sample_text,
            "parsedData": parsed_data,
            "formattedDisplay": formatted_display,
            "testType": "sample_receipt"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
