import axios from 'axios'
import type { OfferCreatePayload, RideOffer } from '../types/offer'
import type { OfferMatchRequest, OfferMatchResponse } from '../types/match'
import type { RequestDetail, RideRequest } from '../types/request'
import type { UserProfile, UserUpdatePayload } from '../types/user'
import type { GeoPoint } from '../types/geo'
import type { PoiSearchResponse } from '../types/location'
import type { TrendingHotspotsResponse } from '../types/hotspot'

const API_ROOT =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/api\/v1\/?$/, '') ||
  'http://localhost:8000'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || `${API_ROOT}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

let tokenRefresher: (() => Promise<string | null>) | null = null

export function setTokenRefresher(fn: () => Promise<string | null>) {
  tokenRefresher = fn
}

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common.Authorization
  }
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (
      error.response?.status === 401 &&
      tokenRefresher &&
      original &&
      !original._retry
    ) {
      original._retry = true
      const token = await tokenRefresher()
      if (token) {
        setAuthToken(token)
        original.headers.Authorization = `Bearer ${token}`
        return api(original)
      }
    }
    return Promise.reject(error)
  }
)

export async function checkHealth(): Promise<{
  status: string
  service: string
  mongodb?: string
  firebase?: string
}> {
  const { data } = await axios.get(`${API_ROOT}/health`)
  return data
}

export async function syncUser(): Promise<UserProfile> {
  const { data } = await api.post<UserProfile>('/auth/sync')
  return data
}

export async function getMe(): Promise<UserProfile> {
  const { data } = await api.get<UserProfile>('/auth/me')
  return data
}

export async function updateProfile(
  payload: UserUpdatePayload
): Promise<UserProfile> {
  const { data } = await api.patch<UserProfile>('/users/me', payload)
  return data
}

export async function createOffer(
  payload: OfferCreatePayload
): Promise<RideOffer> {
  const { data } = await api.post<RideOffer>('/offers', payload)
  return data
}

export async function getMyOffers(): Promise<RideOffer[]> {
  const { data } = await api.get<RideOffer[]>('/offers/mine')
  return data
}

export async function matchOffers(
  payload: OfferMatchRequest
): Promise<OfferMatchResponse> {
  const { data } = await api.post<OfferMatchResponse>('/offers/match', payload)
  return data
}

export interface CreateRequestPayload {
  offerId: string
  pickup: GeoPoint
  dropoff: GeoPoint
  pickupLabel: string
  dropoffLabel: string
}

export async function createRequest(
  payload: CreateRequestPayload
): Promise<RideRequest> {
  const { data } = await api.post<RideRequest>('/requests', payload)
  return data
}

export async function getMyRequests(): Promise<RideRequest[]> {
  const { data } = await api.get<RideRequest[]>('/requests/mine')
  return data
}

export async function getDriverInbox(): Promise<RideRequest[]> {
  const { data } = await api.get<RideRequest[]>('/requests/inbox/driver')
  return data
}

export async function getRequestDetail(id: string): Promise<RequestDetail> {
  const { data } = await api.get<RequestDetail>(`/requests/${id}/detail`)
  return data
}

export async function getOfferRequests(offerId: string): Promise<RideRequest[]> {
  const { data } = await api.get<RideRequest[]>(`/offers/${offerId}/requests`)
  return data
}

export async function acceptRequest(id: string): Promise<RideRequest> {
  const { data } = await api.patch<RideRequest>(`/requests/${id}/accept`)
  return data
}

export async function rejectRequest(id: string): Promise<RideRequest> {
  const { data } = await api.patch<RideRequest>(`/requests/${id}/reject`)
  return data
}

export async function cancelRequest(id: string): Promise<RideRequest> {
  const { data } = await api.patch<RideRequest>(`/requests/${id}/cancel`)
  return data
}

export async function completeRequest(id: string): Promise<RideRequest> {
  const { data } = await api.patch<RideRequest>(`/requests/${id}/complete`)
  return data
}

export async function searchLocations(
  q: string,
  limit = 8
): Promise<PoiSearchResponse> {
  const { data } = await api.get<PoiSearchResponse>('/locations/search', {
    params: { q, limit },
  })
  return data
}

export async function getTrendingHotspots(): Promise<TrendingHotspotsResponse> {
  const { data } = await api.get<TrendingHotspotsResponse>('/hotspots/trending')
  return data
}

export async function refreshHotspots(): Promise<void> {
  await api.post('/hotspots/refresh')
}
