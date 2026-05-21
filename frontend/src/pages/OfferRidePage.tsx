import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { LocationSearchInput } from '../components/LocationSearchInput'
import { MapView, type PickMode } from '../components/MapView'
import { createOffer } from '../services/api'
import { getApiErrorMessage } from '../utils/errors'
import type { LatLng } from '../types/geo'
import { toGeoPoint } from '../types/geo'

export function OfferRidePage() {
  const navigate = useNavigate()
  const [pickMode, setPickMode] = useState<PickMode>('start')
  const [startPoint, setStartPoint] = useState<LatLng | null>(null)
  const [endPoint, setEndPoint] = useState<LatLng | null>(null)
  const [startLabel, setStartLabel] = useState('')
  const [endLabel, setEndLabel] = useState('')
  const [departureTime, setDepartureTime] = useState('')
  const [availableSeats, setAvailableSeats] = useState(1)
  const [notes, setNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function handlePick(
    mode: 'start' | 'end' | 'pickup' | 'dropoff',
    point: LatLng
  ) {
    if (mode === 'start') setStartPoint(point)
    else if (mode === 'end') setEndPoint(point)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    if (!startPoint || !endPoint) {
      setError('Set both start and end points on the map.')
      return
    }
    if (!startLabel.trim() || !endLabel.trim()) {
      setError('Enter labels for start and end locations.')
      return
    }
    if (!departureTime) {
      setError('Choose a departure time.')
      return
    }

    const startGeo = toGeoPoint(startPoint)
    const endGeo = toGeoPoint(endPoint)

    setSubmitting(true)
    try {
      await createOffer({
        startPoint: startGeo,
        endPoint: endGeo,
        route: {
          type: 'LineString',
          coordinates: [startGeo.coordinates, endGeo.coordinates],
        },
        startLabel: startLabel.trim(),
        endLabel: endLabel.trim(),
        departureTime: new Date(departureTime).toISOString(),
        availableSeats,
        notes: notes.trim(),
      })
      navigate('/my-offers', { state: { created: true } })
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-5">
      <Link to="/dashboard" className="text-sm text-cyan-400 hover:underline">
        ← Dashboard
      </Link>
      <h1 className="text-2xl font-bold text-white">Offer a Ride</h1>

      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setPickMode('start')}
          className={`flex-1 rounded-lg py-2 text-sm font-medium ${
            pickMode === 'start'
              ? 'bg-emerald-600 text-white'
              : 'bg-slate-800 text-slate-400'
          }`}
        >
          Set Start {startPoint ? '✓' : ''}
        </button>
        <button
          type="button"
          onClick={() => setPickMode('end')}
          className={`flex-1 rounded-lg py-2 text-sm font-medium ${
            pickMode === 'end'
              ? 'bg-rose-600 text-white'
              : 'bg-slate-800 text-slate-400'
          }`}
        >
          Set End {endPoint ? '✓' : ''}
        </button>
      </div>

      <MapView
        pickMode={pickMode}
        startPoint={startPoint}
        endPoint={endPoint}
        onPick={handlePick}
      />

      <form onSubmit={handleSubmit} className="space-y-4">
        <LocationSearchInput
          label="Start label"
          value={startLabel}
          onLabelChange={setStartLabel}
          placeholder="e.g. Uni Gate"
          onSelect={(label, point) => {
            setStartLabel(label)
            setStartPoint(point)
          }}
        />
        <LocationSearchInput
          label="End label"
          value={endLabel}
          onLabelChange={setEndLabel}
          placeholder="e.g. Alkapuri"
          onSelect={(label, point) => {
            setEndLabel(label)
            setEndPoint(point)
          }}
        />
        <label className="block">
          <span className="text-sm text-slate-400">Departure time</span>
          <input
            type="datetime-local"
            required
            value={departureTime}
            onChange={(e) => setDepartureTime(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white"
          />
        </label>
        <label className="block">
          <span className="text-sm text-slate-400">Available seats</span>
          <input
            type="number"
            min={1}
            max={6}
            value={availableSeats}
            onChange={(e) => setAvailableSeats(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white"
          />
        </label>
        <label className="block">
          <span className="text-sm text-slate-400">Notes (optional)</span>
          <input
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            maxLength={200}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white"
          />
        </label>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="min-h-[48px] w-full rounded-xl bg-blue-600 py-3 font-semibold text-white hover:bg-blue-500 disabled:opacity-60"
        >
          {submitting ? 'Publishing…' : 'Publish ride offer'}
        </button>
      </form>
    </div>
  )
}
