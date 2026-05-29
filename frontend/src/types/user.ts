export type UserRole = 'rider' | 'driver' | 'both'

export interface VehicleInfo {
  type?: 'two_wheeler' | 'car' | 'other'
  description?: string
}

export interface UserStats {
  ridesAsDriver: number
  ridesAsRider: number
}

export interface UserProfile {
  id: string
  firebaseUid: string
  email: string
  displayName: string
  photoUrl?: string | null
  phone?: string | null
  role: UserRole
  vehicle?: VehicleInfo | null
  stats?: UserStats
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface UserUpdatePayload {
  phone?: string
  role?: UserRole
  vehicle?: VehicleInfo
}
