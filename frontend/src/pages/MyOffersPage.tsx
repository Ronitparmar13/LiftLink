import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { cancelOffer, getMyOffers } from '../services/api'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { getApiErrorMessage } from '../utils/errors'
import { ListSkeleton } from '../components/Skeleton'
import type { RideOffer } from '../types/offer'

const STATUS_COLORS: Record<string, string> = {
  open: 'bg-emerald-900/50 text-emerald-400',
  full: 'bg-amber-900/50 text-amber-400',
  in_progress: 'bg-blue-900/50 text-blue-400',
  completed: 'bg-slate-800 text-slate-400',
  cancelled: 'bg-red-900/50 text-red-400',
}

export function MyOffersPage() {
  const location = useLocation()
  const [offers, setOffers] = useState<RideOffer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [cancellingId, setCancellingId] = useState<string | null>(null)
  const [confirmCancelId, setConfirmCancelId] = useState<string | null>(null)
  const justCreated = (location.state as { created?: boolean })?.created

  useEffect(() => {
    getMyOffers()
      .then(setOffers)
      .catch((err) => setError(getApiErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  async function handleCancel(offerId: string) {
    setCancellingId(offerId)
    try {
      await cancelOffer(offerId)
      setOffers((prev) =>
        prev.map((o) => (o.id === offerId ? { ...o, status: 'cancelled' } : o))
      )
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setCancellingId(null)
    }
  }

  return (
    <div className="space-y-5">
      <Link to="/dashboard" className="text-sm text-cyan-400 hover:underline">
        ← Dashboard
      </Link>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">My Offers</h1>
        <Link
          to="/offer-ride"
          className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white"
        >
          + New
        </Link>
      </div>

      {justCreated && (
        <p className="rounded-lg bg-emerald-950/50 p-3 text-sm text-emerald-400">
          Ride offer published successfully.
        </p>
      )}

      {loading && <ListSkeleton count={3} />}
      {error && <p className="text-red-400">{error}</p>}

      {!loading && !error && offers.length === 0 && (
        <p className="text-slate-500">No offers yet. Publish your first ride.</p>
      )}

      <ul className="space-y-3">
        {offers.map((offer) => (
          <li
            key={offer.id}
            className="rounded-xl border border-slate-800 bg-slate-900 p-4"
          >
            <div className="flex justify-between text-sm">
              <span className="font-medium text-white">
                {offer.startLabel} → {offer.endLabel}
              </span>
              <span
                className={`rounded px-2 py-0.5 text-xs ${
                  STATUS_COLORS[offer.status] ?? 'bg-slate-800 text-slate-400'
                }`}
              >
                {offer.status.replace('_', ' ')}
              </span>
            </div>
            <p className="mt-2 text-xs text-slate-400">
              {new Date(offer.departureTime).toLocaleString()} ·{' '}
              {offer.availableSeats} seat(s) · ₹{offer.estimatedFuelSplitTotal}{' '}
              est.
            </p>
            <p className="mt-1 text-xs text-slate-500">
              {offer.estimatedDistanceKm} km route
            </p>
            <div className="mt-3 flex gap-2">
              {offer.status === 'open' && (
                <Link
                  to={`/my-offers/${offer.id}/requests`}
                  className="flex-1 rounded-lg border border-slate-700 py-2 text-center text-sm text-cyan-400 hover:bg-slate-800"
                >
                  View requests
                </Link>
              )}
              {offer.status === 'open' && (
                <button
                  type="button"
                  onClick={() => setConfirmCancelId(offer.id)}
                  disabled={cancellingId === offer.id}
                  className="flex-1 rounded-lg border border-red-800 py-2 text-sm text-red-400 hover:bg-red-950 disabled:opacity-60"
                >
                  {cancellingId === offer.id ? 'Cancelling…' : 'Cancel'}
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>

      <ConfirmDialog
        open={confirmCancelId !== null}
        title="Cancel ride offer?"
        message="This action cannot be undone. The offer will be marked as cancelled."
        confirmLabel="Cancel offer"
        onConfirm={() => {
          if (confirmCancelId) void handleCancel(confirmCancelId)
          setConfirmCancelId(null)
        }}
        onCancel={() => setConfirmCancelId(null)}
      />
    </div>
  )
}
