export interface TrendingZone {
  label: string
  centroid: [number, number]
  requestCount: number
}

export interface TrendingHotspotsResponse {
  generatedAt?: string | null
  zones: TrendingZone[]
  sampleSize: number
}
