import { useNavigate } from 'react-router-dom';
import { TrendingHotspots } from '@/components/TrendingHotspots';
import Button3D from '@/components/Button3D';
import Panel3D from '@/components/Panel3D';

export function DashboardPage() {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <Panel3D elevation={3} className="p-6">
        <h2 className="text-xl font-bold mb-4">Trending Pickup Zones</h2>
        <TrendingHotspots />
      </Panel3D>

      <div className="grid gap-4 md:grid-cols-2">
        <Panel3D elevation={2} className="p-6 text-center">
          <h3 className="font-semibold mb-3">Find a Ride</h3>
          <p className="text-muted-foreground mb-4">
            Search for available rides along your route
          </p>
          <Button3D variant="primary" size="lg" onClick={() => navigate('/find-ride')}>
            Find a Ride
          </Button3D>
        </Panel3D>

        <Panel3D elevation={2} className="p-6 text-center">
          <h3 className="font-semibold mb-3">Offer a Ride</h3>
          <p className="text-muted-foreground mb-4">
            Share your vehicle and split fuel costs
          </p>
          <Button3D variant="secondary" size="lg" onClick={() => navigate('/offer-ride')}>
            Offer a Ride
          </Button3D>
        </Panel3D>
      </div>

      <Panel3D elevation={3} className="p-6">
        <h2 className="text-xl font-bold mb-4">Active Trip</h2>
        <div className="space-y-4">
          {/* Active trip widget would go here */}
          <p className="text-muted-foreground">No active trip</p>
        </div>
      </Panel3D>
    </div>
  );
}