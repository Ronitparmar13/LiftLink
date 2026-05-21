import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { FuelSplitBadge, PaymentDisclaimer } from '../components/FuelSplitBadge'
import { useTrips } from '../contexts/TripContext'
import { useAuth } from '../contexts/AuthContext'
import {
  cancelRequest,
  completeRequest,
  getRequestDetail,
} from '../services/api'
import { getApiErrorMessage } from '../utils/errors'
import type { RequestDetail } from '../types/request'

const STATUS_LABELS: Record<string, string> = {
  pending: 'Waiting for driver',
  accepted: 'Confirmed',
  rejected: 'Declined',
  cancelled: 'Cancelled',
  completed: 'Completed',
}

export function RequestStatusPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { profile } = useAuth()
  const { refresh } = useTrips()
  const [detail, setDetail] = useState<RequestDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [acting, setActing] = useState(false)

  const load = useCallback(async () => {
    if (!id) return
    try {
      const data = await getRequestDetail(id)
      setDetail(data)
      setError(null)
    } catch (err) {
      setError(getApiErrorMessage(err))
    }
  }, [id])

  useEffect(() => {
    load()
    const interval = setInterval(load, 5000)
    return () => clearInterval(interval)
  }, [load])

  const isRider = detail && profile?.id === detail.rider.id
  const req = detail?.request
  const otherParty = isRider ? detail?.driver : detail?.rider
  const showContact = req?.status === 'accepted'

  async function handleCancel() {
    if (!id) return
    setActing(true)
    try {
      await cancelRequest(id)
      await refresh()
      await load()
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setActing(false)
    }
  }

  async function handleComplete() {
    if (!id) return
    setActing(true)
    try {
      await completeRequest(id)
      await refresh()
      await load()
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setActing(false)
    }
  }

  if (!detail || !req) {
    return (
      <div className="text-slate-400">
        {error ?? 'Loading trip…'}
        <button type="button" onClick={load} className="ml-2 text-cyan-400">
          Refresh
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <Link to="/dashboard" className="text-sm text-cyan-400 hover:underline">
        ← Dashboard
      </Link>

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Your ride</h1>
        <span
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            req.status === 'accepted'
              ? 'bg-emerald-900/50 text-emerald-400'
              : req.status === 'pending'
                ? 'bg-amber-900/50 text-amber-300'
                : 'bg-slate-800 text-slate-400'
          }`}
        >
          {STATUS_LABELS[req.status]}
        </span>
      </div>

      <section className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <p className="text-sm text-slate-400">Route</p>
        <p className="font-medium text-white">
          {req.pickupLabel} → {req.dropoffLabel}
        </p>
        <p className="mt-1 text-xs text-slate-500">
          Driver route: {detail.offer.startLabel} → {detail.offer.endLabel}
        </p>
        <p className="mt-2 text-xs text-slate-500">
          Departure {new Date(detail.offer.departureTime).toLocaleString()}
        </p>
        <div className="mt-4">
          <FuelSplitBadge
            distanceKm={req.riderDistanceKm}
            ratePerKm={detail.offer.fuelSplitRatePerKm}
            total={req.estimatedFuelSplitCost}
          />
        </div>
      </section>

      {showContact && otherParty && (
        <section className="rounded-xl border border-emerald-900/40 bg-emerald-950/20 p-4">
          <p className="text-sm text-emerald-400">Contact</p>
          <p className="font-semibold text-white">{otherParty.displayName}</p>
          {otherParty.phone && (
            <a
              href={`tel:${otherParty.phone}`}
              className="mt-1 block text-cyan-400"
            >
              {otherParty.phone}
            </a>
          )}
          {otherParty.email && (
            <p className="text-sm text-slate-400">{otherParty.email}</p>
          )}
          <PaymentDisclaimer />
        </section>
      )}

      {req.status === 'pending' && isRider && (
        <>
          <PaymentDisclaimer />
          <button
            type="button"
            onClick={handleCancel}
            disabled={acting}
            className="w-full rounded-xl border border-slate-700 py-3 text-slate-300 hover:bg-slate-800 disabled:opacity-60"
          >
            Cancel request
          </button>
        </>
      )}

      {req.status === 'accepted' && (
        <button
          type="button"
          onClick={handleComplete}
          disabled={acting}
          className="min-h-[48px] w-full rounded-xl bg-emerald-600 py-3 font-semibold text-white hover:bg-emerald-500 disabled:opacity-60"
        >
          {acting ? '…' : 'Mark ride complete'}
        </button>
      )}

      {req.status === 'rejected' && (
        <button
          type="button"
          onClick={() => navigate('/find-ride')}
          className="w-full rounded-xl bg-blue-600 py-3 font-semibold text-white"
        >
          Find another ride
        </button>
      )}

      {error && <p className="text-sm text-red-400">{error}</p>}

      <button
        type="button"
        onClick={load}
        className="text-sm text-slate-500 hover:text-slate-300"
      >
        Refresh status
      </button>
    </div>
  )
}
