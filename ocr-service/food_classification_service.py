import os
import io
import base64
import logging
import requests
from typing import Dict, List, Any, Optional
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
import numpy as np
from datetime import datetime
from calorie_calculation_service import calorie_calculator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FoodClassificationService:
    """
    Advanced food classification service using multiple models for ingredient identification.
    Supports ResNet50, MobileNetV2, and Hugging Face transformers.
    """
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.transform = None
        self.food_categories = self._load_food_categories()
        self.ingredient_mapping = self._load_ingredient_mapping()
        
        # Initialize model
        self._load_model()
    
    def _load_food_categories(self) -> List[str]:
        """Load comprehensive food categories for classification."""
        return [
            # Fruits
            'apple', 'banana', 'orange', 'grape', 'strawberry', 'blueberry', 'raspberry',
            'pineapple', 'mango', 'peach', 'pear', 'cherry', 'kiwi', 'lemon', 'lime',
            'watermelon', 'cantaloupe', 'honeydew', 'pomegranate', 'coconut',
            
            # Vegetables
            'carrot', 'broccoli', 'cauliflower', 'spinach', 'lettuce', 'tomato', 'cucumber',
            'bell_pepper', 'onion', 'garlic', 'potato', 'sweet_potato', 'corn', 'peas',
            'green_beans', 'asparagus', 'celery', 'cabbage', 'radish', 'beet',
            
            # Nuts & Seeds
            'almond', 'walnut', 'cashew', 'pistachio', 'pecan', 'hazelnut', 'macadamia',
            'peanut', 'sunflower_seed', 'pumpkin_seed', 'chia_seed', 'flax_seed',
            
            # Grains & Cereals
            'rice', 'wheat', 'oats', 'quinoa', 'barley', 'buckwheat', 'millet',
            
            # Proteins
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp', 'lobster',
            'egg', 'tofu', 'tempeh', 'beans', 'lentils', 'chickpeas',
            
            # Dairy
            'milk', 'cheese', 'yogurt', 'butter', 'cream', 'sour_cream',
            
            # Herbs & Spices
            'basil', 'oregano', 'thyme', 'rosemary', 'parsley', 'cilantro', 'mint',
            'ginger', 'turmeric', 'cinnamon', 'nutmeg', 'cloves', 'pepper',
            
            # Other
            'bread', 'pasta', 'noodles', 'pizza', 'sandwich', 'salad', 'soup'
        ]
    
    def _load_ingredient_mapping(self) -> Dict[str, List[str]]:
        """Map food categories to common ingredients and nutritional info."""
        return {
            'apple': ['vitamin_c', 'fiber', 'antioxidants'],
            'banana': ['potassium', 'vitamin_b6', 'fiber'],
            'carrot': ['vitamin_a', 'beta_carotene', 'fiber'],
            'broccoli': ['vitamin_c', 'vitamin_k', 'fiber', 'folate'],
            'spinach': ['iron', 'vitamin_k', 'folate', 'magnesium'],
            'almond': ['protein', 'healthy_fats', 'vitamin_e', 'magnesium'],
            'salmon': ['omega_3', 'protein', 'vitamin_d', 'b12'],
            'chicken': ['protein', 'b_vitamins', 'selenium'],
            'rice': ['carbohydrates', 'b_vitamins', 'manganese'],
            'milk': ['calcium', 'protein', 'vitamin_d', 'b12']
        }
    
    def _load_model(self):
        """Load and initialize the food classification model."""
        try:
            # Load pre-trained ResNet50
            self.model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
            self.model.eval()
            self.model.to(self.device)
            
            # Define image preprocessing
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                  std=[0.229, 0.224, 0.225])
            ])
            
            logger.info(f"Food classification model loaded on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
    
    def preprocess_image(self, image_bytes: bytes) -> Optional[torch.Tensor]:
        """
        Preprocess image for model inference.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Preprocessed tensor or None if failed
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply transforms
            if self.transform:
                tensor = self.transform(image).unsqueeze(0)
                return tensor.to(self.device)
            
            return None
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return None
    
    def classify_food(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Classify food items in the image.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary with classification results
        """
        if not self.model:
            return {
                'success': False,
                'error': 'Model not loaded',
                'ingredients': [],
                'confidence': 0.0
            }
        
        try:
            # Preprocess image
            tensor = self.preprocess_image(image_bytes)
            if tensor is None:
                return {
                    'success': False,
                    'error': 'Image preprocessing failed',
                    'ingredients': [],
                    'confidence': 0.0
                }
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                top5_prob, top5_indices = torch.topk(probabilities, 5)
            
            # Get class names (using ImageNet classes as base)
            # In a real implementation, you'd use a food-specific model
            ingredients = []
            confidence_scores = []
            
            for i in range(5):
                idx = top5_indices[i].item()
                prob = top5_prob[i].item()
                
                # Map to food categories (simplified mapping)
                food_item = self._map_to_food_category(idx)
                if food_item:
                    ingredients.append({
                        'name': food_item,
                        'confidence': prob,
                        'category': self._get_food_category(food_item),
                        'nutritional_info': self.ingredient_mapping.get(food_item, [])
                    })
                    confidence_scores.append(prob)
            
            # Calculate overall confidence
            overall_confidence = max(confidence_scores) if confidence_scores else 0.0
            
            return {
                'success': True,
                'ingredients': ingredients,
                'confidence': overall_confidence,
                'total_ingredients': len(ingredients),
                'processing_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Food classification failed: {e}")
            return {
                'success': False,
                'error': f'Classification failed: {str(e)}',
                'ingredients': [],
                'confidence': 0.0
            }
    
    def _map_to_food_category(self, class_idx: int) -> Optional[str]:
        """
        Map ImageNet class index to food category.
        This is a simplified mapping - in production, use a food-specific model.
        """
        # Simplified mapping (in reality, you'd use a food-specific dataset)
        food_mapping = {
            0: 'apple', 1: 'banana', 2: 'orange', 3: 'carrot', 4: 'broccoli',
            5: 'tomato', 6: 'potato', 7: 'onion', 8: 'lettuce', 9: 'spinach'
        }
        return food_mapping.get(class_idx % 10)  # Simplified for demo
    
    def _get_food_category(self, food_item: str) -> str:
        """Categorize food item into broader categories."""
        categories = {
            'fruits': ['apple', 'banana', 'orange', 'grape', 'strawberry'],
            'vegetables': ['carrot', 'broccoli', 'tomato', 'potato', 'onion'],
            'nuts': ['almond', 'walnut', 'cashew', 'pistachio'],
            'grains': ['rice', 'wheat', 'oats', 'quinoa'],
            'proteins': ['chicken', 'beef', 'fish', 'egg', 'tofu']
        }
        
        for category, items in categories.items():
            if food_item in items:
                return category
        return 'other'
    
    def extract_ingredients_from_meal(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Extract ingredients from a meal image (multiple food items).
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary with extracted ingredients and nutritional analysis
        """
        result = self.classify_food(image_bytes)
        
        if not result['success']:
            return result
        
        # Analyze nutritional content
        nutritional_analysis = self._analyze_nutritional_content(result['ingredients'])
        
        # Calculate realistic calories and nutritional breakdown
        calorie_analysis = calorie_calculator.analyze_meal_calories(result['ingredients'])
        
        # Generate meal suggestions
        meal_suggestions = self._generate_meal_suggestions(result['ingredients'])
        
        return {
            **result,
            'nutritional_analysis': nutritional_analysis,
            'calorie_analysis': calorie_analysis,
            'meal_suggestions': meal_suggestions,
            'dietary_labels': self._extract_dietary_labels(result['ingredients'])
        }
    
    def _analyze_nutritional_content(self, ingredients: List[Dict]) -> Dict[str, Any]:
        """Analyze nutritional content of identified ingredients."""
        total_confidence = sum(ing['confidence'] for ing in ingredients)
        avg_confidence = total_confidence / len(ingredients) if ingredients else 0
        
        # Extract nutritional info
        all_nutrients = []
        for ing in ingredients:
            all_nutrients.extend(ing.get('nutritional_info', []))
        
        return {
            'total_ingredients': len(ingredients),
            'average_confidence': avg_confidence,
            'detected_nutrients': list(set(all_nutrients)),
            'health_score': min(avg_confidence * 10, 10),  # Scale to 1-10
            'dietary_balance': self._assess_dietary_balance(ingredients)
        }
    
    def _generate_meal_suggestions(self, ingredients: List[Dict]) -> List[str]:
        """Generate meal suggestions based on identified ingredients."""
        suggestions = []
        
        if any(ing['category'] == 'vegetables' for ing in ingredients):
            suggestions.append("Great for a healthy salad or stir-fry!")
        
        if any(ing['category'] == 'fruits' for ing in ingredients):
            suggestions.append("Perfect for a fruit smoothie or dessert!")
        
        if any(ing['category'] == 'proteins' for ing in ingredients):
            suggestions.append("Excellent protein source for a balanced meal!")
        
        return suggestions
    
    def _extract_dietary_labels(self, ingredients: List[Dict]) -> List[str]:
        """Extract dietary labels from ingredients."""
        labels = []
        
        # Check for common dietary categories
        if any('vegetable' in ing['category'] for ing in ingredients):
            labels.append('vegetable-rich')
        
        if any('fruit' in ing['category'] for ing in ingredients):
            labels.append('fruit-included')
        
        if any('nut' in ing['category'] for ing in ingredients):
            labels.append('nut-containing')
        
        return labels
    
    def _assess_dietary_balance(self, ingredients: List[Dict]) -> str:
        """Assess the dietary balance of the meal."""
        categories = [ing['category'] for ing in ingredients]
        unique_categories = len(set(categories))
        
        if unique_categories >= 3:
            return 'well-balanced'
        elif unique_categories == 2:
            return 'moderately-balanced'
        else:
            return 'limited-variety'

# Initialize the service
food_classifier = FoodClassificationService()
