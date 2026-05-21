export type UserRole = 'rider' | 'driver' | 'both'

export interface VehicleInfo {
  type?: 'two_wheeler' | 'car' | 'other'
  description?: string
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
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface UserUpdatePayload {
  phone?: string
  role?: UserRole
  vehicle?: VehicleInfo
}
