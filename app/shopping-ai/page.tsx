'use client'

import React from 'react'
import EnhancedShoppingList from '@/components/EnhancedShoppingList'

export default function AIShoppingPage() {
  // In a real app, you'd get this from authentication
  const userId = 'user-123'

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8">
        <EnhancedShoppingList userId={userId} />
      </div>
    </div>
  )
}