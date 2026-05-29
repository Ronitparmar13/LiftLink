import { useEffect, useState } from 'react'
import { getTrendingHotspots, refreshHotspots } from '../services/api'
import type { TrendingHotspotsResponse } from '../types/hotspot'
import { ListSkeleton } from './Skeleton'

export function TrendingHotspots() {
  const [data, setData] = useState<TrendingHotspotsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  async function load() {
    try {
      setData(await getTrendingHotspots())
    } catch {
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const id = window.setTimeout(() => {
      void load()
    }, 0)
    return () => window.clearTimeout(id)
  }, [])

  async function handleRefresh() {
    setRefreshing(true)
    try {
      await refreshHotspots()
      await load()
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <section className="space-y-3 border-t border-slate-800 pt-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-semibold text-white">Trending pickup zones</h2>
          <p className="text-xs text-slate-500">
            {data?.sampleSize ? `${data.sampleSize} recent rides analyzed` : 'K-Means demand clusters'}
          </p>
        </div>
        <button
          type="button"
          onClick={handleRefresh}
          disabled={refreshing}
          className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs text-slate-300 disabled:opacity-60"
        >
          {refreshing ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      {loading && <ListSkeleton count={2} />}

      {!loading && (!data || data.zones.length === 0) && (
        <p className="rounded-xl border border-dashed border-slate-700 p-4 text-center text-sm text-slate-500">
          Add accepted or completed requests, then refresh hotspots.
        </p>
      )}

      {data && data.zones.length > 0 && (
        <div className="grid gap-3">
          {data.zones.map((zone) => (
            <div
              key={`${zone.label}-${zone.centroid.join(',')}`}
              className="rounded-xl border border-slate-800 bg-slate-900 p-4"
            >
              <div className="flex items-center justify-between gap-3">
                <p className="font-medium text-white">{zone.label}</p>
                <span className="rounded bg-cyan-900/40 px-2 py-0.5 text-xs text-cyan-400">
                  {zone.requestCount} rides
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-500">
                {zone.centroid[1].toFixed(4)}, {zone.centroid[0].toFixed(4)}
              </p>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
