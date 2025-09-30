'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Users, 
  QrCode, 
  UserPlus, 
  Copy, 
  Share2, 
  Settings,
  Trash2,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { FamilyService } from '@/lib/family-service'
import { QRCodeService } from '@/lib/qr-service'
import type { Family, FamilyMember } from '@/lib/types'

interface FamilyDashboardProps {
  userId: string
  onFamilyJoined?: (family: Family) => void
}

export default function FamilyDashboard({ userId, onFamilyJoined }: FamilyDashboardProps) {
  const [family, setFamily] = useState<Family | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showQRCode, setShowQRCode] = useState(false)
  const [inviteCode, setInviteCode] = useState('')
  const [qrData, setQrData] = useState('')

  useEffect(() => {
    loadFamily()
  }, [userId])

  const loadFamily = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/api/family?userId=${userId}`)
      const result = await response.json()
      
      if (result.success && result.data.length > 0) {
        setFamily(result.data[0])
      }
    } catch (err) {
      setError('Failed to load family data')
    } finally {
      setLoading(false)
    }
  }

  const createFamily = async (name: string) => {
    try {
      setLoading(true)
      const response = await fetch('/api/family', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, createdBy: userId })
      })
      
      const result = await response.json()
      if (result.success) {
        setFamily(result.data)
        onFamilyJoined?.(result.data)
      } else {
        setError(result.error)
      }
    } catch (err) {
      setError('Failed to create family')
    } finally {
      setLoading(false)
    }
  }

  const joinFamily = async () => {
    if (!inviteCode.trim()) return

    try {
      setLoading(true)
      const response = await fetch('/api/family/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          inviteCode: inviteCode.trim(),
          userId,
          userName: 'User Name', // This should come from user profile
          userEmail: 'user@example.com' // This should come from user profile
        })
      })
      
      const result = await response.json()
      if (result.success) {
        setFamily(result.data)
        setInviteCode('')
        onFamilyJoined?.(result.data)
      } else {
        setError(result.error)
      }
    } catch (err) {
      setError('Failed to join family')
    } finally {
      setLoading(false)
    }
  }

  const copyInviteCode = () => {
    if (family?.inviteCode) {
      navigator.clipboard.writeText(family.inviteCode)
    }
  }

  const generateQRCode = async () => {
    if (!family) return

    try {
      const qrData = JSON.stringify({
        type: 'family_invite',
        familyId: family.id,
        inviteCode: family.inviteCode,
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
      })
      
      setQrData(qrData)
      setShowQRCode(true)
    } catch (err) {
      setError('Failed to generate QR code')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  if (!family) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              Create or Join Family
            </CardTitle>
            <CardDescription>
              Create a new family group or join an existing one using an invite code
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h3 className="font-semibold">Create New Family</h3>
                <Button 
                  onClick={() => createFamily('My Family')}
                  className="w-full"
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  Create Family
                </Button>
              </div>
              
              <div className="space-y-3">
                <h3 className="font-semibold">Join Existing Family</h3>
                <div className="flex gap-2">
                  <Input
                    placeholder="Enter invite code"
                    value={inviteCode}
                    onChange={(e) => setInviteCode(e.target.value)}
                  />
                  <Button onClick={joinFamily} disabled={!inviteCode.trim()}>
                    Join
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                {family.name}
              </CardTitle>
              <CardDescription>
                {family.members.length} member{family.members.length !== 1 ? 's' : ''}
              </CardDescription>
            </div>
            <Badge variant="outline" className="text-green-600">
              Active
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="members" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="members">Members</TabsTrigger>
              <TabsTrigger value="invite">Invite</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
            </TabsList>

            <TabsContent value="members" className="space-y-4">
              <div className="space-y-3">
                {family.members.map((member) => (
                  <div key={member.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                        <Users className="w-4 h-4 text-purple-600" />
                      </div>
                      <div>
                        <p className="font-medium">{member.name}</p>
                        <p className="text-sm text-gray-500">{member.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={member.role === 'admin' ? 'default' : 'secondary'}>
                        {member.role}
                      </Badge>
                      {member.isActive && (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="invite" className="space-y-4">
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Invite Code</h3>
                  <div className="flex gap-2">
                    <Input
                      value={family.inviteCode}
                      readOnly
                      className="font-mono"
                    />
                    <Button onClick={copyInviteCode} variant="outline">
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">QR Code</h3>
                  <div className="flex gap-2">
                    <Button onClick={generateQRCode} variant="outline">
                      <QrCode className="w-4 h-4 mr-2" />
                      Generate QR Code
                    </Button>
                    <Button variant="outline">
                      <Share2 className="w-4 h-4 mr-2" />
                      Share
                    </Button>
                  </div>
                </div>

                {showQRCode && qrData && (
                  <div className="p-4 border rounded-lg bg-gray-50">
                    <h4 className="font-medium mb-2">QR Code Generated</h4>
                    <p className="text-sm text-gray-600 mb-3">
                      Share this QR code with family members to let them join instantly
                    </p>
                    <div className="text-xs font-mono bg-white p-2 rounded border break-all">
                      {qrData}
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="settings" className="space-y-4">
              <div className="space-y-3">
                <h3 className="font-semibold">Family Settings</h3>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start">
                    <Settings className="w-4 h-4 mr-2" />
                    Manage Permissions
                  </Button>
                  <Button variant="outline" className="w-full justify-start text-red-600">
                    <Trash2 className="w-4 h-4 mr-2" />
                    Leave Family
                  </Button>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {error && (
        <div className="p-4 border border-red-200 bg-red-50 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-600" />
          <span className="text-red-800">{error}</span>
        </div>
      )}
    </div>
  )
}
