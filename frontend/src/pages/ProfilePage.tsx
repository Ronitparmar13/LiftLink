import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { updateProfile } from '../services/api'
import { getApiErrorMessage } from '../utils/errors'
import type { UserRole } from '../types/user'

export function ProfilePage() {
  const { profile, refreshProfile } = useAuth()
  const [phone, setPhone] = useState(profile?.phone ?? '')
  const [role, setRole] = useState<UserRole>(profile?.role ?? 'both')
  const [vehicleType, setVehicleType] = useState(
    profile?.vehicle?.type ?? ''
  )
  const [vehicleDesc, setVehicleDesc] = useState(
    profile?.vehicle?.description ?? ''
  )
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    setMessage(null)
    try {
      await updateProfile({
        phone: phone || undefined,
        role,
        vehicle: vehicleType
          ? {
              type: vehicleType as 'two_wheeler' | 'car' | 'other',
              description: vehicleDesc || undefined,
            }
          : undefined,
      })
      await refreshProfile()
      setMessage('Profile saved.')
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <Link to="/dashboard" className="text-sm text-cyan-400 hover:underline">
        ← Dashboard
      </Link>
      <h1 className="text-2xl font-bold text-white">Profile</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block">
          <span className="text-sm text-slate-400">Phone (optional)</span>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white"
            placeholder="+91…"
          />
        </label>

        <label className="block">
          <span className="text-sm text-slate-400">Role</span>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white"
          >
            <option value="both">Both rider & driver</option>
            <option value="rider">Rider only</option>
            <option value="driver">Driver only</option>
          </select>
        </label>

        <label className="block">
          <span className="text-sm text-slate-400">Vehicle type</span>
          <select
            value={vehicleType}
            onChange={(e) => setVehicleType(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white"
          >
            <option value="">—</option>
            <option value="two_wheeler">Two wheeler</option>
            <option value="car">Car</option>
            <option value="other">Other</option>
          </select>
        </label>

        <label className="block">
          <span className="text-sm text-slate-400">Vehicle description</span>
          <input
            type="text"
            value={vehicleDesc}
            onChange={(e) => setVehicleDesc(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white"
            placeholder="e.g. White Activa"
          />
        </label>

        {error && (
          <p className="text-sm text-red-400">{error}</p>
        )}
        {message && (
          <p className="text-sm text-emerald-400">{message}</p>
        )}

        <button
          type="submit"
          disabled={saving}
          className="min-h-[44px] w-full rounded-xl bg-blue-600 py-3 font-semibold text-white hover:bg-blue-500 disabled:opacity-60"
        >
          {saving ? 'Saving…' : 'Save profile'}
        </button>
      </form>
    </div>
  )
}
