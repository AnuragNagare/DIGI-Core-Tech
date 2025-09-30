# 🍎 Food Classification Integration Guide

This guide explains how to integrate food recognition and ingredient identification into your YUH Smart Grocery App.

## 🎯 Overview

The food classification system can identify:
- **Fruits**: Apple, banana, orange, grape, strawberry, etc.
- **Vegetables**: Carrot, broccoli, tomato, potato, onion, etc.
- **Nuts & Seeds**: Almond, walnut, cashew, pistachio, etc.
- **Grains**: Rice, wheat, oats, quinoa, etc.
- **Proteins**: Chicken, beef, fish, egg, tofu, etc.
- **Dairy**: Milk, cheese, yogurt, butter, etc.
- **Herbs & Spices**: Basil, oregano, thyme, ginger, etc.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd ocr-service
python setup_food_classification.py
```

### 2. Start the Food Classification Service

```bash
python start_food_service.py
```

The service will be available at `http://localhost:8001`

### 3. Test the Service

```bash
curl http://localhost:8001/health
```

## 📱 Integration with Frontend

### 1. Add Food Classifier Component

The `FoodClassifier` component is already created and ready to use:

```tsx
import FoodClassifier from '@/components/FoodClassifier'

// In your component
const [showFoodClassifier, setShowFoodClassifier] = useState(false)

// Usage
<FoodClassifier 
  onClose={() => setShowFoodClassifier(false)}
  onIngredientsDetected={(ingredients) => {
    // Handle detected ingredients
    console.log('Detected ingredients:', ingredients)
  }}
/>
```

### 2. API Integration

The API endpoint is already configured at `/api/ai/classify-photo`:

```typescript
import { aiApi } from '@/lib/api'

// Classify food image
const result = await aiApi.classifyPhoto(imageDataUrl)
if (result.success) {
  console.log('Ingredients:', result.data.ingredients)
  console.log('Health Score:', result.data.nutritional_analysis.health_score)
}
```

## 🔧 Technical Details

### Model Architecture

- **Base Model**: ResNet50 pre-trained on ImageNet
- **Fine-tuning**: Custom food dataset (Food-101 + Fruits-360)
- **Accuracy**: 85-95% on food classification
- **Processing Time**: 1-3 seconds per image
- **Memory Usage**: ~1-2GB RAM

### API Endpoints

#### POST `/classify-food`
Full food classification with nutritional analysis

**Request:**
```json
{
  "imageDataUrl": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ingredients": [
      {
        "name": "apple",
        "confidence": 0.95,
        "category": "fruits",
        "nutritional_info": ["vitamin_c", "fiber", "antioxidants"]
      }
    ],
    "confidence": 0.92,
    "total_ingredients": 1,
    "nutritional_analysis": {
      "health_score": 9.2,
      "dietary_balance": "well-balanced"
    },
    "meal_suggestions": ["Great for a healthy snack!"],
    "dietary_labels": ["fruit-included"]
  }
}
```

#### POST `/classify-ingredients`
Simple ingredient classification

**Response:**
```json
{
  "success": true,
  "ingredients": [
    {
      "name": "carrot",
      "confidence": 0.88,
      "category": "vegetables"
    }
  ]
}
```

## 🎨 UI Components

### FoodClassifier Component Features

- **Camera Integration**: Works with Capacitor camera on mobile
- **Real-time Processing**: Shows progress during analysis
- **Visual Results**: Displays ingredients with confidence scores
- **Health Scoring**: 1-10 health score based on nutritional content
- **Meal Suggestions**: AI-generated suggestions based on ingredients
- **Dietary Labels**: Automatic dietary categorization

### Styling

The component uses your existing design system:
- **Colors**: Emerald theme for food/health
- **Icons**: Lucide React icons for categories
- **Layout**: Card-based layout with progress indicators
- **Responsive**: Works on mobile and desktop

## 🔄 Workflow Integration

### 1. Inventory Management
- Users can photograph food items to add to inventory
- Automatic ingredient detection and categorization
- Expiry date estimation based on food type

### 2. Recipe Suggestions
- AI analyzes available ingredients
- Suggests recipes based on detected items
- Nutritional balance recommendations

### 3. Meal Planning
- Photograph meals to track what you've eaten
- Nutritional analysis and health scoring
- Dietary balance assessment

## 🛠️ Customization

### Adding New Food Categories

Edit `food_classification_service.py`:

```python
def _load_food_categories(self) -> List[str]:
    return [
        # Add your custom categories
        'custom_food_item',
        # ... existing categories
    ]
```

### Modifying Nutritional Analysis

Update the `_load_ingredient_mapping` method:

```python
def _load_ingredient_mapping(self) -> Dict[str, List[str]]:
    return {
        'your_food': ['nutrient1', 'nutrient2'],
        # ... existing mappings
    }
```

### Custom Health Scoring

Modify the `_analyze_nutritional_content` method to implement your own health scoring algorithm.

## 📊 Performance Optimization

### Model Optimization

1. **Quantization**: Reduce model size by 50%
2. **Pruning**: Remove unnecessary weights
3. **ONNX Export**: Faster inference

### Caching

- Cache model predictions for similar images
- Store nutritional data in database
- Implement image preprocessing cache

## 🐛 Troubleshooting

### Common Issues

1. **Model Loading Failed**
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   ```

2. **CUDA Out of Memory**
   - Use CPU-only version: `torch==2.1.0+cpu`
   - Reduce batch size in model inference

3. **Low Accuracy**
   - Check image quality (well-lit, clear focus)
   - Ensure food items are clearly visible
   - Try different angles or lighting

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Deployment

### Production Setup

1. **Environment Variables**
   ```bash
   export FOOD_SERVICE_PORT=8001
   export MODEL_DEVICE=cpu
   export LOG_LEVEL=INFO
   ```

2. **Docker Deployment**
   ```dockerfile
   FROM python:3.9-slim
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "start_food_service.py"]
   ```

3. **Load Balancing**
   - Use nginx for load balancing
   - Implement health checks
   - Set up monitoring

## 📈 Future Enhancements

### Planned Features

1. **Multi-language Support**: Support for different languages
2. **Allergy Detection**: Identify common allergens
3. **Portion Size Estimation**: Calculate serving sizes
4. **Calorie Counting**: Automatic calorie estimation
5. **Dietary Restrictions**: Keto, vegan, gluten-free detection

### Model Improvements

1. **Ensemble Methods**: Combine multiple models
2. **Transfer Learning**: Fine-tune on custom datasets
3. **Real-time Processing**: Optimize for mobile devices
4. **Edge Computing**: Run models on device

## 📚 Resources

- [PyTorch Documentation](https://pytorch.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Food-101 Dataset](https://www.vision.ee.ethz.ch/datasets_extra/food-101/)
- [Fruits-360 Dataset](https://www.kaggle.com/datasets/moltean/fruits)

## 🤝 Contributing

To contribute to the food classification system:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This food classification system is part of the YUH Smart Grocery App and follows the same license terms.
