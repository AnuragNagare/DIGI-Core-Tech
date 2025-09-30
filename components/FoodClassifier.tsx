'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Camera, 
  Upload, 
  X, 
  CheckCircle, 
  AlertTriangle,
  Leaf,
  Apple,
  Carrot,
  Nut,
  Utensils,
  Sparkles,
  Target
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { aiApi } from '@/lib/api'
import PortionSizeConfirmation from './PortionSizeConfirmation'

interface FoodIngredient {
  name: string
  confidence: number
  category: string
  nutritional_info: string[]
}

interface CalorieAnalysis {
  total_calories: number
  total_protein: number
  total_carbs: number
  total_fat: number
  total_fiber: number
  total_weight_g: number
  calories_per_100g: number
  detailed_breakdown: Array<{
    name: string
    portion_size_g: number
    calories: number
    protein: number
    carbs: number
    fat: number
    fiber: number
    confidence: number
  }>
  meal_type: string
  nutritional_quality: {
    quality_score: number
    quality_rating: string
    protein_percentage: number
    fat_percentage: number
    fiber_content: number
    recommendations: string[]
  }
  dietary_recommendations: string[]
}

interface FoodClassificationResult {
  ingredients: FoodIngredient[]
  confidence: number
  total_ingredients: number
  processing_time: string
  nutritional_analysis: {
    total_ingredients: number
    average_confidence: number
    detected_nutrients: string[]
    health_score: number
    dietary_balance: string
  }
  calorie_analysis: CalorieAnalysis
  meal_suggestions: string[]
  dietary_labels: string[]
}

interface FoodClassifierProps {
  onClose: () => void
  onIngredientsDetected?: (ingredients: FoodIngredient[]) => void
}

const isMobileApp = () => {
  return typeof window !== 'undefined' && (
    window.location.protocol === 'capacitor:' ||
    window.location.protocol === 'ionic:' ||
    /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  )
}

export default function FoodClassifier({ onClose, onIngredientsDetected }: FoodClassifierProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<FoodClassificationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [showCamera, setShowCamera] = useState(false)
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null)
  const [showPortionConfirmation, setShowPortionConfirmation] = useState(false)
  const [portionData, setPortionData] = useState<{
    foodName: string
    predictedWeight: number
    predictedCalories: number
    confirmedWeight: number
    isConfirmed: boolean
  } | null>(null)
  const [realTimeNutrition, setRealTimeNutrition] = useState<{
    calories: number
    protein: number
    carbs: number
    fat: number
    fiber: number
  }>({
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
    fiber: 0
  })

  // Cleanup camera stream on unmount
  useEffect(() => {
    return () => {
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop())
      }
    }
  }, [cameraStream])

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment', // Use back camera if available
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      })
      setCameraStream(stream)
      setShowCamera(true)
    } catch (err) {
      console.error('Camera access failed:', err)
      setError('Camera access failed. Please try uploading an image instead.')
    }
  }

  const capturePhoto = () => {
    if (!cameraStream) return
    
    const video = document.getElementById('camera-video') as HTMLVideoElement
    if (!video) return
    
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    ctx?.drawImage(video, 0, 0)
    
    const imageDataUrl = canvas.toDataURL('image/jpeg', 0.9)
    setSelectedImage(imageDataUrl)
    setShowCamera(false)
    
    // Stop camera stream
    cameraStream.getTracks().forEach(track => track.stop())
    setCameraStream(null)
    
    // Process the image
    processImage(imageDataUrl)
  }

  const processImage = async (imageDataUrl: string) => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Call the food classification API
      const response = await aiApi.classifyPhoto(imageDataUrl)
      
      if (response.success && response.data) {
        setResult(response.data)
        if (onIngredientsDetected) {
          onIngredientsDetected(response.data.ingredients)
        }
        
        // Show portion confirmation if we have calorie analysis
        if (response.data.calorie_analysis && response.data.calorie_analysis.detailed_breakdown.length > 0) {
          const firstItem = response.data.calorie_analysis.detailed_breakdown[0]
          setPortionData({
            foodName: firstItem.name,
            predictedWeight: firstItem.portion_size_g,
            predictedCalories: firstItem.calories,
            confirmedWeight: firstItem.portion_size_g,
            isConfirmed: false
          })
          setRealTimeNutrition({
            calories: firstItem.calories,
            protein: firstItem.protein,
            carbs: firstItem.carbs,
            fat: firstItem.fat,
            fiber: firstItem.fiber
          })
          setShowPortionConfirmation(true)
        }
      } else {
        setError(response.error || 'Food classification failed')
      }
    } catch (err) {
      console.error('Food classification failed:', err)
      setError(err instanceof Error ? err.message : 'Failed to process image')
    } finally {
      setIsLoading(false)
    }
  }

  const handleWeightChange = useCallback(async (newWeight: number) => {
    if (!portionData) return

    try {
      // Calculate real-time nutrition based on weight change
      const scaleFactor = newWeight / portionData.predictedWeight
      const updatedNutrition = {
        calories: Math.round(portionData.predictedCalories * scaleFactor),
        protein: Math.round((realTimeNutrition.protein * scaleFactor) * 10) / 10,
        carbs: Math.round((realTimeNutrition.carbs * scaleFactor) * 10) / 10,
        fat: Math.round((realTimeNutrition.fat * scaleFactor) * 10) / 10,
        fiber: Math.round((realTimeNutrition.fiber * scaleFactor) * 10) / 10
      }
      
      setRealTimeNutrition(updatedNutrition)
    } catch (err) {
      console.error('Error updating nutrition:', err)
    }
  }, [portionData, realTimeNutrition])

  const handlePortionConfirm = useCallback(async (finalWeight: number) => {
    if (!portionData) return

    try {
      // Update portion data
      setPortionData(prev => prev ? { ...prev, confirmedWeight: finalWeight, isConfirmed: true } : null)
      
      // Update real-time nutrition with final values
      const scaleFactor = finalWeight / portionData.predictedWeight
      const finalNutrition = {
        calories: Math.round(portionData.predictedCalories * scaleFactor),
        protein: Math.round((realTimeNutrition.protein * scaleFactor) * 10) / 10,
        carbs: Math.round((realTimeNutrition.carbs * scaleFactor) * 10) / 10,
        fat: Math.round((realTimeNutrition.fat * scaleFactor) * 10) / 10,
        fiber: Math.round((realTimeNutrition.fiber * scaleFactor) * 10) / 10
      }
      
      setRealTimeNutrition(finalNutrition)
      setShowPortionConfirmation(false)
    } catch (err) {
      console.error('Error confirming portion:', err)
    }
  }, [portionData, realTimeNutrition])

  const handlePortionSkip = useCallback(() => {
    setShowPortionConfirmation(false)
    if (portionData) {
      setPortionData(prev => prev ? { ...prev, isConfirmed: true } : null)
    }
  }, [portionData])

  const handleImageCapture = async () => {
    if (isMobileApp()) {
      try {
        const { Camera } = await import('@capacitor/camera')
        const { CameraResultType, CameraSource } = await import('@capacitor/camera')
        
        const image = await Camera.getPhoto({
          quality: 90,
          allowEditing: false,
          resultType: CameraResultType.DataUrl,
          source: CameraSource.Camera
        })

        if (image.dataUrl) {
          setSelectedImage(image.dataUrl)
          processImage(image.dataUrl)
        } else {
          throw new Error('No image captured')
        }
      } catch (capacitorError) {
        console.warn('Capacitor Camera not available:', capacitorError)
        setError('Camera access failed. Please try uploading an image instead.')
      }
    } else {
      // For desktop browsers, start camera
      await startCamera()
    }
  }

  const handleFileUpload = async () => {
    try {
      // Create file input for upload
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = 'image/*'
      
      const file = await new Promise<File>((resolve, reject) => {
        input.onchange = (event) => {
          const file = (event.target as HTMLInputElement).files?.[0]
          if (file) {
            resolve(file)
          } else {
            reject(new Error('No file selected'))
          }
        }
        input.click()
      })

      // Convert file to data URL
      const reader = new FileReader()
      const imageDataUrl = await new Promise<string>((resolve, reject) => {
        reader.onload = (e) => resolve(e.target?.result as string)
        reader.onerror = () => reject(new Error('Failed to read file'))
        reader.readAsDataURL(file)
      })

      setSelectedImage(imageDataUrl)
      processImage(imageDataUrl)
    } catch (err) {
      console.error('File upload failed:', err)
      setError(err instanceof Error ? err.message : 'Failed to upload image')
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'fruits':
        return <Apple className="w-4 h-4" />
      case 'vegetables':
        return <Carrot className="w-4 h-4" />
      case 'nuts':
        return <Nut className="w-4 h-4" />
      case 'proteins':
        return <Utensils className="w-4 h-4" />
      default:
        return <Leaf className="w-4 h-4" />
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'fruits':
        return 'bg-red-100 text-red-800'
      case 'vegetables':
        return 'bg-green-100 text-green-800'
      case 'nuts':
        return 'bg-amber-100 text-amber-800'
      case 'proteins':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getHealthScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600'
    if (score >= 6) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-100 rounded-lg">
              <Camera className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Food Classifier</h2>
              <p className="text-sm text-gray-600">Identify ingredients in your food</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        <div className="p-6">
          {showCamera && (
            <div className="text-center py-8">
              <div className="relative mb-6">
                <video
                  id="camera-video"
                  autoPlay
                  playsInline
                  muted
                  className="w-full max-w-md mx-auto rounded-lg border-2 border-emerald-200"
                  ref={(video) => {
                    if (video && cameraStream) {
                      video.srcObject = cameraStream
                    }
                  }}
                />
                <div className="absolute inset-0 border-2 border-dashed border-emerald-400 rounded-lg pointer-events-none">
                  <div className="absolute top-2 left-2 right-2 text-center">
                    <p className="text-sm text-white bg-black bg-opacity-50 rounded px-2 py-1">
                      Position your food in the frame
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="flex gap-4 justify-center">
                <Button 
                  onClick={capturePhoto}
                  className="bg-emerald-500 hover:bg-emerald-600 px-8 py-3 text-lg"
                >
                  <Camera className="w-6 h-6 mr-3" />
                  Capture Photo
                </Button>
                
                <Button 
                  onClick={() => {
                    setShowCamera(false)
                    if (cameraStream) {
                      cameraStream.getTracks().forEach(track => track.stop())
                      setCameraStream(null)
                    }
                  }}
                  variant="outline"
                  className="px-8 py-3 text-lg"
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}

          {!result && !isLoading && !showCamera && (
            <div className="text-center py-8">
              <div className="w-24 h-24 mx-auto mb-6 bg-emerald-50 rounded-full flex items-center justify-center">
                <Camera className="w-12 h-12 text-emerald-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Capture Food Image</h3>
              <p className="text-gray-600 mb-6">
                Take a photo of your food to identify ingredients and get nutritional insights
              </p>
              
              {/* Camera and Upload Options */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button 
                  onClick={handleImageCapture}
                  disabled={isLoading}
                  className="bg-emerald-500 hover:bg-emerald-600 px-6 py-3 text-base flex-1 sm:flex-none"
                >
                  <Camera className="w-5 h-5 mr-2" />
                  {isLoading ? 'Processing...' : 'Take Photo'}
                </Button>
                
                <Button 
                  onClick={handleFileUpload}
                  disabled={isLoading}
                  variant="outline"
                  className="border-emerald-200 text-emerald-700 hover:bg-emerald-50 px-6 py-3 text-base flex-1 sm:flex-none"
                >
                  <Upload className="w-5 h-5 mr-2" />
                  Upload Image
                </Button>
              </div>
              
              <p className="text-xs text-gray-500 mt-4">
                Works on both mobile and desktop
              </p>
            </div>
          )}

          {isLoading && (
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto mb-4 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin"></div>
              <h3 className="text-lg font-semibold mb-2">Analyzing Food...</h3>
              <p className="text-gray-600">Identifying ingredients and nutritional content</p>
              <div className="mt-4">
                <Progress value={66} className="w-full" />
              </div>
            </div>
          )}

          {error && (
            <Alert className="mb-6">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Portion Size Confirmation */}
          {showPortionConfirmation && portionData && (
            <PortionSizeConfirmation
              foodName={portionData.foodName}
              predictedWeight={portionData.predictedWeight}
              predictedCalories={portionData.predictedCalories}
              onWeightChange={handleWeightChange}
              onConfirm={handlePortionConfirm}
              onSkip={handlePortionSkip}
              isConfirmed={portionData.isConfirmed}
              realTimeCalories={realTimeNutrition.calories}
              realTimeMacros={realTimeNutrition}
            />
          )}

          {result && (
            <div className="space-y-6">
              {/* Selected Image */}
              {selectedImage && (
                <div className="text-center">
                  <img 
                    src={selectedImage} 
                    alt="Captured food" 
                    className="w-48 h-48 object-cover rounded-lg mx-auto border"
                  />
                </div>
              )}

              {/* Calorie Analysis */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-orange-600" />
                    Calorie Analysis
                  </CardTitle>
                  <CardDescription>
                    Realistic calorie count based on actual nutritional data
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">
                        {result.calorie_analysis.total_calories}
                      </div>
                      <div className="text-sm text-orange-700">Total Calories</div>
                    </div>
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {result.calorie_analysis.total_weight_g}g
                      </div>
                      <div className="text-sm text-blue-700">Total Weight</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    <div className="text-center p-2 bg-gray-50 rounded">
                      <div className="font-semibold text-gray-700">{result.calorie_analysis.total_protein}g</div>
                      <div className="text-xs text-gray-600">Protein</div>
                    </div>
                    <div className="text-center p-2 bg-gray-50 rounded">
                      <div className="font-semibold text-gray-700">{result.calorie_analysis.total_carbs}g</div>
                      <div className="text-xs text-gray-600">Carbs</div>
                    </div>
                    <div className="text-center p-2 bg-gray-50 rounded">
                      <div className="font-semibold text-gray-700">{result.calorie_analysis.total_fat}g</div>
                      <div className="text-xs text-gray-600">Fat</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Health Score */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-emerald-600" />
                    Health Score
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-4">
                    <div className="text-3xl font-bold">
                      <span className={getHealthScoreColor(result.nutritional_analysis.health_score)}>
                        {result.nutritional_analysis.health_score.toFixed(1)}
                      </span>
                      <span className="text-gray-500 text-lg">/10</span>
                    </div>
                    <div className="flex-1">
                      <Progress 
                        value={result.nutritional_analysis.health_score * 10} 
                        className="h-3"
                      />
                      <p className="text-sm text-gray-600 mt-1">
                        {result.nutritional_analysis.dietary_balance.replace('-', ' ')}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Detected Ingredients */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-emerald-600" />
                    Detected Ingredients ({result.total_ingredients})
                  </CardTitle>
                  <CardDescription>
                    Confidence: {(result.confidence * 100).toFixed(1)}%
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-3">
                    {result.ingredients.map((ingredient, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          {getCategoryIcon(ingredient.category)}
                          <div>
                            <p className="font-medium capitalize">{ingredient.name}</p>
                            <Badge 
                              variant="secondary" 
                              className={cn("text-xs", getCategoryColor(ingredient.category))}
                            >
                              {ingredient.category}
                            </Badge>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium">
                            {(ingredient.confidence * 100).toFixed(1)}%
                          </p>
                          <Progress 
                            value={ingredient.confidence * 100} 
                            className="w-16 h-2 mt-1"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Nutritional Analysis */}
              {result.nutritional_analysis.detected_nutrients.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Nutritional Content</CardTitle>
                    <CardDescription>
                      Key nutrients detected in your food
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {result.nutritional_analysis.detected_nutrients.map((nutrient, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {nutrient.replace('_', ' ')}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Meal Suggestions */}
              {result.meal_suggestions.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Meal Suggestions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {result.meal_suggestions.map((suggestion, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <div className="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0"></div>
                          <p className="text-sm text-gray-700">{suggestion}</p>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Detailed Calorie Breakdown */}
              {result.calorie_analysis.detailed_breakdown.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Detailed Calorie Breakdown</CardTitle>
                    <CardDescription>
                      Calorie count per ingredient with realistic portion sizes
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {result.calorie_analysis.detailed_breakdown.map((item, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center gap-3">
                            {getCategoryIcon(item.name)}
                            <div>
                              <p className="font-medium capitalize">{item.name}</p>
                              <p className="text-sm text-gray-600">
                                {item.portion_size_g}g • {(item.confidence * 100).toFixed(0)}% confidence
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-bold text-orange-600">{item.calories} cal</p>
                            <p className="text-xs text-gray-600">
                              P:{item.protein}g C:{item.carbs}g F:{item.fat}g
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Nutritional Quality */}
              <Card>
                <CardHeader>
                  <CardTitle>Nutritional Quality</CardTitle>
                  <CardDescription>
                    Quality rating: {result.calorie_analysis.nutritional_quality.quality_rating.replace('_', ' ')}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <div className="text-lg font-bold text-green-600">
                        {result.calorie_analysis.nutritional_quality.protein_percentage}%
                      </div>
                      <div className="text-sm text-green-700">Protein</div>
                    </div>
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <div className="text-lg font-bold text-blue-600">
                        {result.calorie_analysis.nutritional_quality.fat_percentage}%
                      </div>
                      <div className="text-sm text-blue-700">Fat</div>
                    </div>
                  </div>
                  
                  {result.calorie_analysis.nutritional_quality.recommendations.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700">Recommendations:</p>
                      {result.calorie_analysis.nutritional_quality.recommendations.map((rec, index) => (
                        <p key={index} className="text-sm text-gray-600 flex items-start gap-2">
                          <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                          {rec}
                        </p>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Dietary Labels */}
              {result.dietary_labels.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Dietary Information</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {result.dietary_labels.map((label, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {label.replace('-', ' ')}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <div className="flex gap-2 flex-1">
                  <Button 
                    onClick={handleImageCapture}
                    variant="outline"
                    className="flex-1"
                  >
                    <Camera className="w-4 h-4 mr-2" />
                    Take Photo
                  </Button>
                  <Button 
                    onClick={handleFileUpload}
                    variant="outline"
                    className="flex-1"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Upload
                  </Button>
                </div>
                <Button 
                  onClick={onClose}
                  className="w-full sm:w-auto"
                >
                  Done
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
