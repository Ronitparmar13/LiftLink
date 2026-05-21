import { Link } from 'react-router-dom'
import { useTrips } from '../contexts/TripContext'

export function ActiveTripWidget() {
  const { activeRiderTrip, driverPending, refresh, loading } = useTrips()

  if (!activeRiderTrip && driverPending.length === 0) return null

  return (
    <section className="space-y-3 rounded-xl border border-cyan-900/40 bg-cyan-950/20 p-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-cyan-400">Active trips</h2>
        <button
          type="button"
          onClick={() => refresh()}
          disabled={loading}
          className="text-xs text-slate-500 hover:text-slate-300"
        >
          Refresh
        </button>
      </div>

      {activeRiderTrip && (
        <Link
          to={`/requests/${activeRiderTrip.id}`}
          className="block rounded-lg bg-slate-900/80 px-3 py-2 hover:bg-slate-800"
        >
          <p className="text-sm font-medium text-white">
            Your request · {activeRiderTrip.status}
          </p>
          <p className="text-xs text-slate-400">
            {activeRiderTrip.pickupLabel} → {activeRiderTrip.dropoffLabel}
          </p>
        </Link>
      )}

      {driverPending.length > 0 && (
        <div>
          <p className="text-xs text-slate-500">
            {driverPending.length} pending request(s) on your offers
          </p>
          <Link
            to="/driver-inbox"
            className="mt-1 inline-block text-sm text-cyan-400 hover:underline"
          >
            Review requests →
          </Link>
        </div>
      )}
    </section>
  )
}
