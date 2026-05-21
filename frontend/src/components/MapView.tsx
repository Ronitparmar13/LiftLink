import { useEffect } from 'react'
import {
  MapContainer,
  Marker,
  Polyline,
  TileLayer,
  useMap,
  useMapEvents,
} from 'react-leaflet'
import L from 'leaflet'
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'
import type { LatLng } from '../types/geo'
import { CAMPUS_CENTER } from '../types/geo'

import 'leaflet/dist/leaflet.css'

// Fix default marker icons with Vite
// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({ iconRetinaUrl, iconUrl, shadowUrl })

const startIcon = new L.Icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  className: 'hue-rotate-90',
})

export type PickMode = 'start' | 'end' | 'pickup' | 'dropoff' | null

export interface RouteOverlay {
  positions: [number, number][]
  color?: string
  weight?: number
  dashArray?: string
}

interface MapViewProps {
  pickMode: PickMode
  startPoint: LatLng | null
  endPoint: LatLng | null
  onPick: (mode: Exclude<PickMode, null>, point: LatLng) => void
  className?: string
  /** Extra driver routes (read-only) */
  routeOverlays?: RouteOverlay[]
}

const pickupIcon = new L.Icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  className: 'filter hue-rotate-60',
})

function MapClickHandler({
  pickMode,
  onPick,
}: {
  pickMode: PickMode
  onPick: (mode: Exclude<PickMode, null>, point: LatLng) => void
}) {
  useMapEvents({
    click(e) {
      if (!pickMode) return
      onPick(pickMode, { lat: e.latlng.lat, lng: e.latlng.lng })
    },
  })
  return null
}

function Recenter({ center }: { center: LatLng }) {
  const map = useMap()
  useEffect(() => {
    map.setView([center.lat, center.lng], map.getZoom())
  }, [center.lat, center.lng, map])
  return null
}

const PICK_LABELS: Record<Exclude<PickMode, null>, string> = {
  start: 'START',
  end: 'END',
  pickup: 'PICKUP',
  dropoff: 'DROPOFF',
}

export function MapView({
  pickMode,
  startPoint,
  endPoint,
  onPick,
  className = 'h-[50vh] min-h-[280px] w-full rounded-xl overflow-hidden border border-slate-700',
  routeOverlays = [],
}: MapViewProps) {
  const riderMode = pickMode === 'pickup' || pickMode === 'dropoff'
  const routePositions: [number, number][] = []
  if (startPoint) routePositions.push([startPoint.lat, startPoint.lng])
  if (endPoint) routePositions.push([endPoint.lat, endPoint.lng])

  return (
    <div className={className}>
      <MapContainer
        center={[CAMPUS_CENTER.lat, CAMPUS_CENTER.lng]}
        zoom={14}
        scrollWheelZoom
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Recenter center={CAMPUS_CENTER} />
        <MapClickHandler pickMode={pickMode} onPick={onPick} />
        {routeOverlays.map((overlay, i) => (
          <Polyline
            key={`overlay-${i}`}
            positions={overlay.positions}
            color={overlay.color ?? '#a78bfa'}
            weight={overlay.weight ?? 3}
            dashArray={overlay.dashArray ?? '6 8'}
          />
        ))}
        {startPoint && (
          <Marker
            position={[startPoint.lat, startPoint.lng]}
            icon={riderMode ? pickupIcon : startIcon}
          />
        )}
        {endPoint && (
          <Marker position={[endPoint.lat, endPoint.lng]} />
        )}
        {!riderMode && routePositions.length >= 2 && (
          <Polyline positions={routePositions} color="#22d3ee" weight={4} />
        )}
        {riderMode && routePositions.length >= 2 && (
          <Polyline
            positions={routePositions}
            color="#f472b6"
            weight={3}
            dashArray="4 6"
          />
        )}
      </MapContainer>
      {pickMode && (
        <p className="mt-2 text-center text-xs text-cyan-400">
          Tap map to set {PICK_LABELS[pickMode]} point
        </p>
      )}
    </div>
  )
}
