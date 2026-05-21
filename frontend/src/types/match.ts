import type { GeoPoint } from './geo'
import type { RideOffer } from './offer'

export interface OfferMatchRequest {
  pickup: GeoPoint
  dropoff: GeoPoint
  pickupLabel?: string
  dropoffLabel?: string
  departureAfter?: string
  departureBefore?: string
}

export interface DriverSummary {
  id: string
  displayName: string
  photoUrl?: string | null
  vehicle?: { type?: string; description?: string } | null
}

export interface MatchResult {
  offer: RideOffer
  driver: DriverSummary
  riderDistanceKm: number
  estimatedFuelSplitCost: number
  matchScore: number
  pickupDistanceM: number
  dropoffDistanceM: number
}

export interface OfferMatchResponse {
  matches: MatchResult[]
  matchRadiusMeters: number
}
