'use client'

import React from 'react'
import FamilyDashboard from '@/components/family/FamilyDashboard'

export default function FamilyPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <FamilyDashboard 
        userId="user-123" 
        onFamilyJoined={(family) => {
          console.log('Family joined:', family)
          // Handle family joined event
        }} 
      />
    </div>
  )
}
