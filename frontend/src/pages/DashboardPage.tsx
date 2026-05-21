import { Link, useLocation } from 'react-router-dom'
import { ActiveTripWidget } from '../components/ActiveTripWidget'
import { TrendingHotspots } from '../components/TrendingHotspots'
import { useAuth } from '../contexts/AuthContext'

export function DashboardPage() {
  const { profile } = useAuth()
  const location = useLocation()
  const flash = (location.state as { message?: string })?.message

  return (
    <div className="space-y-6">
      {flash && (
        <p className="rounded-lg bg-emerald-950/50 p-3 text-sm text-emerald-400">
          {flash}
        </p>
      )}
      <div>
        <h1 className="text-2xl font-bold text-white">
          Hello, {profile?.displayName?.split(' ')[0] ?? 'there'}
        </h1>
        <p className="mt-1 text-sm text-slate-400">{profile?.email}</p>
      </div>

      <ActiveTripWidget />

      <div className="grid gap-4 sm:grid-cols-2">
        <Link
          to="/find-ride"
          className="rounded-2xl border border-slate-800 bg-slate-900 p-5 transition hover:border-cyan-700"
        >
          <span className="text-2xl">🚗</span>
          <h2 className="mt-2 font-semibold text-white">Find a Ride</h2>
          <p className="mt-1 text-sm text-slate-400">Match drivers on your route</p>
          <span className="mt-3 inline-block text-xs text-emerald-500">Ready</span>
        </Link>

        <Link
          to="/offer-ride"
          className="rounded-2xl border border-blue-800/50 bg-blue-950/30 p-5 transition hover:border-blue-600"
        >
          <span className="text-2xl">📍</span>
          <h2 className="mt-2 font-semibold text-white">Offer a Ride</h2>
          <p className="mt-1 text-sm text-slate-400">Share your route & seats</p>
        </Link>
      </div>

      <Link
        to="/my-offers"
        className="block rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-3 text-sm text-slate-300 hover:text-white"
      >
        View my published offers →
      </Link>

      <Link
        to="/profile"
        className="block rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-3 text-sm text-slate-300 hover:text-white"
      >
        Edit profile & vehicle →
      </Link>

      <TrendingHotspots />
    </div>
  )
}
