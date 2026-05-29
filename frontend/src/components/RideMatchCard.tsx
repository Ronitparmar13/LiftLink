import { FuelSplitBadge } from './FuelSplitBadge'
import type { MatchResult } from '../types/match'
import Button3D from '../components/Button3D'

interface RideMatchCardProps {
  match: MatchResult
  onRequest?: () => void
  requesting?: boolean
}

export function RideMatchCard({
  match,
  onRequest,
  requesting,
}: RideMatchCardProps) {
  const { offer, driver } = match

  return (
    <li className="rounded-xl border border-slate-800 bg-slate-900 p-4">
      <div className="flex items-start gap-3">
        {driver.photoUrl ? (
          <img
            src={driver.photoUrl}
            alt=""
            className="h-10 w-10 rounded-full border border-slate-700"
          />
        ) : (
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-800 text-sm text-slate-400">
            {driver.displayName.charAt(0)}
          </div>
        )}
        <div className="min-w-0 flex-1">
          <p className="font-semibold text-white">{driver.displayName}</p>
          {driver.vehicle?.description && (
            <p className="text-xs text-slate-500">{driver.vehicle.description}</p>
          )}
          <p className="mt-1 text-sm text-slate-300">
            {offer.startLabel} → {offer.endLabel}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {new Date(offer.departureTime).toLocaleString()} ·{' '}
            {offer.availableSeats} seat(s)
          </p>
        </div>
        <span className="rounded bg-cyan-900/40 px-2 py-0.5 text-xs text-cyan-400">
          {Math.round(match.matchScore * 100)}% match
        </span>
      </div>

       <div className="mt-3 flex items-center justify-between border-t border-slate-800 pt-3">
         <FuelSplitBadge
           distanceKm={match.riderDistanceKm}
           ratePerKm={offer.fuelSplitRatePerKm}
           total={match.estimatedFuelSplitCost}
         />
         {onRequest && (
           <Button3D
             variant="primary"
             size="md"
             onClick={onRequest}
             disabled={requesting}
             className="min-h-[40px]"
           >
             {requesting ? '…' : 'Request Ride'}
           </Button3D>
         )}
       </div>
    </li>
  )
}
