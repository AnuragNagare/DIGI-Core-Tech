import { NextResponse } from 'next/server'
import type { ApiResponse, Family } from '@/lib/types'
import { FamilyService } from '@/lib/family-service'

export async function POST(request: Request): Promise<NextResponse<ApiResponse<Family>>> {
  try {
    const body = await request.json()
    const { inviteCode, userId, userName, userEmail } = body

    if (!inviteCode || !userId || !userName || !userEmail) {
      return NextResponse.json({ 
        success: false, 
        error: 'Invite code, user ID, name, and email are required' 
      }, { status: 400 })
    }

    const family = await FamilyService.joinFamily(inviteCode, userId, userName, userEmail)
    
    if (!family) {
      return NextResponse.json({ 
        success: false, 
        error: 'Failed to join family' 
      }, { status: 500 })
    }

    return NextResponse.json({ success: true, data: family })
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to join family' 
    }, { status: 500 })
  }
}
