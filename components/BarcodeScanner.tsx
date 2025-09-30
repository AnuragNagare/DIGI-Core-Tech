'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { X, Camera } from 'lucide-react'

interface BarcodeScannerProps {
  onResult: (barcode: string) => void
  onClose: () => void
}

export default function BarcodeScanner({ onResult, onClose }: BarcodeScannerProps) {
  const [error, setError] = useState<string | null>(null)

  const handleMobilePhotoCapture = async () => {
    try {
      // Try to use Capacitor Camera if available
      try {
        const { Camera } = await import('@capacitor/camera')
        const { CameraResultType, CameraSource } = await import('@capacitor/camera')
        
        const image = await Camera.getPhoto({
          quality: 90,
          allowEditing: false,
          resultType: CameraResultType.DataUrl,
          source: CameraSource.Camera
        })

        // Simulate barcode detection
        const simulatedBarcode = BC
        onResult(simulatedBarcode)
        return
      } catch (capacitorError) {
        console.warn('Capacitor Camera not available:', capacitorError)
      }

      // Fallback to file input for web browsers
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = 'image/*'
      input.capture = 'environment'
      
      input.onchange = (event) => {
        const file = (event.target as HTMLInputElement).files?.[0]
        if (file) {
          const simulatedBarcode = BC
          onResult(simulatedBarcode)
        }
      }
      
      input.click()
    } catch (err) {
      console.error('Photo capture failed:', err)
      setError('Camera access failed. Please try again.')
    }
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl p-6 max-w-sm w-full">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Camera Error</h3>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="flex gap-2">
            <Button 
              className="flex-1" 
              onClick={() => {
                setError(null)
                handleMobilePhotoCapture()
              }}
            >
              Retry
            </Button>
            <Button variant="outline" className="flex-1" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      <div className="flex items-center justify-between p-4 bg-black text-white">
        <h2 className="text-lg font-semibold">Scan Barcode</h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="text-white hover:bg-gray-800"
        >
          <X className="w-5 h-5" />
        </Button>
      </div>

      <div className="flex-1 flex items-center justify-center bg-gray-900">
        <div className="text-center text-white p-8">
          <Camera className="w-20 h-20 mx-auto mb-6 opacity-60" />
          <h3 className="text-xl font-semibold mb-4">Camera Scanner</h3>
          <p className="mb-6 opacity-80">Tap the button below to open your camera</p>
          <Button 
            onClick={handleMobilePhotoCapture}
            className="bg-emerald-500 hover:bg-emerald-600 px-8 py-3 text-lg"
          >
            <Camera className="w-6 h-6 mr-3" />
            Open Camera
          </Button>
        </div>
      </div>

      <div className="p-4 bg-black text-white text-center">
        <p className="text-sm opacity-80">Take a clear photo of the barcode</p>
      </div>
    </div>
  )
}
