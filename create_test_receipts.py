"""
Create sample receipt images for testing OCR
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_receipt_image(filename, store_name, items, total):
    """
    Create a simple receipt image for testing.
    
    Args:
        filename: Output filename
        store_name: Name of the store
        items: List of (name, price) tuples
        total: Total amount
    """
    # Create image
    width = 400
    height = 100 + len(items) * 30 + 100
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use default font
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        font_large = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
        font_large = ImageFont.load_default()
    
    # Draw receipt content
    y = 20
    
    # Store name
    draw.text((width//2 - 50, y), store_name, fill='black', font=font_large)
    y += 40
    
    # Date
    draw.text((width//2 - 60, y), "Date: 01/15/2024", fill='black', font=font)
    y += 30
    
    # Line separator
    draw.line([(20, y), (width-20, y)], fill='black', width=2)
    y += 20
    
    # Items
    for item_name, price in items:
        draw.text((30, y), item_name, fill='black', font=font)
        draw.text((width-100, y), f"${price:.2f}", fill='black', font=font)
        y += 30
    
    # Line separator
    draw.line([(20, y), (width-20, y)], fill='black', width=2)
    y += 20
    
    # Total
    draw.text((30, y), "TOTAL:", fill='black', font=font_large)
    draw.text((width-100, y), f"${total:.2f}", fill='black', font=font_large)
    
    # Save image
    img.save(filename)
    print(f"✅ Created receipt: {filename}")


# Create McDonald's receipt
create_receipt_image(
    "test_mcdonalds_sample.png",
    "McDonald's",
    [
        ("2 Burritos", 6.98),
        ("M Iced Coffee", 2.49),
        ("Hash Browns", 1.99),
        ("Chicken Nuggets", 4.99),
        ("Large Fries", 2.99),
        ("Cola", 1.99)
    ],
    21.43
)

# Create grocery receipt
create_receipt_image(
    "test_grocery_sample.png",
    "Fresh Market",
    [
        ("Apples 2 lb", 4.98),
        ("Bananas 1 bunch", 2.49),
        ("Milk 1 gal", 3.99),
        ("Bread", 2.49),
        ("Eggs 1 doz", 3.99),
        ("Chicken Breast", 8.99),
        ("Tomatoes", 2.99),
        ("Lettuce", 1.99),
        ("Cheese", 5.99),
        ("Orange Juice", 4.49)
    ],
    42.39
)

# Create restaurant receipt
create_receipt_image(
    "test_restaurant_sample.png",
    "Luigi's Restaurant",
    [
        ("Pasta Carbonara", 14.99),
        ("Caesar Salad", 8.99),
        ("Garlic Bread", 4.99),
        ("Tiramisu", 6.99),
        ("Coffee", 2.99)
    ],
    38.95
)

print("\n✅ All test receipts created!")
print("\nYou can now test with:")
print("  python test_tesseract_comparison.py")
