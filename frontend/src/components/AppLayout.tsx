import { Link, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export function AppLayout() {
  const { profile, signOut } = useAuth()
  const navigate = useNavigate()

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
      <main className="mx-auto w-full max-w-lg flex-1 px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
