import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { FuelSplitBadge } from '../components/FuelSplitBadge'
import { ListSkeleton } from '../components/Skeleton'
import { useTrips } from '../contexts/TripContext'
import {
  acceptRequest,
  getOfferRequests,
  rejectRequest,
} from '../services/api'
import { getApiErrorMessage } from '../utils/errors'
import type { RideRequest } from '../types/request'

export function OfferInboxPage() {
  const { offerId } = useParams<{ offerId: string }>()
  const { refresh } = useTrips()
  const [requests, setRequests] = useState<RideRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actingId, setActingId] = useState<string | null>(null)
  const [confirmRejectId, setConfirmRejectId] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!offerId) return
    setLoading(true)
    try {
      const data = await getOfferRequests(offerId)
      setRequests(data)
      setError(null)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }, [offerId])

  useEffect(() => {
    load()
  }, [load])

  async function handleAccept(requestId: string) {
    setActingId(requestId)
    try {
      await acceptRequest(requestId)
      await refresh()
      await load()
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setActingId(null)
    }
  }

  async function handleReject(requestId: string) {
    setActingId(requestId)
    try {
      await rejectRequest(requestId)
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
      <Link to="/my-offers" className="text-sm text-cyan-400 hover:underline">
        ← My offers
      </Link>
      <h1 className="text-2xl font-bold text-white">Ride requests</h1>

      {loading && <ListSkeleton count={3} />}
      {error && <p className="text-red-400">{error}</p>}

      {!loading && requests.length === 0 && (
        <p className="text-slate-500">No requests for this offer yet.</p>
      )}

      <ul className="space-y-3">
        {requests.map((req) => (
          <li
            key={req.id}
            className="rounded-xl border border-slate-800 bg-slate-900 p-4"
          >
            <div className="flex justify-between">
              <p className="font-medium text-white">
                {req.pickupLabel} → {req.dropoffLabel}
              </p>
              <span className="text-xs text-slate-500">{req.status}</span>
            </div>
            <FuelSplitBadge
              className="mt-2"
              distanceKm={req.riderDistanceKm}
              ratePerKm={req.estimatedFuelSplitCost / req.riderDistanceKm}
              total={req.estimatedFuelSplitCost}
            />
            {req.status === 'pending' && (
              <div className="mt-3 flex gap-2">
                <button
                  type="button"
                  onClick={() => handleAccept(req.id)}
                  disabled={actingId === req.id}
                  className="flex-1 rounded-lg bg-emerald-600 py-2 text-sm font-semibold text-white disabled:opacity-60"
                >
                  Accept
                </button>
                <button
                  type="button"
                  onClick={() => setConfirmRejectId(req.id)}
                  disabled={actingId === req.id}
                  className="flex-1 rounded-lg border border-slate-600 py-2 text-sm text-slate-300 disabled:opacity-60"
                >
                  Reject
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>

      <ConfirmDialog
        open={confirmRejectId !== null}
        title="Reject ride request?"
        message="The rider will be notified that their request was declined."
        confirmLabel="Reject"
        onConfirm={() => {
          if (confirmRejectId) void handleReject(confirmRejectId)
          setConfirmRejectId(null)
        }}
        onCancel={() => setConfirmRejectId(null)}
      />
    </div>
  )
}
