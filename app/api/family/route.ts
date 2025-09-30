import { NextResponse } from 'next/server'
import type { ApiResponse, Family, FamilyMember } from '@/lib/types'
import { FamilyService } from '@/lib/family-service'

export async function GET(request: Request): Promise<NextResponse<ApiResponse<Family[]>>> {
  try {
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get('userId')

    if (!userId) {
      return NextResponse.json({ success: false, error: 'User ID required' }, { status: 400 })
    }

    const family = await FamilyService.getFamilyByUserId(userId)
    const families = family ? [family] : []

    return NextResponse.json({ success: true, data: families })
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to get families' 
    }, { status: 500 })
  }
}

export async function POST(request: Request): Promise<NextResponse<ApiResponse<Family>>> {
  try {
    const body = await request.json()
    const { name, createdBy } = body

    if (!name || !createdBy) {
      return NextResponse.json({ success: false, error: 'Name and createdBy are required' }, { status: 400 })
    }

    const family = await FamilyService.createFamily(name, createdBy)
    return NextResponse.json({ success: true, data: family })
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to create family' 
    }, { status: 500 })
  }
}
