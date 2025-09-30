/**
 * QR Code Service for Family Invites
 * Handles generation and parsing of QR codes and invite codes
 */

export class QRCodeService {
  /**
   * Generate a secure invite code (6 characters)
   */
  static generateInviteCode(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    let result = ''
    for (let i = 0; i < 6; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return result
  }

  /**
   * Generate QR code data for family invite
   */
  static async generateQRCode(familyId: string, inviteCode: string, expiresAt: string): Promise<string> {
    const qrData = JSON.stringify({
      type: 'family_invite',
      familyId,
      inviteCode,
      expiresAt
    })
    
    // For now, return the JSON data as a string
    // In a real implementation, you would generate an actual QR code image
    return qrData
  }

  /**
   * Parse invite code from QR data
   */
  static parseQRCode(qrData: string): { familyId: string; inviteCode: string; expiresAt: string } | null {
    try {
      const parsed = JSON.parse(qrData)
      
      if (parsed.type !== 'family_invite') {
        return null
      }

      // Check if expired
      const now = new Date()
      const expiresAt = new Date(parsed.expiresAt)
      
      if (now > expiresAt) {
        return null
      }

      return {
        familyId: parsed.familyId,
        inviteCode: parsed.inviteCode,
        expiresAt: parsed.expiresAt
      }
    } catch (error) {
      return null
    }
  }

  /**
   * Validate invite code format
   */
  static validateInviteCode(code: string): boolean {
    return /^[A-Z0-9]{6}$/.test(code)
  }

  /**
   * Check if invite code is expired
   */
  static isInviteExpired(expiresAt: string): boolean {
    const now = new Date()
    const expiryDate = new Date(expiresAt)
    return now > expiryDate
  }
}
