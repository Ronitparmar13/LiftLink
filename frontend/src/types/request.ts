import type { GeoPoint } from './geo'

export type RequestStatus =
  | 'pending'
  | 'accepted'
  | 'rejected'
  | 'cancelled'
  | 'completed'

export interface RideRequest {
  id: string
  riderId: string
  offerId: string
  pickup: GeoPoint
  dropoff: GeoPoint
  pickupLabel: string
  dropoffLabel: string
  riderDistanceKm: number
  estimatedFuelSplitCost: number
  status: RequestStatus
  driverResponseAt?: string | null
  createdAt: string
  updatedAt: string
}

export interface ContactSummary {
  id: string
  displayName: string
  photoUrl?: string | null
  phone?: string | null
  email?: string | null
}

export interface OfferSummary {
  id: string
  startLabel: string
  endLabel: string
  departureTime: string
  status: string
  fuelSplitRatePerKm: number
}

export interface RequestDetail {
  request: RideRequest
  offer: OfferSummary
  rider: ContactSummary
  driver: ContactSummary
}
