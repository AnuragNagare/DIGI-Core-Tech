"""
Intelligent Receipt Item Extractor
Uses ML + Rule-based filtering to extract ONLY real food items from receipts
Ignores: totals, subtotals, payment info, dates, store names, loyalty numbers, etc.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReceiptItem:
    """Represents a single food/grocery item from a receipt."""
    name: str
    quantity: float
    price: float
    unit_price: float = None
    unit: str = None
    confidence: float = 0.0
    
class IntelligentReceiptParser:
    """
    Intelligent parser that extracts ONLY actual food/grocery items.
    Filters out all receipt metadata, totals, and irrelevant text.
    """
    
    def __init__(self):
        # Words/phrases that indicate NON-ITEM lines (to be filtered out)
        self.BLACKLIST_KEYWORDS = {
            # Receipt metadata
            'subtotal', 'sub-total', 'sub total', 'total', 'change', 'cash', 'credit',
            'debit', 'card', 'payment', 'amount', 'balance', 'due', 'paid', 'tender',
            
            # Loyalty & discounts
            'loyalty', 'points', 'rewards', 'member', 'savings', 'discount', 'coupon',
            'promo', 'promotion', 'special', 'buy one', 'get one', 'bogo', 'deal',
            
            # Receipt info
            'receipt', 'invoice', 'order', 'transaction', 'ref', 'reference',
            'store', 'location', 'address', 'phone', 'tel', 'email',
            
            # Date/Time
            'date', 'time', 'day', 'month', 'year',
            
            # Units without item names (these appear alone on receipt)
            'net', 'gross', '@', 'ea', 'each', 'per', 'pkg', 'pack', 'package',
            
            # Numbers/codes alone
            'number', 'no', '#', 'id', 'code', 'sku', 'barcode',
            
            # Tax related
            'tax', 'gst', 'pst', 'hst', 'vat', 'duty', 'fee', 'surcharge',
            
            # Greetings
            'thank', 'welcome', 'hello', 'goodbye', 'please', 'visit',
            'come', 'again', 'see you', 'have a', 'enjoy',
        }
        
        # Words that commonly appear in ONLY unit descriptions (not item names)
        self.UNIT_ONLY_KEYWORDS = {
            'kg', 'g', 'lb', 'oz', 'l', 'ml', 'net', 'wt', 'weight'
        }
        
        # Common food categories (helps validate if something is a food item)
        self.FOOD_CATEGORIES = {
            # Vegetables
            'lettuce', 'tomato', 'potato', 'onion', 'carrot', 'broccoli', 'spinach',
            'pepper', 'cucumber', 'zucchini', 'zuchinni', 'squash', 'celery', 'cabbage', 
            'pea', 'peas', 'bean', 'beans', 'corn', 'mushroom', 'asparagus', 'brussel', 'sprout', 'sprouts',
            
            # Fruits
            'apple', 'banana', 'orange', 'grape', 'grapes', 'strawberry', 'blueberry', 'melon',
            'mango', 'pineapple', 'peach', 'pear', 'cherry', 'avocado', 'kiwi',
            'lemon', 'lime', 'grapefruit', 'plum',
            
            # Proteins
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp', 'turkey',
            'lamb', 'bacon', 'sausage', 'ham', 'egg', 'eggs', 'tofu',
            
            # Dairy
            'milk', 'cheese', 'yogurt', 'butter', 'cream', 'ice cream',
            
            # Grains
            'bread', 'rice', 'pasta', 'cereal', 'flour', 'oat', 'oats', 'quinoa',
            
            # Beverages
            'juice', 'soda', 'water', 'coffee', 'tea', 'beer', 'wine',
            
            # Other groceries
            'oil', 'sugar', 'salt', 'spice', 'sauce', 'soup', 'nut', 'nuts', 'seed', 'seeds',
        }
    
    def is_blacklisted(self, text: str) -> bool:
        """Check if text contains blacklisted keywords."""
        import re
        
        text_lower = text.lower()
        
        # Extract just the item name (before price) for checking
        item_name_only = re.sub(r'\s*\$?\d+\.\d{2}\s*$', '', text).strip().lower()
        
        # Short keywords that need word boundary matching to avoid false positives
        # (e.g., 'ea' shouldn't match 'peas', 'no' shouldn't match 'snow', 'fee' shouldn't match 'coffee')
        short_keywords = {'ea', 'no', '@', '#', 'id', 'per', 'fee', 'tax', 'gst', 'pst', 'hst', 'vat'}
        
        # Check for exact blacklist matches
        for keyword in self.BLACKLIST_KEYWORDS:
            # For short keywords, use word boundaries
            if keyword in short_keywords:
                # Match only if it's a complete word
                if not re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    continue  # Not a match, skip to next keyword
            else:
                # For longer keywords, simple substring match
                if keyword not in text_lower:
                    continue  # Not a match, skip to next keyword
            
            # If we get here, the keyword was found
            logger.debug(f"  🔍 Found keyword '{keyword}' in '{text[:50]}'")
            
            # Special handling for certain keywords
            if keyword in ['special', 'discount', 'promo']:
                # If the item name is ONLY this keyword (like "SPECIAL 2.50"), blacklist it
                if item_name_only == keyword:
                    logger.debug(f"  ❌ Blacklisting (standalone promo)")
                    return True
                
                # If it has food words (like "CHICKEN SPECIAL"), allow it
                if any(food in text_lower for food in self.FOOD_CATEGORIES):
                    logger.debug(f"  ✅ Allowing (has food word)")
                    continue
                    
                # Short line without food words? Blacklist
                if len(item_name_only) < 15:
                    logger.debug(f"  ❌ Blacklisting (short promo)")
                    return True
            
            # If keyword is in food/beverage categories, DON'T blacklist
            if keyword in ['coffee', 'tea', 'juice', 'soda', 'water', 'beer', 'wine']:
                logger.debug(f"  ✅ Allowing (beverage keyword)")
                continue
            
            # For other blacklist words (totals, dates, etc.), always filter
            # unless they're unit descriptors that might be part of item names
            if keyword not in ['ea', 'no', '@', '#', 'id', 'per', 'net', 'each', 'pkg', 'pack', 'package']:
                logger.debug(f"  ❌ Blacklisting (metadata keyword)")
                return True
        
        return False
    
    def is_unit_descriptor_only(self, text: str) -> bool:
        """Check if text is ONLY a unit descriptor (like '0.442kg NET @ $2.99/kg')."""
        text_lower = text.lower()
        
        # If it starts with a number followed by kg/lb/etc and contains NET, it's a unit line
        if re.match(r'^\d+\.?\d*\s*(kg|g|lb|oz|net|wt)', text_lower):
            return True
        
        # If it's ONLY unit keywords
        words = text_lower.split()
        if all(word in self.UNIT_ONLY_KEYWORDS or word.replace('.', '').isdigit() for word in words):
            return True
        
        return False
    
    def is_likely_food_item(self, text: str) -> bool:
        """Check if text likely contains a food item name."""
        text_lower = text.lower()
        
        # Split into words for better matching
        words = text_lower.split()
        
        # Check if ANY word contains a known food keyword (partial matching)
        for word in words:
            for food in self.FOOD_CATEGORIES:
                # Partial match - allows "zucchini" to match "zuchinni"
                if food in word or word in food:
                    return True
        
        # Additional heuristics:
        # - Has letters and is not too short
        if len(text) < 3:
            return False
        
        # - Contains at least some alphabetic characters (not just numbers/symbols)
        if sum(c.isalpha() for c in text) < 3:
            return False
        
        # - If it's all caps and has a reasonable length, might be a product name
        # - AND it has a price, it's probably a food item (we already filtered blacklist)
        if text.isupper() and 3 < len(text) < 40:
            # If we got here and it's not blacklisted, and has a price, 
            # it's likely a food item
            return True
        
        # - If it has mixed case and reasonable length, could be food
        if 3 < len(text) < 40 and any(c.isalpha() for c in text):
            return True
        
        return False
    
    def extract_price_and_quantity(self, line: str) -> Tuple[float, float, str]:
        """
        Extract quantity and price from a receipt line.
        Returns: (quantity, price, remaining_text_for_item_name)
        Note: price defaults to 0.0 if not found (never None)
        """
        original_line = line
        quantity = 1.0
        price = 0.0  # Default to 0.0 instead of None to prevent TypeError in sum()
        
        # Pattern 0: Tab-separated format "Item Name \t Qty \t Rate \t Amount"
        # Example: "Pizza Large        1    430.0    430.0"
        if '\t' in line or '  ' in line:  # Multiple spaces or tabs
            parts = re.split(r'\s{2,}|\t+', line.strip())
            parts = [p.strip() for p in parts if p.strip()]
            
            if len(parts) >= 3:
                # Try to parse: [name, qty, rate, amount] or [name, qty, amount]
                # Look for numeric parts at the end
                numeric_parts = []
                name_parts = []
                
                for part in parts:
                    if re.match(r'^\d+\.?\d*$', part):
                        numeric_parts.append(float(part))
                    else:
                        # Check if it contains a price-like pattern
                        price_in_part = re.search(r'\$?(\d+\.\d{2})', part)
                        if price_in_part and len(part) < 15:  # Short, likely just a price
                            numeric_parts.append(float(price_in_part.group(1)))
                        else:
                            name_parts.append(part)
                
                if len(numeric_parts) >= 2:
                    # Format: [qty, rate, amount] or [qty, amount]
                    quantity = numeric_parts[0]
                    price = numeric_parts[-1]  # Last number is the amount
                    line = ' '.join(name_parts)
                    return quantity, price, line
        
        # Pattern 1: "ITEM $XX.XX" or "ITEM XX.XX" or "ITEM XX.X"
        # Match prices with 1 or 2 decimal places at end of line
        price_match = re.search(r'\$?(\d+\.\d{1,2})\s*$', line)
        if price_match:
            price = float(price_match.group(1))
            line = line[:price_match.start()].strip()
        
        # Pattern 2: "0.442kg NET @ $2.99/kg" - extract weight as quantity
        weight_match = re.search(r'(?:^|\s)(\d+\.?\d*)\s*(kg|g|lb|oz)\b', line.lower())
        if weight_match:
            weight = float(weight_match.group(1))
            unit = weight_match.group(2)
            
            # Convert to kg for consistency
            if unit == 'g':
                quantity = weight / 1000
            elif unit == 'lb':
                quantity = weight * 0.453592
            elif unit == 'oz':
                quantity = weight * 0.0283495
            else:
                quantity = weight
            
            # Remove this from the line
            # Remove this weight segment (remove matched span)
            start_index = weight_match.start()
            end_index = weight_match.end()
            # If match began with whitespace because of the non-capturing group, strip it too
            line = (line[:start_index].rstrip() + " " + line[end_index:].lstrip()).strip()
        
        # Pattern 3: Quantity at start "2 x ITEM" or "2 ITEM" 
        qty_match = re.match(r'^(\d+)\s*x?\s+', line.lower())
        if qty_match and not weight_match:  # Don't override weight-based quantity
            quantity = float(qty_match.group(1))
            line = line[qty_match.end():].strip()
        
        return quantity, price, line
    
    def clean_item_name(self, name: str) -> str:
        """Clean up item name by removing extra symbols and normalizing."""
        # Remove leading/trailing special chars
        name = re.sub(r'^[^\w]+|[^\w]+$', '', name)
        
        # Remove common suffixes that aren't part of the name
        name = re.sub(r'\s+(NET|@|ea|each|pkg).*$', '', name, flags=re.IGNORECASE)
        
        # Normalize spaces
        name = ' '.join(name.split())
        
        # Title case for better readability
        return name.title()
    
    def parse_receipt_items(self, ocr_text: str) -> List[Dict[str, Any]]:
        """
        Extract ONLY actual food/grocery items from OCR text.
        Handles both flat and hierarchical receipt formats.
        
        Args:
            ocr_text: Raw OCR text from receipt
            
        Returns:
            List of dictionaries with item details
        """
        if not ocr_text:
            logger.warning("Empty OCR text provided")
            return []
        
        # DON'T strip lines yet - we need indentation for hierarchical parsing
        lines_raw = [line.rstrip() for line in ocr_text.split('\n') if line.strip()]
        items = []
        seen_items = set()  # Avoid duplicates
        
        logger.info(f"Parsing {len(lines_raw)} lines from receipt")
        
        # Strategy 1: Look for hierarchical format (like McDonald's)
        # Lines with quantity and price, followed by indented item names
        hierarchical_items = self._parse_hierarchical_format(lines_raw)
        
        if hierarchical_items:
            logger.info(f"✅ Detected hierarchical format, extracted {len(hierarchical_items)} items")
            return hierarchical_items
        
        # Strategy 2: Flat format (item name and price on same line)
        # Keep original spacing for tab-separated formats
        logger.info("Using flat format parsing")
        
        for i, line_raw in enumerate(lines_raw):
            line = line_raw.strip()
            logger.debug(f"Processing line {i}: '{line}'")
            
            # Skip empty or very short lines
            if len(line) < 3:
                logger.debug(f"  ❌ Too short")
                continue
            
            # Filter 1: Blacklisted keywords (totals, dates, etc.)
            if self.is_blacklisted(line):
                logger.debug(f"  ❌ Blacklisted: '{line}'")
                continue
            
            # Filter 2: Unit descriptors only (like "0.442kg NET @ $2.99/kg")
            if self.is_unit_descriptor_only(line):
                logger.debug(f"  ❌ Unit descriptor only: '{line}'")
                continue
            
            # Filter 3: Must have a price ($ sign or decimal number)
            # Match $X.XX, XX.XX, X.X, etc.
            if not re.search(r'\$?\d+\.?\d*', line):
                logger.debug(f"  ❌ No price found: '{line}'")
                continue
            
            # Extract quantity and price (use raw line to preserve spacing)
            quantity, price, item_name_raw = self.extract_price_and_quantity(line_raw.strip())
            
            if not price or price <= 0:
                logger.debug(f"  ❌ Invalid price: {price}")
                continue
            
            # Clean item name
            item_name = self.clean_item_name(item_name_raw)
            
            # Filter 4: Must have a reasonable item name
            if len(item_name) < 3:
                logger.debug(f"  ❌ Name too short after cleaning: '{item_name}'")
                continue
            
            # Filter 5: Check if it's likely a food item
            if not self.is_likely_food_item(item_name):
                logger.debug(f"  ❌ Not a food item: '{item_name}'")
                continue
            
            # Avoid duplicates
            item_key = f"{item_name}_{price}"
            if item_key in seen_items:
                logger.debug(f"  ❌ Duplicate: '{item_name}'")
                continue
            
            seen_items.add(item_key)
            
            # Success! This is a real item
            item = {
                'name': item_name,
                'quantity': quantity,
                'price': price,
                'unit_price': self._compute_unit_price(price, quantity),
                'original_line': line
            }
            
            items.append(item)
            price_str = f"${price:.2f}" if price is not None else "No price"
            logger.info(f"  ✅ Extracted: {item_name} (qty: {quantity}, price: {price_str})")
        
        logger.info(f"Successfully extracted {len(items)} items from receipt")
        return items
    
    def _parse_hierarchical_format(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parse hierarchical receipt format like:
          1 Buy One, Get One    3.99
            1 Sausage Egg McMuffin
            1 Sausage Egg McMuffin
          1 2 Burritos EVM       6.99
            1 S Coffee
              ADD Cream
        """
        items = []
        seen_items = set()
        i = 0
        
        logger.debug(f"Starting hierarchical parsing with {len(lines)} lines")
        
        while i < len(lines):
            line = lines[i]
            original_line = line
            line_stripped = line.strip()
            
            # Check if line is indented (has leading spaces)
            indent_level = len(line) - len(line.lstrip())
            
            # Check if line has a price
            has_price = bool(re.search(r'\$?\d+\.\d{2}', line_stripped))
            
            logger.debug(f"Line {i}: indent={indent_level}, has_price={has_price}, text='{line_stripped[:40]}'")
            
            if has_price:  # Any line with a price could be a group header or item
                # This is a line item with price (might be at any indent level)
                quantity, price, item_name_raw = self.extract_price_and_quantity(line_stripped)
                
                # Check if this is a blacklisted group header (like "Buy One Get One")
                if self.is_blacklisted(line_stripped):
                    # It's a promotion/group header - extract the sub-items
                    logger.info(f"  📦 Found group header (blacklisted): {line_stripped[:50]}")
                    price_str = f"${price:.2f}" if price is not None else "No price"
                    logger.debug(f"     Indent level: {indent_level}, Price: {price_str}")
                    i += 1
                    
                    # Look ahead for indented sub-items
                    sub_item_count = 0
                    while i < len(lines):
                        next_line = lines[i]
                        next_stripped = next_line.strip()
                        next_indent = len(next_line) - len(next_line.lstrip())
                        
                        logger.debug(f"     Checking line {i}: indent={next_indent}, text='{next_stripped[:40]}'")
                        
                        # If next line is indented, it's a sub-item
                        if next_indent > indent_level and next_stripped:
                            logger.debug(f"       ✓ Line is indented ({next_indent} > {indent_level})")
                            
                            # Check if it's a modifier
                            if self._is_modifier(next_stripped):
                                logger.debug(f"       ✗ Skipping modifier: {next_stripped[:30]}")
                                i += 1
                                continue
                                
                            # Extract item name
                            item_name = self._clean_sub_item_name(next_stripped)
                            logger.debug(f"       Cleaned name: '{item_name}'")
                            
                            # Validate price before adding sub-item
                            if not price or price <= 0:
                                logger.debug(f"       ✗ Invalid parent price: {price}")
                                i += 1
                                continue
                            
                            if item_name and self.is_likely_food_item(item_name):
                                item_key = f"{item_name}_{price}_sub"
                                if item_key not in seen_items:
                                    items.append({
                                        'name': item_name,
                                        'quantity': 1,
                                        'price': price,  # Use parent's price
                                        'unit_price': price,
                                        'original_line': next_line
                                    })
                                    seen_items.add(item_key)
                                    sub_item_count += 1
                                    price_str = f"${price:.2f}" if price is not None else "No price"
                                    logger.info(f"  ✅ Extracted sub-item: {item_name} ({price_str})")
                                else:
                                    logger.debug(f"       ✗ Duplicate: {item_name}")
                            else:
                                logger.debug(f"       ✗ Not a food item: {item_name}")
                            i += 1
                        else:
                            # No more sub-items, back to main level
                            logger.debug(f"       ✗ Not indented enough ({next_indent} <= {indent_level}), exiting sub-item loop")
                            break
                    
                    logger.debug(f"     Extracted {sub_item_count} sub-items from group")
                    continue
                    
                else:
                    # It's a regular item with price (not blacklisted)
                    item_name = self.clean_item_name(item_name_raw)
                    
                    # Validate price before adding item
                    if not price or price <= 0:
                        logger.debug(f"  ❌ Invalid price in hierarchical: {price}")
                        i += 1
                        continue
                    
                    if item_name and self.is_likely_food_item(item_name) and len(item_name) >= 3:
                        item_key = f"{item_name}_{price}"
                        if item_key not in seen_items:
                            items.append({
                                'name': item_name,
                                'quantity': quantity,
                                'price': price,
                                'unit_price': self._compute_unit_price(price, quantity),
                                'original_line': original_line
                            })
                            seen_items.add(item_key)
                            price_str = f"${price:.2f}" if price is not None else "No price"
                            logger.info(f"  ✅ Extracted: {item_name} ({price_str})")
                    
                    # Also check for sub-items under this item
                    i += 1
                    while i < len(lines):
                        next_line = lines[i]
                        next_stripped = next_line.strip()
                        next_indent = len(next_line) - len(next_line.lstrip())
                        
                        if next_indent > indent_level and next_stripped:
                            if not self._is_modifier(next_stripped):
                                sub_item_name = self._clean_sub_item_name(next_stripped)
                                
                                # Validate price before adding sub-item
                                if price and price > 0 and sub_item_name and self.is_likely_food_item(sub_item_name):
                                    item_key = f"{sub_item_name}_{price}_sub"
                                    if item_key not in seen_items:
                                        items.append({
                                            'name': sub_item_name,
                                            'quantity': 1,
                                            'price': price,
                                            'unit_price': price,
                                            'original_line': next_line
                                        })
                                        seen_items.add(item_key)
                                        price_str = f"${price:.2f}" if price is not None else "No price"
                                        logger.info(f"  ✅ Extracted sub-item: {sub_item_name} ({price_str})")
                            i += 1
                        else:
                            break
                    continue
            
            i += 1
        
        # Return items if we found any
        return items if items else []
    
    def _clean_sub_item_name(self, text: str) -> str:
        """Clean sub-item name by removing quantity markers."""
        # Remove leading quantity like "1 " or "2 "
        cleaned = re.sub(r'^\d+\s+', '', text)
        return self.clean_item_name(cleaned)
    
    def _compute_unit_price(self, price: Optional[float], quantity: Optional[float]) -> Optional[float]:
        """Safely compute unit price while handling missing data."""
        if price is None:
            return None
        if not quantity or quantity <= 0:
            return price
        try:
            return price / quantity
        except Exception:
            logger.debug("  ⚠️ Could not compute unit price", exc_info=True)
            return price

    def _is_modifier(self, text: str) -> bool:
        """Check if text is a modifier (ADD, NO, EXTRA, etc.)."""
        modifiers = ['add', 'no', 'extra', 'hold', 'without', 'with', 'side']
        text_lower = text.lower()
        
        # Check if starts with modifier
        for mod in modifiers:
            if text_lower.startswith(mod + ' ') or text_lower == mod:
                return True
        
        return False
    
    def _extract_price_only(self, line: str) -> float:
        """Extract just the price from a line."""
        match = re.search(r'\$?(\d+\.\d{2})', line)
        if match:
            return float(match.group(1))
        return 0.0
    
    def parse_receipt(self, ocr_text: str) -> Dict[str, Any]:
        """
        Parse complete receipt including items, totals, date, and merchant.
        
        Args:
            ocr_text: Raw OCR text from receipt
            
        Returns:
            Dictionary with items, total, date, merchant_name, and other fields
        """
        result = {
            'items': [],
            'total': 0.0,
            'subtotal': 0.0,
            'tax': 0.0,
            'date': None,
            'merchant_name': None,
            'raw_text': ocr_text
        }
        
        if not ocr_text:
            return result
        
        lines = ocr_text.split('\n')
        
        # Extract items
        result['items'] = self.parse_receipt_items(ocr_text)
        
        # Extract merchant name (usually first 1-3 lines)
        result['merchant_name'] = self._extract_merchant_name(lines)
        
        # Extract date
        result['date'] = self._extract_date(ocr_text)
        
        # Extract totals
        totals = self._extract_totals(lines)
        result.update(totals)
        
        return result
    
    def _extract_merchant_name(self, lines: List[str]) -> Optional[str]:
        """Extract merchant/store name from first few lines."""
        # Check first 5 lines for merchant name
        for line in lines[:5]:
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 3:
                continue
            
            # Skip if it's just numbers or special chars
            if re.match(r'^[\d\s\-\.\(\)]+$', line_clean):
                continue
            
            # Skip common non-merchant patterns
            if any(word in line_clean.lower() for word in ['invoice', 'receipt', 'bill', 'phone', 'tel', 'address']):
                continue
            
            # If it's mostly uppercase and not too long, likely merchant name
            if line_clean.isupper() and len(line_clean) <= 40:
                return line_clean
            
            # If it contains common business words
            if any(word in line_clean.lower() for word in ['restaurant', 'market', 'shop', 'store', 'cafe', 'foods']):
                return line_clean
            
            # First non-empty line that looks like text
            if len(line_clean) > 5 and not line_clean[0].isdigit():
                return line_clean
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from receipt text and normalize to YYYY-MM-DD format."""
        import datetime
        
        # Common date patterns
        date_patterns = [
            # MM/DD/YYYY or MM/DD/YY
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', 'mdy'),
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})', 'mdy_short'),
            
            # DD/MM/YYYY or DD/MM/YY
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', 'dmy'),
            
            # YYYY-MM-DD
            (r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', 'ymd'),
            
            # Month DD, YYYY
            (r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})', 'mdy_text'),
            
            # DD Month YYYY
            (r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})', 'dmy_text'),
            
            # Date: May 11, 2019
            (r'Date:\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})', 'date_prefix'),
        ]
        
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        for pattern, format_type in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if format_type == 'ymd':
                        year, month, day = match.groups()
                        return f"{year}-{int(month):02d}-{int(day):02d}"
                    
                    elif format_type in ['mdy', 'dmy']:
                        part1, part2, year = match.groups()
                        year = int(year)
                        
                        # Heuristic: if first number > 12, it's likely day
                        if int(part1) > 12:
                            day, month = int(part1), int(part2)
                        elif int(part2) > 12:
                            month, day = int(part1), int(part2)
                        else:
                            # Ambiguous, assume MM/DD by default (US format)
                            month, day = int(part1), int(part2)
                        
                        return f"{year}-{month:02d}-{day:02d}"
                    
                    elif format_type == 'mdy_short':
                        month, day, year = match.groups()
                        year = int(year)
                        if year < 100:
                            year = 2000 + year if year < 50 else 1900 + year
                        return f"{year}-{int(month):02d}-{int(day):02d}"
                    
                    elif format_type == 'mdy_text':
                        month_str, day, year = match.groups()
                        month = month_map[month_str.lower()[:3]]
                        return f"{year}-{month:02d}-{int(day):02d}"
                    
                    elif format_type == 'dmy_text':
                        day, month_str, year = match.groups()
                        month = month_map[month_str.lower()[:3]]
                        return f"{year}-{month:02d}-{int(day):02d}"
                    
                    elif format_type == 'date_prefix':
                        month_str, day, year = match.groups()
                        month = month_map[month_str.lower()[:3]]
                        return f"{year}-{month:02d}-{int(day):02d}"
                
                except (ValueError, KeyError) as e:
                    logger.debug(f"Date parsing error: {e}")
                    continue
        
        return None
    
    def _extract_totals(self, lines: List[str]) -> Dict[str, float]:
        """Extract total, subtotal, and tax from receipt."""
        result = {
            'total': 0.0,
            'subtotal': 0.0,
            'tax': 0.0
        }
        
        # Look through lines for total keywords
        for line in lines:
            line_lower = line.lower()
            
            # Extract amounts (handle commas in numbers)
            # Match patterns like: $1,234.56, 1,234.56, $123.45, 123.45, 123.4, etc.
            amounts = re.findall(r'\$?\s*([\d,]+\.?\d*)', line)
            if not amounts:
                continue
            
            # Parse amounts (remove commas)
            parsed_amounts = []
            for amt in amounts:
                try:
                    parsed_amounts.append(float(amt.replace(',', '')))
                except ValueError:
                    continue
            
            if not parsed_amounts:
                continue
            
            # Get the last (rightmost) amount
            amount = parsed_amounts[-1]
            
            # Check for total
            if any(keyword in line_lower for keyword in ['total', 'amount due', 'balance due']):
                # Avoid "item total" or "sub total"
                if 'sub' not in line_lower and 'item' not in line_lower:
                    result['total'] = max(result['total'], amount)
            
            # Check for subtotal
            if any(keyword in line_lower for keyword in ['subtotal', 'sub-total', 'sub total', 'item total']):
                result['subtotal'] = max(result['subtotal'], amount)
            
            # Check for tax
            if any(keyword in line_lower for keyword in ['tax', 'gst', 'hst', 'vat', 'pst']):
                result['tax'] += amount
        
        # If no explicit subtotal found but we have items and total, estimate subtotal
        if result['subtotal'] == 0.0 and result['total'] > 0.0:
            result['subtotal'] = result['total'] - result['tax']
        
        return result


# Global instance
receipt_parser = IntelligentReceiptParser()
