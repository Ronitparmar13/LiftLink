import type { GeoLineString, GeoPoint } from './geo'

export type OfferStatus =
  | 'open'
  | 'full'
  | 'in_progress'
  | 'completed'
  | 'cancelled'

export interface RideOffer {
  id: string
  driverId: string
  route: GeoLineString
  startLabel: string
  endLabel: string
  startPoint: GeoPoint
  endPoint: GeoPoint
  departureTime: string
  availableSeats: number
  status: OfferStatus
  estimatedDistanceKm: number
  fuelSplitRatePerKm: number
  estimatedFuelSplitTotal: number
  notes: string
  createdAt: string
  updatedAt: string
}

export interface OfferCreatePayload {
  startPoint: GeoPoint
  endPoint: GeoPoint
  route: GeoLineString
  startLabel: string
  endLabel: string
  departureTime: string
  availableSeats: number
  notes: string
}
