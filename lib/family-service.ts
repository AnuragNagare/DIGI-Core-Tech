import type { Family, FamilyMember, FamilyInvite, FamilySyncData } from './types'
import { QRCodeService } from './qr-service'

export class FamilyService {
  private static families: Map<string, Family> = new Map()
  private static invites: Map<string, FamilyInvite> = new Map()

  /**
   * Create a new family
   */
  static async createFamily(name: string, createdBy: string): Promise<Family> {
    const familyId = `family_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`
    const inviteCode = QRCodeService.generateInviteCode()
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7 days

    const qrCode = await QRCodeService.generateQRCode(familyId, inviteCode, expiresAt)

    const family: Family = {
      id: familyId,
      name,
      createdBy,
      createdAt: new Date().toISOString(),
      inviteCode,
      qrCode,
      members: [],
      isActive: true
    }

    // Add creator as admin member
    const adminMember: FamilyMember = {
      id: `member_${Date.now()}`,
      familyId,
      userId: createdBy,
      name: 'Family Admin', // This should come from user data
      email: 'admin@family.com', // This should come from user data
      role: 'admin',
      joinedAt: new Date().toISOString(),
      isActive: true
    }

    family.members.push(adminMember)

    // Create invite
    const invite: FamilyInvite = {
      id: `invite_${Date.now()}`,
      familyId,
      inviteCode,
      qrCode,
      createdBy,
      expiresAt,
      usedCount: 0,
      isActive: true
    }

    this.families.set(familyId, family)
    this.invites.set(inviteCode, invite)

    return family
  }

  /**
   * Join family using invite code
   */
  static async joinFamily(inviteCode: string, userId: string, userName: string, userEmail: string): Promise<Family | null> {
    const invite = this.invites.get(inviteCode)
    
    if (!invite || !invite.isActive) {
      throw new Error('Invalid or expired invite code')
    }

    if (QRCodeService.isInviteExpired(invite.expiresAt)) {
      throw new Error('Invite code has expired')
    }

    const family = this.families.get(invite.familyId)
    if (!family) {
      throw new Error('Family not found')
    }

    // Check if user is already a member
    const existingMember = family.members.find(member => member.userId === userId)
    if (existingMember) {
      throw new Error('User is already a member of this family')
    }

    // Add new member
    const newMember: FamilyMember = {
      id: `member_${Date.now()}`,
      familyId: family.id,
      userId,
      name: userName,
      email: userEmail,
      role: 'member',
      joinedAt: new Date().toISOString(),
      isActive: true
    }

    family.members.push(newMember)
    invite.usedCount++

    return family
  }

  /**
   * Join family using QR code
   */
  static async joinFamilyByQR(qrData: string, userId: string, userName: string, userEmail: string): Promise<Family | null> {
    const parsedData = QRCodeService.parseQRCode(qrData)
    
    if (!parsedData) {
      throw new Error('Invalid QR code')
    }

    return this.joinFamily(parsedData.inviteCode, userId, userName, userEmail)
  }

  /**
   * Get family by ID
   */
  static async getFamily(familyId: string): Promise<Family | null> {
    return this.families.get(familyId) || null
  }

  /**
   * Get family by user ID
   */
  static async getFamilyByUserId(userId: string): Promise<Family | null> {
    for (const family of this.families.values()) {
      if (family.members.some(member => member.userId === userId)) {
        return family
      }
    }
    return null
  }

  /**
   * Update family sync data
   */
  static async updateFamilySync(familyId: string, syncData: Partial<FamilySyncData>): Promise<void> {
    const family = this.families.get(familyId)
    if (!family) {
      throw new Error('Family not found')
    }

    // In a real implementation, this would update the database
    // For now, we'll just log the sync
    console.log(`Family ${familyId} sync updated:`, syncData)
  }

  /**
   * Remove member from family
   */
  static async removeMember(familyId: string, userId: string): Promise<boolean> {
    const family = this.families.get(familyId)
    if (!family) {
      return false
    }

    family.members = family.members.filter(member => member.userId !== userId)
    return true
  }

  /**
   * Generate new invite code for family
   */
  static async generateNewInvite(familyId: string, createdBy: string): Promise<FamilyInvite> {
    const family = this.families.get(familyId)
    if (!family) {
      throw new Error('Family not found')
    }

    const inviteCode = QRCodeService.generateInviteCode()
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
    const qrCode = await QRCodeService.generateQRCode(familyId, inviteCode, expiresAt)

    const invite: FamilyInvite = {
      id: `invite_${Date.now()}`,
      familyId,
      inviteCode,
      qrCode,
      createdBy,
      expiresAt,
      usedCount: 0,
      isActive: true
    }

    this.invites.set(inviteCode, invite)
    return invite
  }
}
