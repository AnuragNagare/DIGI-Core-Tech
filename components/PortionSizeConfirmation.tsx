import React, { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  Scale, 
  CheckCircle, 
  AlertTriangle, 
  Target,
  Calculator,
  TrendingUp,
  Zap
} from 'lucide-react'

interface PortionSizeConfirmationProps {
  foodName: string
  predictedWeight: number
  predictedCalories: number
  onWeightChange: (newWeight: number) => void
  onConfirm: (finalWeight: number) => void
  onSkip: () => void
  isConfirmed: boolean
  realTimeCalories: number
  realTimeMacros: {
    protein: number
    carbs: number
    fat: number
    fiber: number
  }
}

export default function PortionSizeConfirmation({
  foodName,
  predictedWeight,
  predictedCalories,
  onWeightChange,
  onConfirm,
  onSkip,
  isConfirmed,
  realTimeCalories,
  realTimeMacros
}: PortionSizeConfirmationProps) {
  const [currentWeight, setCurrentWeight] = useState(predictedWeight)
  const [weightInput, setWeightInput] = useState(predictedWeight.toString())
  const [isAdjusting, setIsAdjusting] = useState(false)

  const handleSliderChange = (value: number[]) => {
    const newWeight = value[0]
    setCurrentWeight(newWeight)
    setWeightInput(newWeight.toString())
    setIsAdjusting(true)
    // Call onWeightChange directly here
    onWeightChange(newWeight)
  }

  const handleInputChange = (value: string) => {
    setWeightInput(value)
    const numValue = parseFloat(value)
    if (!isNaN(numValue) && numValue > 0) {
      setCurrentWeight(numValue)
      setIsAdjusting(true)
      // Call onWeightChange directly here
      onWeightChange(numValue)
    }
  }

  const handleConfirm = () => {
    onConfirm(currentWeight)
    setIsAdjusting(false)
  }

  const handleSkip = () => {
    onSkip()
    setIsAdjusting(false)
  }

  const weightDifference = currentWeight - predictedWeight
  const weightDifferencePercent = ((currentWeight - predictedWeight) / predictedWeight) * 100

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Scale className="w-5 h-5 text-blue-600" />
          Portion Size Confirmation
        </CardTitle>
        <p className="text-sm text-gray-600">
          AI detected: <strong>{foodName}</strong> • Adjust weight for precise calories
        </p>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Predicted vs Current Weight */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium">AI Prediction</span>
            </div>
            <div className="bg-green-50 p-3 rounded-lg border border-green-200">
              <div className="text-2xl font-bold text-green-700">{predictedWeight}g</div>
              <div className="text-sm text-green-600">{predictedCalories} calories</div>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Calculator className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium">Your Adjustment</span>
            </div>
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
              <div className="text-2xl font-bold text-blue-700">{currentWeight}g</div>
              <div className="text-sm text-blue-600">{realTimeCalories} calories</div>
            </div>
          </div>
        </div>

        {/* Weight Adjustment Controls */}
        <div className="space-y-4">
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700">
              Adjust Weight (grams)
            </label>
            
            {/* Slider */}
            <div className="px-2">
              <Slider
                value={[currentWeight]}
                onValueChange={handleSliderChange}
                min={Math.max(10, predictedWeight * 0.3)}
                max={predictedWeight * 3}
                step={5}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>{Math.max(10, Math.round(predictedWeight * 0.3))}g</span>
                <span>{Math.round(predictedWeight * 3)}g</span>
              </div>
            </div>

            {/* Input Field */}
            <div className="flex items-center gap-2">
              <Input
                type="number"
                value={weightInput}
                onChange={(e) => handleInputChange(e.target.value)}
                className="flex-1"
                placeholder="Enter weight in grams"
                min="1"
                step="1"
              />
              <span className="text-sm text-gray-500">g</span>
            </div>
          </div>

          {/* Weight Difference Indicator */}
          {Math.abs(weightDifference) > 5 && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-amber-50 border border-amber-200">
              <TrendingUp className="w-4 h-4 text-amber-600" />
              <span className="text-sm text-amber-700">
                {weightDifference > 0 ? '+' : ''}{weightDifference.toFixed(1)}g 
                ({weightDifferencePercent > 0 ? '+' : ''}{weightDifferencePercent.toFixed(1)}%)
              </span>
            </div>
          )}
        </div>

        {/* Real-time Nutritional Breakdown */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-purple-600" />
            <span className="text-sm font-medium text-gray-700">Real-time Nutrition</span>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="text-center p-3 bg-red-50 rounded-lg border border-red-200">
              <div className="text-lg font-bold text-red-700">{realTimeCalories}</div>
              <div className="text-xs text-red-600">Calories</div>
            </div>
            <div className="text-center p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div className="text-lg font-bold text-blue-700">{realTimeMacros.protein}g</div>
              <div className="text-xs text-blue-600">Protein</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg border border-green-200">
              <div className="text-lg font-bold text-green-700">{realTimeMacros.carbs}g</div>
              <div className="text-xs text-green-600">Carbs</div>
            </div>
            <div className="text-center p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <div className="text-lg font-bold text-yellow-700">{realTimeMacros.fat}g</div>
              <div className="text-xs text-yellow-600">Fat</div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-200">
          <Button
            onClick={handleConfirm}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white"
            disabled={isConfirmed}
          >
            <CheckCircle className="w-4 h-4 mr-2" />
            {isConfirmed ? 'Confirmed' : 'Confirm Portion Size'}
          </Button>
          
          <Button
            onClick={handleSkip}
            variant="outline"
            className="flex-1"
            disabled={isConfirmed}
          >
            Skip & Use AI Prediction
          </Button>
        </div>

        {/* Accuracy Indicator */}
        <div className="text-center">
          <Badge variant="outline" className="text-xs">
            <Target className="w-3 h-3 mr-1" />
            Mathematical Accuracy: 90-95%
          </Badge>
        </div>
      </CardContent>
    </Card>
  )
}
