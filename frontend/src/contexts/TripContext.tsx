import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { getDriverInbox, getMyRequests } from '../services/api'
import type { RideRequest } from '../types/request'
import { useAuth } from './AuthContext'

interface TripContextValue {
  riderRequests: RideRequest[]
  driverPending: RideRequest[]
  activeRiderTrip: RideRequest | null
  loading: boolean
  refresh: () => Promise<void>
}

const TripContext = createContext<TripContextValue | null>(null)

export function TripProvider({ children }: { children: ReactNode }) {
  const { firebaseUser } = useAuth()
  const [riderRequests, setRiderRequests] = useState<RideRequest[]>([])
  const [driverPending, setDriverPending] = useState<RideRequest[]>([])
  const [loading, setLoading] = useState(false)

  const refresh = useCallback(async () => {
    if (!firebaseUser) {
      setRiderRequests([])
      setDriverPending([])
      return
    }
    setLoading(true)
    try {
      const [mine, inbox] = await Promise.all([
        getMyRequests(),
        getDriverInbox(),
      ])
      setRiderRequests(mine)
      setDriverPending(inbox)
    } catch {
      // keep stale data on poll failure
    } finally {
      setLoading(false)
    }
  }, [firebaseUser])

  useEffect(() => {
    refresh()
  }, [refresh])

  const activeRiderTrip = useMemo(
    () =>
      riderRequests.find((r) =>
        ['pending', 'accepted'].includes(r.status)
      ) ?? null,
    [riderRequests]
  )

  const value = useMemo(
    () => ({
      riderRequests,
      driverPending,
      activeRiderTrip,
      loading,
      refresh,
    }),
    [riderRequests, driverPending, activeRiderTrip, loading, refresh]
  )

  return <TripContext.Provider value={value}>{children}</TripContext.Provider>
}

export function useTrips() {
  const ctx = useContext(TripContext)
  if (!ctx) throw new Error('useTrips must be used within TripProvider')
  return ctx
}
