interface FuelSplitBadgeProps {
  distanceKm: number
  ratePerKm: number
  total: number
  className?: string
}

export function FuelSplitBadge({
  distanceKm,
  ratePerKm,
  total,
  className = '',
}: FuelSplitBadgeProps) {
  return (
    <div className={className}>
      <p className="text-lg font-bold text-emerald-400">₹{total}</p>
      <p className="text-xs text-slate-500" title="Fuel-split estimate (~50% of cab fare)">
        {distanceKm} km × ₹{ratePerKm}/km = ₹{total}
      </p>
    </div>
  )
}

export function PaymentDisclaimer() {
  return (
    <p className="rounded-lg border border-amber-900/40 bg-amber-950/30 px-3 py-2 text-xs text-amber-200/90">
      Payment via cash or UPI off-app after the ride (not processed in LiftLink).
    </p>
  )
}
