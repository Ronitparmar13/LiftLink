import type { GeoPoint } from './geo'

export type PoiCategory =
  | 'gate'
  | 'hostel'
  | 'academic'
  | 'landmark'
  | 'bus_stop'
  | 'other'

export interface PoiSearchResult {
  poiId: string
  name: string
  matchedAlias: string
  score: number
  location: GeoPoint
  category: PoiCategory
}

export interface PoiSearchResponse {
  results: PoiSearchResult[]
}
