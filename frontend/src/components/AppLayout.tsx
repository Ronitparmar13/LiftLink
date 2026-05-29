import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Home', icon: '🏠' },
  { path: '/find-ride', label: 'Find', icon: '🔍' },
  { path: '/offer-ride', label: 'Offer', icon: '🚗' },
  { path: '/my-offers', label: 'My Offers', icon: '📋' },
  { path: '/profile', label: 'Profile', icon: '👤' },
]

export function AppLayout() {
  const { profile, signOut } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  async function handleSignOut() {
    await signOut()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-950">
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/95 backdrop-blur">
        <div className="mx-auto flex max-w-lg items-center justify-between px-4 py-3">
          <Link to="/dashboard" className="text-lg font-bold text-white">
            LiftLink
          </Link>
          <div className="flex items-center gap-3">
            {profile?.photoUrl && (
              <img
                src={profile.photoUrl}
                alt=""
                className="h-8 w-8 rounded-full border border-slate-700"
              />
            )}
            <button
              type="button"
              onClick={handleSignOut}
              className="text-sm text-slate-400 hover:text-white"
            >
              Logout
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-lg flex-1 px-4 py-6 pb-20">
        <Outlet />
      </main>
      <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-slate-800 bg-slate-950/95 backdrop-blur md:hidden">
        <div className="mx-auto flex max-w-lg justify-around py-2">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center gap-0.5 px-3 py-1 text-xs ${
                  isActive ? 'text-cyan-400' : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            )
          })}
        </div>
      </nav>
    </div>
  )
}
