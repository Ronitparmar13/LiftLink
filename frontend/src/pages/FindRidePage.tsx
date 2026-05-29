import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { PaymentDisclaimer } from '../components/FuelSplitBadge'
import { LocationSearchInput } from '../components/LocationSearchInput'
import { MapView, type PickMode, type RouteOverlay } from '../components/MapView'
import { RideMatchCard } from '../components/RideMatchCard'
import Button3D from '../components/Button3D'
import { matchOffers, createRequest } from '../services/api'
import { getApiErrorMessage } from '../utils/errors'
import type { LatLng } from '../types/geo'
import { toGeoPoint } from '../types/geo'
import type { MatchResult } from '../types/match'

function defaultDepartureWindow() {
  const now = new Date()
  const after = now.toISOString().slice(0, 16)
  const before = new Date(now.getTime() + 4 * 60 * 60 * 1000)
    .toISOString()
    .slice(0, 16)
  return { after, before }
}

export function FindRidePage() {
  const navigate = useNavigate()
  const defaults = defaultDepartureWindow()
  const [pickMode, setPickMode] = useState<PickMode>('pickup')
  const [pickupPoint, setPickupPoint] = useState<LatLng | null>(null)
  const [dropoffPoint, setDropoffPoint] = useState<LatLng | null>(null)
  const [pickupLabel, setPickupLabel] = useState('')
  const [dropoffLabel, setDropoffLabel] = useState('')
  const [departureAfter, setDepartureAfter] = useState(defaults.after)
  const [departureBefore, setDepartureBefore] = useState(defaults.before)
  const [matches, setMatches] = useState<MatchResult[]>([])
  const [matchRadius, setMatchRadius] = useState(500)
  const [searching, setSearching] = useState(false)
  const [requestingId, setRequestingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [searched, setSearched] = useState(false)

  const routeOverlays: RouteOverlay[] = useMemo(
    () =>
      matches.map((m) => ({
        positions: m.offer.route.coordinates.map(
          ([lng, lat]) => [lat, lng] as [number, number]
        ),
        color: '#a78bfa',
        weight: 3,
        dashArray: '6 8',
      })),
    [matches]
  )

  function handlePick(mode: Exclude<PickMode, null>, point: LatLng) {
    if (mode === 'pickup') setPickupPoint(point)
    else if (mode === 'dropoff') setDropoffPoint(point)
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSearched(true)

    if (!pickupPoint || !dropoffPoint) {
      setError('Set pickup and dropoff on the map.')
      return
    }

    setSearching(true)
    setMatches([])
    try {
      const res = await matchOffers({
        pickup: toGeoPoint(pickupPoint),
        dropoff: toGeoPoint(dropoffPoint),
        pickupLabel: pickupLabel.trim() || 'Pickup',
        dropoffLabel: dropoffLabel.trim() || 'Dropoff',
        departureAfter: new Date(departureAfter).toISOString(),
        departureBefore: new Date(departureBefore).toISOString(),
      })
      setMatches(res.matches)
      setMatchRadius(res.matchRadiusMeters)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setSearching(false)
    }
  }

  async function handleRequest(match: MatchResult) {
    if (!pickupPoint || !dropoffPoint) return
    setRequestingId(match.offer.id)
    setError(null)
    try {
      const created = await createRequest({
        offerId: match.offer.id,
        pickup: toGeoPoint(pickupPoint),
        dropoff: toGeoPoint(dropoffPoint),
        pickupLabel: pickupLabel.trim() || 'Pickup',
        dropoffLabel: dropoffLabel.trim() || 'Dropoff',
      })
      navigate(`/requests/${created.id}`)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setRequestingId(null)
    }
  }

  return (
    <div className="space-y-5">
      <Link to="/dashboard" className="text-sm text-cyan-400 hover:underline">
        ← Dashboard
      </Link>
      <h1 className="text-2xl font-bold text-white">Find a Ride</h1>
      <p className="text-sm text-slate-400">
        Matches drivers whose route passes within {matchRadius}m of your pickup
        and dropoff.
      </p>

       <div className="flex gap-2">
         <Button3D
           variant={pickMode === 'pickup' ? 'secondary' : 'outline'}
           size="md"
           onClick={() => setPickMode('pickup')}
           className="flex-1"
         >
           Pickup {pickupPoint ? '✓' : ''}
         </Button3D>
         <Button3D
           variant={pickMode === 'dropoff' ? 'secondary' : 'outline'}
           size="md"
           onClick={() => setPickMode('dropoff')}
           className="flex-1"
         >
           Dropoff {dropoffPoint ? '✓' : ''}
         </Button3D>
       </div>

      <MapView
        pickMode={pickMode}
        startPoint={pickupPoint}
        endPoint={dropoffPoint}
        onPick={handlePick}
        routeOverlays={routeOverlays}
      />

      <form onSubmit={handleSearch} className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <LocationSearchInput
            label="Pickup label"
            value={pickupLabel}
            onLabelChange={setPickupLabel}
            placeholder="e.g. Uni Gate"
            onSelect={(label, point) => {
              setPickupLabel(label)
              setPickupPoint(point)
            }}
          />
          <LocationSearchInput
            label="Dropoff label"
            value={dropoffLabel}
            onLabelChange={setDropoffLabel}
            placeholder="e.g. Sayajigunj"
            onSelect={(label, point) => {
              setDropoffLabel(label)
              setDropoffPoint(point)
            }}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <label className="block">
            <span className="text-xs text-slate-400">From</span>
            <input
              type="datetime-local"
              value={departureAfter}
              onChange={(e) => setDepartureAfter(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-2 py-2 text-sm text-white"
            />
          </label>
          <label className="block">
            <span className="text-xs text-slate-400">Until</span>
            <input
              type="datetime-local"
              value={departureBefore}
              onChange={(e) => setDepartureBefore(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-2 py-2 text-sm text-white"
            />
          </label>
        </div>

        <Button3D
          variant="primary"
          size="lg"
          type="submit"
          disabled={searching}
          className="w-full"
        >
          {searching ? 'Searching…' : 'Search matching rides'}
        </Button3D>
      </form>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {searched && !searching && matches.length === 0 && !error && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 text-center">
          <p className="text-slate-300">No drivers on your route right now.</p>
          <p className="mt-2 text-sm text-slate-500">
            Try widening the time window or check again later.
          </p>
        </div>
      )}

      {matches.length > 0 && (
        <>
          <PaymentDisclaimer />
          <ul className="space-y-3">
          {matches.map((m) => (
            <RideMatchCard
              key={m.offer.id}
              match={m}
              onRequest={() => handleRequest(m)}
              requesting={requestingId === m.offer.id}
            />
          ))}
          </ul>
        </>
      )}
    </div>
  )
}
