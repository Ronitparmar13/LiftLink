import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FuelSplitBadge } from '../components/FuelSplitBadge'
import { acceptRequest, getDriverInbox, rejectRequest } from '../services/api'
import { getApiErrorMessage } from '../utils/errors'
import { useTrips } from '../contexts/TripContext'
import type { RideRequest } from '../types/request'

export function DriverInboxPage() {
  const { refresh } = useTrips()
  const [requests, setRequests] = useState<RideRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actingId, setActingId] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    try {
      setRequests(await getDriverInbox())
      setError(null)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function handleAccept(id: string) {
    setActingId(id)
    try {
      await acceptRequest(id)
      await refresh()
      await load()
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setActingId(null)
    }
  }

  async function handleReject(id: string) {
    setActingId(id)
    try {
      await rejectRequest(id)
      await refresh()
      await load()
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setActingId(null)
    }
  }

  return (
    <div className="space-y-5">
      <Link to="/dashboard" className="text-sm text-cyan-400 hover:underline">
        ← Dashboard
      </Link>
      <h1 className="text-2xl font-bold text-white">Driver inbox</h1>

      {loading && <p className="text-slate-400">Loading…</p>}
      {error && <p className="text-red-400">{error}</p>}
      {!loading && requests.length === 0 && (
        <p className="text-slate-500">No pending requests.</p>
      )}

      <ul className="space-y-3">
        {requests.map((req) => (
          <li
            key={req.id}
            className="rounded-xl border border-slate-800 bg-slate-900 p-4"
          >
            <p className="font-medium text-white">
              {req.pickupLabel} → {req.dropoffLabel}
            </p>
            <FuelSplitBadge
              className="mt-2"
              distanceKm={req.riderDistanceKm}
              ratePerKm={
                Math.round((req.estimatedFuelSplitCost / req.riderDistanceKm) * 10) /
                10
              }
              total={req.estimatedFuelSplitCost}
            />
            <div className="mt-3 flex gap-2">
              <button
                type="button"
                onClick={() => handleAccept(req.id)}
                disabled={actingId === req.id}
                className="flex-1 rounded-lg bg-emerald-600 py-2 text-sm font-semibold text-white"
              >
                Accept
              </button>
              <button
                type="button"
                onClick={() => handleReject(req.id)}
                disabled={actingId === req.id}
                className="flex-1 rounded-lg border border-slate-600 py-2 text-sm text-slate-300"
              >
                Reject
              </button>
            </div>
            <Link
              to={`/my-offers/${req.offerId}/requests`}
              className="mt-2 block text-xs text-slate-500 hover:text-cyan-400"
            >
              View offer →
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
