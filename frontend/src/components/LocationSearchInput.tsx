import { useEffect, useRef, useState } from 'react'
import { searchLocations } from '../services/api'
import { fromGeoPoint, type LatLng } from '../types/geo'
import type { PoiSearchResult } from '../types/location'

interface LocationSearchInputProps {
  label: string
  value: string
  placeholder?: string
  onLabelChange: (value: string) => void
  onSelect: (label: string, point: LatLng) => void
}

export function LocationSearchInput({
  label,
  value,
  placeholder,
  onLabelChange,
  onSelect,
}: LocationSearchInputProps) {
  const [results, setResults] = useState<PoiSearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const requestId = useRef(0)

  useEffect(() => {
    const query = value.trim()
    if (query.length < 2) {
      return
    }

    const current = ++requestId.current
    const timeout = window.setTimeout(async () => {
      setLoading(true)
      try {
        const res = await searchLocations(query)
        if (requestId.current === current) {
          setResults(res.results)
          setOpen(true)
        }
      } catch {
        if (requestId.current === current) setResults([])
      } finally {
        if (requestId.current === current) setLoading(false)
      }
    }, 300)

    return () => window.clearTimeout(timeout)
  }, [value])

  return (
    <label className="relative block">
      <span className="text-sm text-slate-400">{label}</span>
      <input
        value={value}
        onChange={(e) => {
          onLabelChange(e.target.value)
          setOpen(true)
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 200)}
        placeholder={placeholder}
        className="
          mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white
          transition-all duration-300 ease-out
          transform-gpu
          focus:outline-none
          focus:border-primary-500
          focus:ring-2 focus:ring-primary-500/20
          focus:translate-y-[-1px]
          focus:scale-101
          focus:drop-shadow-[0_4px_12px_-2px_rgba(59,130,246,0.3)]
        "
      />
      {open && value.trim().length >= 2 && (results.length > 0 || loading) && (
        <div className="
          absolute z-[1000] mt-2 max-h-60 w-full overflow-auto rounded-xl border border-slate-700 bg-slate-950/90 backdrop-blur-sm
          shadow-2xl
          transition-all duration-300 ease-out
          transform-gpu
        "
        >
          {loading && (
            <p className="px-4 py-3 text-sm text-slate-500">Searching…</p>
          )}
          {results.map((poi) => (
            <button
              key={poi.poiId}
              type="button"
              onMouseDown={(e) => {
                e.preventDefault()
                onSelect(poi.name, fromGeoPoint(poi.location))
                setOpen(false)
              }}
              className="
                block w-full px-4 py-3 text-left hover:bg-slate-800/70
                transition-all duration-200 ease-out
              "
            >
              <span className="block text-sm font-medium text-white">
                {poi.name}
              </span>
              <span className="text-xs text-slate-500">
                {poi.matchedAlias} · {poi.score}% match
              </span>
            </button>
          ))}
        </div>
      )}
    </label>
  )
}
