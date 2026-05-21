import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { getMyOffers } from '../services/api'
import { getApiErrorMessage } from '../utils/errors'
import type { RideOffer } from '../types/offer'

export function MyOffersPage() {
  const location = useLocation()
  const [offers, setOffers] = useState<RideOffer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const justCreated = (location.state as { created?: boolean })?.created

  useEffect(() => {
    getMyOffers()
      .then(setOffers)
      .catch((err) => setError(getApiErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

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

      {loading && <p className="text-slate-400">Loading…</p>}
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
                  offer.status === 'open'
                    ? 'bg-emerald-900/50 text-emerald-400'
                    : 'bg-slate-800 text-slate-400'
                }`}
              >
                {offer.status}
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
            {offer.status === 'open' && (
              <Link
                to={`/my-offers/${offer.id}/requests`}
                className="mt-2 inline-block text-sm text-cyan-400 hover:underline"
              >
                View ride requests →
              </Link>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
