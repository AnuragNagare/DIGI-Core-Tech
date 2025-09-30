'use client'

import React from 'react'
import TrackingPage from '@/components/tracking/TrackingPage'

export default function TrackingPageRoute() {
  return (
    <div className="min-h-screen bg-gray-50">
      <TrackingPage 
        familyId="family-123" 
        userId="user-123" 
      />
    </div>
  )
}
