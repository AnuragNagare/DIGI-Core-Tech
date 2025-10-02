import os
import io
import logging
from dataclasses import asdict
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import torch
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TRANSFORMERS_NO_FLAX"] = "1"

from transformers import CLIPModel, CLIPProcessor
from datetime import datetime
from calorie_calculation_service import calorie_calculator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FoodClassificationService:
    """
    Advanced food classification service using multiple models for ingredient identification.
    Supports CLIP-based zero-shot recognition with rich nutritional mappings.
    """
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.clip_model: Optional[CLIPModel] = None
        self.clip_processor: Optional[CLIPProcessor] = None
        self.text_prompts: List[str] = []
        self.prompt_metadata: List[Dict[str, str]] = []
        self.text_prompt_embeddings: Optional[torch.Tensor] = None
        self.canonical_to_indices: Dict[str, List[int]] = {}
        self.temperature: float = float(os.getenv('FOOD_CLIP_SOFTMAX_TEMP', '0.07'))
        self.food_categories = self._load_food_categories()
        self.ingredient_mapping = self._load_ingredient_mapping()
        self.food_profiles = self._build_food_profiles()
        
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
        """Load and initialize the CLIP-based food classification model."""
        # Use smaller/base CLIP model to reduce memory requirements
        model_name = os.getenv('FOOD_CLIP_MODEL', 'openai/clip-vit-base-patch32')
        try:
            self.clip_model = CLIPModel.from_pretrained(model_name)
            self.clip_processor = CLIPProcessor.from_pretrained(model_name)
            self.clip_model.to(self.device)
            self.clip_model.eval()

            self.text_prompts, self.prompt_metadata = self._build_text_prompts()
            text_inputs = self.clip_processor(
                text=self.text_prompts,
                padding=True,
                return_tensors='pt'
            )
            text_inputs = {key: value.to(self.device) for key, value in text_inputs.items()}

            with torch.no_grad():
                text_embeddings = self.clip_model.get_text_features(**text_inputs)

            text_embeddings = text_embeddings / text_embeddings.norm(p=2, dim=-1, keepdim=True)
            self.text_prompt_embeddings = text_embeddings
            self.canonical_to_indices.clear()

            for idx, meta in enumerate(self.prompt_metadata):
                canonical = meta['canonical_name']
                if canonical not in self.canonical_to_indices:
                    self.canonical_to_indices[canonical] = []
                self.canonical_to_indices[canonical].append(idx)

            logger.info(
                "Food classification CLIP model '%s' loaded on %s with %d prompts",
                model_name,
                self.device,
                len(self.text_prompts)
            )

        except Exception as e:
            logger.error(f"Failed to load CLIP model '{model_name}': {e}")
            self.clip_model = None
            self.clip_processor = None
            self.text_prompt_embeddings = None
            self.canonical_to_indices.clear()
    
    def preprocess_image(self, image_bytes: bytes) -> Optional[Image.Image]:
        """
        Decode image bytes into a PIL image.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            PIL Image or None if failed
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
            
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
        if not self.clip_model or not self.clip_processor or self.text_prompt_embeddings is None:
            return {
                'success': False,
                'error': 'Model not loaded',
                'ingredients': [],
                'confidence': 0.0
            }
        
        try:
            # Preprocess image
            image = self.preprocess_image(image_bytes)
            if image is None:
                return {
                    'success': False,
                    'error': 'Image preprocessing failed',
                    'ingredients': [],
                    'confidence': 0.0
                }
            
            predictions = self._predict_with_clip(image, top_k=5)
            ingredients: List[Dict[str, Any]] = []
            confidence_scores: List[float] = []

            for prediction in predictions:
                canonical_name = prediction['canonical_name']
                normalized = self._normalize_prediction(canonical_name)
                if not normalized:
                    continue

                probability = float(prediction['probability'])
                portion_estimate = calorie_calculator.estimate_portion_size(canonical_name, probability)
                nutrition_snapshot = self._get_nutrition_snapshot(canonical_name)

                ingredient_entry = {
                    'name': canonical_name,
                    'display_name': normalized['display_name'],
                    'raw_prediction_label': canonical_name,
                    'matched_keyword': prediction.get('matched_synonym', normalized['matched_keyword']),
                    'confidence': round(probability, 4),
                    'confidence_percent': round(probability * 100, 1),
                    'clip_score': round(float(prediction['score']), 4),
                    'prompt_used': prediction.get('prompt'),
                    'category': normalized['category'],
                    'nutritional_info': normalized['key_nutrients'],
                    'nutrition_summary': nutrition_snapshot,
                    'portion_override_g': round(portion_estimate, 1) if portion_estimate else None,
                    'component_ingredients': normalized['ingredients']
                }
                ingredients.append(ingredient_entry)
                confidence_scores.append(probability)
            
            # Calculate overall confidence
            overall_confidence = confidence_scores[0] if confidence_scores else 0.0
            
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

    def _normalize_prediction(self, raw_label: str) -> Optional[Dict[str, Any]]:
        """Normalize ImageNet raw label into a canonical food profile."""
        label = raw_label.lower().replace('_', ' ').replace('-', ' ')
        label = ''.join(ch for ch in label if ch.isalnum() or ch.isspace()).strip()
        
        for canonical_name, profile in self.food_profiles.items():
            for keyword in profile['synonyms']:
                if keyword in label:
                    return {
                        'canonical_name': canonical_name,
                        'display_name': profile.get('display_name', canonical_name.replace('_', ' ').title()),
                        'category': profile['category'],
                        'key_nutrients': profile.get('key_nutrients', []),
                        'ingredients': profile.get('ingredients', [canonical_name]),
                        'matched_keyword': keyword
                    }
        
        # If label already matches a canonical name
        canonical_candidate = label.replace(' ', '_')
        if canonical_candidate in self.food_profiles:
            profile = self.food_profiles[canonical_candidate]
            return {
                'canonical_name': canonical_candidate,
                'display_name': profile.get('display_name', canonical_candidate.replace('_', ' ').title()),
                'category': profile['category'],
                'key_nutrients': profile.get('key_nutrients', []),
                'ingredients': profile.get('ingredients', [canonical_candidate]),
                'matched_keyword': canonical_candidate
            }
        
        return None

    def _build_text_prompts(self) -> Tuple[List[str], List[Dict[str, str]]]:
        """Generate descriptive prompts for each food profile."""
        prompts: List[str] = []
        metadata: List[Dict[str, str]] = []
        base_templates = [
            "a high quality food photograph of {}",
            "a close-up photo of {}",
            "a plate of {}",
            "{} on a dining table"
        ]

        for canonical_name, profile in self.food_profiles.items():
            synonyms = profile.get('synonyms', [])
            normalized_synonyms = set()
            for synonym in synonyms:
                normalized_synonyms.add(synonym)
                normalized_synonyms.add(synonym + 's')
            normalized_synonyms.add(canonical_name.replace('_', ' '))

            for synonym in sorted(normalized_synonyms):
                cleaned_synonym = synonym.strip()
                if not cleaned_synonym:
                    continue
                for template in base_templates:
                    prompt = template.format(cleaned_synonym)
                    prompts.append(prompt)
                    metadata.append({
                        'canonical_name': canonical_name,
                        'synonym': cleaned_synonym,
                        'template': template
                    })

        return prompts, metadata

    def _predict_with_clip(self, image: Image.Image, top_k: int = 5) -> List[Dict[str, Any]]:
        """Run CLIP inference and return top-k canonical predictions."""
        if (
            not self.clip_model
            or not self.clip_processor
            or self.text_prompt_embeddings is None
            or not self.canonical_to_indices
        ):
            return []

        image_inputs = self.clip_processor(images=image, return_tensors='pt')
        image_inputs = {key: value.to(self.device) for key, value in image_inputs.items()}

        with torch.no_grad():
            image_features = self.clip_model.get_image_features(**image_inputs)

        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
        similarity_scores = image_features @ self.text_prompt_embeddings.T
        similarity_scores = similarity_scores.squeeze(0)

        canonical_candidates: List[Dict[str, Any]] = []
        canonical_score_tensors: List[torch.Tensor] = []

        for canonical_name, indices in self.canonical_to_indices.items():
            prompt_scores = similarity_scores[indices]
            max_score, best_local_idx = torch.max(prompt_scores, dim=0)
            best_prompt_index = indices[best_local_idx.item()]
            canonical_candidates.append({
                'canonical_name': canonical_name,
                'score': max_score.detach().cpu().item(),
                'score_tensor': max_score,
                'best_prompt_index': best_prompt_index
            })
            canonical_score_tensors.append(max_score)

        if not canonical_candidates:
            return []

        stacked_scores = torch.stack(canonical_score_tensors)
        probabilities = torch.nn.functional.softmax(stacked_scores / self.temperature, dim=0)

        for candidate, probability in zip(canonical_candidates, probabilities):
            prompt_index = candidate['best_prompt_index']
            candidate['probability'] = probability.detach().cpu().item()
            candidate['matched_synonym'] = self.prompt_metadata[prompt_index]['synonym']
            candidate['prompt'] = self.text_prompts[prompt_index]

        canonical_candidates.sort(key=lambda item: item['probability'], reverse=True)
        top_candidates = canonical_candidates[:top_k]

        top_score_tensors = torch.stack([cand['score_tensor'] for cand in top_candidates])
        top_probabilities = torch.nn.functional.softmax(top_score_tensors / self.temperature, dim=0)

        for candidate, probability in zip(top_candidates, top_probabilities):
            candidate['probability'] = probability.detach().cpu().item()

        for candidate in top_candidates:
            candidate.pop('score_tensor', None)

        return top_candidates

    def _get_nutrition_snapshot(self, canonical_name: str) -> Optional[Dict[str, Any]]:
        """Return structured nutritional information for a canonical food name."""
        nutrient_entry = calorie_calculator.nutritional_database.get(canonical_name)
        if not nutrient_entry:
            return None
        nutrition_dict = asdict(nutrient_entry)
        # Rename keys for clarity
        return {
            'calories_per_100g': nutrition_dict.get('calories_per_100g'),
            'protein_per_100g': nutrition_dict.get('protein_per_100g'),
            'carbs_per_100g': nutrition_dict.get('carbs_per_100g'),
            'fat_per_100g': nutrition_dict.get('fat_per_100g'),
            'fiber_per_100g': nutrition_dict.get('fiber_per_100g'),
            'typical_portion_size_g': nutrition_dict.get('typical_portion_size'),
            'portion_description': nutrition_dict.get('portion_description'),
            'micronutrients': {
                'sugar_per_100g': nutrition_dict.get('sugar_per_100g'),
                'sodium_per_100g': nutrition_dict.get('sodium_per_100g'),
                'potassium_per_100g': nutrition_dict.get('potassium_per_100g'),
                'vitamin_c_per_100g': nutrition_dict.get('vitamin_c_per_100g'),
                'vitamin_a_per_100g': nutrition_dict.get('vitamin_a_per_100g'),
                'calcium_per_100g': nutrition_dict.get('calcium_per_100g'),
                'iron_per_100g': nutrition_dict.get('iron_per_100g')
            }
        }
    
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

    def _build_food_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Define canonical food profiles with synonyms and nutritional highlights."""
        return {
            'apple': {
                'display_name': 'Apple',
                'category': 'fruits',
                'synonyms': ['apple', 'granny smith', 'gala apple', 'fuji apple'],
                'key_nutrients': ['vitamin C', 'fiber', 'antioxidants']
            },
            'banana': {
                'display_name': 'Banana',
                'category': 'fruits',
                'synonyms': ['banana', 'bananas', 'ripe banana', 'yellow banana', 'peeled banana', 'bunch of bananas', 'plantain', 'green banana', 'unripe banana'],
                'key_nutrients': ['potassium', 'vitamin B6', 'fiber']
            },
            'orange': {
                'display_name': 'Orange',
                'category': 'fruits',
                'synonyms': ['orange', 'navel orange', 'blood orange'],
                'key_nutrients': ['vitamin C', 'fiber', 'folate']
            },
            'grape': {
                'display_name': 'Grapes',
                'category': 'fruits',
                'synonyms': ['grape', 'bunch of grapes'],
                'key_nutrients': ['antioxidants', 'vitamin K', 'manganese']
            },
            'strawberry': {
                'display_name': 'Strawberries',
                'category': 'fruits',
                'synonyms': ['strawberry', 'strawberries'],
                'key_nutrients': ['vitamin C', 'manganese', 'antioxidants']
            },
            'blueberry': {
                'display_name': 'Blueberries',
                'category': 'fruits',
                'synonyms': ['blueberry', 'blueberries'],
                'key_nutrients': ['antioxidants', 'vitamin C', 'fiber']
            },
            'pineapple': {
                'display_name': 'Pineapple',
                'category': 'fruits',
                'synonyms': ['pineapple'],
                'key_nutrients': ['vitamin C', 'manganese', 'bromelain']
            },
            'mango': {
                'display_name': 'Mango',
                'category': 'fruits',
                'synonyms': ['mango'],
                'key_nutrients': ['vitamin C', 'vitamin A', 'fiber']
            },
            'peach': {
                'display_name': 'Peach',
                'category': 'fruits',
                'synonyms': ['peach', 'nectarine'],
                'key_nutrients': ['vitamin C', 'vitamin A', 'fiber']
            },
            'pear': {
                'display_name': 'Pear',
                'category': 'fruits',
                'synonyms': ['pear', 'bartlett pear'],
                'key_nutrients': ['fiber', 'vitamin C', 'copper']
            },
            'carrot': {
                'display_name': 'Carrot',
                'category': 'vegetables',
                'synonyms': ['carrot', 'baby carrot'],
                'key_nutrients': ['beta-carotene', 'vitamin A', 'fiber']
            },
            'broccoli': {
                'display_name': 'Broccoli',
                'category': 'vegetables',
                'synonyms': ['broccoli', 'broccoli florets', 'head of broccoli', 'steamed broccoli'],
                'key_nutrients': ['vitamin C', 'vitamin K', 'fiber']
            },
            'tomato': {
                'display_name': 'Tomato',
                'category': 'vegetables',
                'synonyms': ['tomato', 'roma tomato', 'cherry tomato'],
                'key_nutrients': ['lycopene', 'vitamin C', 'potassium']
            },
            'potato': {
                'display_name': 'Potato',
                'category': 'vegetables',
                'synonyms': ['potato', 'baked potato', 'russet'],
                'key_nutrients': ['potassium', 'vitamin C', 'fiber']
            },
            'onion': {
                'display_name': 'Onion',
                'category': 'vegetables',
                'synonyms': ['onion', 'red onion', 'white onion'],
                'key_nutrients': ['antioxidants', 'vitamin C', 'fiber']
            },
            'lettuce': {
                'display_name': 'Lettuce',
                'category': 'vegetables',
                'synonyms': ['lettuce', 'romaine', 'iceberg', 'salad greens'],
                'key_nutrients': ['vitamin K', 'folate', 'fiber']
            },
            'spinach': {
                'display_name': 'Spinach',
                'category': 'vegetables',
                'synonyms': ['spinach', 'baby spinach'],
                'key_nutrients': ['iron', 'vitamin K', 'folate']
            },
            'cucumber': {
                'display_name': 'Cucumber',
                'category': 'vegetables',
                'synonyms': ['cucumber'],
                'key_nutrients': ['hydration', 'vitamin K', 'potassium']
            },
            'bell_pepper': {
                'display_name': 'Bell Pepper',
                'category': 'vegetables',
                'synonyms': ['bell pepper', 'red pepper', 'green pepper', 'yellow pepper'],
                'key_nutrients': ['vitamin C', 'vitamin A', 'fiber']
            },
            'corn': {
                'display_name': 'Corn',
                'category': 'grains',
                'synonyms': ['corn', 'maize', 'corn on the cob'],
                'key_nutrients': ['carbohydrates', 'fiber', 'b vitamins']
            },
            'almond': {
                'display_name': 'Almonds',
                'category': 'nuts',
                'synonyms': ['almond', 'almonds'],
                'key_nutrients': ['healthy fats', 'vitamin E', 'magnesium']
            },
            'walnut': {
                'display_name': 'Walnuts',
                'category': 'nuts',
                'synonyms': ['walnut', 'walnuts'],
                'key_nutrients': ['omega-3 fats', 'antioxidants', 'magnesium']
            },
            'cashew': {
                'display_name': 'Cashews',
                'category': 'nuts',
                'synonyms': ['cashew', 'cashews'],
                'key_nutrients': ['healthy fats', 'copper', 'magnesium']
            },
            'pistachio': {
                'display_name': 'Pistachios',
                'category': 'nuts',
                'synonyms': ['pistachio', 'pistachios'],
                'key_nutrients': ['protein', 'fiber', 'vitamin B6']
            },
            'peanut': {
                'display_name': 'Peanuts',
                'category': 'nuts',
                'synonyms': ['peanut', 'peanuts'],
                'key_nutrients': ['protein', 'healthy fats', 'niacin']
            },
            'rice': {
                'display_name': 'Rice',
                'category': 'grains',
                'synonyms': ['rice', 'risotto', 'pilaf'],
                'key_nutrients': ['carbohydrates', 'manganese', 'b vitamins']
            },
            'oats': {
                'display_name': 'Oats',
                'category': 'grains',
                'synonyms': ['oats', 'oatmeal', 'porridge'],
                'key_nutrients': ['fiber', 'protein', 'iron']
            },
            'quinoa': {
                'display_name': 'Quinoa',
                'category': 'grains',
                'synonyms': ['quinoa'],
                'key_nutrients': ['complete protein', 'fiber', 'magnesium']
            },
            'bread': {
                'display_name': 'Bread',
                'category': 'grains',
                'synonyms': ['bread', 'toast', 'baguette', 'bagel'],
                'key_nutrients': ['carbohydrates', 'fiber', 'b vitamins']
            },
            'pasta': {
                'display_name': 'Pasta',
                'category': 'grains',
                'synonyms': ['pasta', 'spaghetti', 'penne', 'macaroni', 'lasagna', 'fettuccine', 'noodle', 'noodles', 'linguine', 'tagliatelle'],
                'key_nutrients': ['carbohydrates', 'protein', 'b vitamins']
            },
            'pizza': {
                'display_name': 'Pizza',
                'category': 'meals',
                'synonyms': ['pizza', 'slice of pizza', 'pepperoni pizza', 'cheese pizza', 'margherita pizza', 'vegetable pizza'],
                'key_nutrients': ['carbohydrates', 'protein', 'calcium']
            },
            'salad': {
                'display_name': 'Salad',
                'category': 'vegetables',
                'synonyms': ['salad', 'green salad', 'garden salad', 'caesar salad', 'bowl of salad', 'veggie salad', 'mixed greens'],
                'key_nutrients': ['fiber', 'vitamin C', 'folate']
            },
            'chicken': {
                'display_name': 'Chicken',
                'category': 'proteins',
                'synonyms': ['chicken', 'roasted chicken', 'chicken breast'],
                'key_nutrients': ['lean protein', 'b vitamins', 'selenium']
            },
            'beef': {
                'display_name': 'Beef',
                'category': 'proteins',
                'synonyms': ['beef', 'steak', 'burger', 'hamburger'],
                'key_nutrients': ['protein', 'iron', 'vitamin B12']
            },
            'fish': {
                'display_name': 'Fish',
                'category': 'proteins',
                'synonyms': ['fish', 'cod', 'tilapia', 'trout'],
                'key_nutrients': ['lean protein', 'omega-3', 'vitamin D']
            },
            'salmon': {
                'display_name': 'Salmon',
                'category': 'proteins',
                'synonyms': ['salmon'],
                'key_nutrients': ['omega-3', 'protein', 'vitamin D']
            },
            'egg': {
                'display_name': 'Egg',
                'category': 'proteins',
                'synonyms': ['egg', 'omelet', 'omelette', 'scrambled egg'],
                'key_nutrients': ['protein', 'choline', 'vitamin D']
            },
            'tofu': {
                'display_name': 'Tofu',
                'category': 'proteins',
                'synonyms': ['tofu'],
                'key_nutrients': ['plant protein', 'calcium', 'iron']
            },
            'beans': {
                'display_name': 'Beans',
                'category': 'proteins',
                'synonyms': ['beans', 'lentil', 'lentils', 'chickpea', 'chickpeas'],
                'key_nutrients': ['plant protein', 'fiber', 'iron']
            },
            'milk': {
                'display_name': 'Milk',
                'category': 'dairy',
                'synonyms': ['milk'],
                'key_nutrients': ['calcium', 'protein', 'vitamin D']
            },
            'cheese': {
                'display_name': 'Cheese',
                'category': 'dairy',
                'synonyms': ['cheese', 'cheddar', 'mozzarella', 'parmesan'],
                'key_nutrients': ['protein', 'calcium', 'vitamin A']
            },
            'yogurt': {
                'display_name': 'Yogurt',
                'category': 'dairy',
                'synonyms': ['yogurt', 'yoghurt', 'greek yogurt'],
                'key_nutrients': ['probiotics', 'protein', 'calcium']
            },
            'butter': {
                'display_name': 'Butter',
                'category': 'dairy',
                'synonyms': ['butter'],
                'key_nutrients': ['fat', 'vitamin A', 'vitamin D']
            },
            'olive_oil': {
                'display_name': 'Olive Oil',
                'category': 'fats',
                'synonyms': ['olive oil', 'extra virgin olive oil'],
                'key_nutrients': ['healthy fats', 'antioxidants', 'vitamin E']
            }
        }

# Initialize the service
food_classifier = FoodClassificationService()
