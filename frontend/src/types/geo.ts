export interface GeoPoint {
  type: 'Point'
  coordinates: [number, number] // [lng, lat]
}

export interface GeoLineString {
  type: 'LineString'
  coordinates: [number, number][]
}

export interface LatLng {
  lat: number
  lng: number
}

export function toGeoPoint({ lat, lng }: LatLng): GeoPoint {
  return { type: 'Point', coordinates: [lng, lat] }
}

export function fromGeoPoint(point: GeoPoint): LatLng {
  const [lng, lat] = point.coordinates
  return { lat, lng }
}

/** Parul University campus center */
export const CAMPUS_CENTER: LatLng = { lat: 22.312, lng: 73.211 }
