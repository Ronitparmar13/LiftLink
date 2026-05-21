import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth, isFirebaseConfigured } from '../contexts/AuthContext'
import { ALLOWED_EMAIL_DOMAIN } from '../services/firebase'
import { checkHealth } from '../services/api'
import { useState } from 'react'

export function LoginPage() {
  const { firebaseUser, loading, error, signInWithGoogle, clearError } = useAuth()
  const navigate = useNavigate()
  const [signingIn, setSigningIn] = useState(false)
  const [apiOk, setApiOk] = useState<boolean | null>(null)

  useEffect(() => {
    if (!loading && firebaseUser) {
      navigate('/dashboard', { replace: true })
    }
  }, [firebaseUser, loading, navigate])

  useEffect(() => {
    checkHealth()
      .then(() => setApiOk(true))
      .catch(() => setApiOk(false))
  }, [])

  async function handleSignIn() {
    clearError()
    setSigningIn(true)
    try {
      await signInWithGoogle()
    } catch {
      // error set in context or popup cancelled
    } finally {
      setSigningIn(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 py-8">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/90 p-8 shadow-xl">
        <p className="text-center text-sm font-medium uppercase tracking-wider text-cyan-400">
          Parul University
        </p>
        <h1 className="mt-2 text-center text-3xl font-bold text-white">LiftLink</h1>
        <p className="mt-2 text-center text-sm text-slate-400">
          Campus ride-pooling for @{ALLOWED_EMAIL_DOMAIN}
        </p>

        {apiOk === false && (
          <p className="mt-4 rounded-lg bg-amber-950/50 p-3 text-sm text-amber-300">
            Backend offline. Start API on port 8000 first.
          </p>
        )}

        {error && (
          <p className="mt-4 rounded-lg bg-red-950/50 p-3 text-sm text-red-300">{error}</p>
        )}

        {!isFirebaseConfigured() ? (
          <p className="mt-6 text-sm text-slate-500">
            Add <code className="text-cyan-400">VITE_FIREBASE_*</code> to{' '}
            <code className="text-cyan-400">frontend/.env</code> (see docs/SETUP_FIREBASE.md).
          </p>
        ) : (
          <button
            type="button"
            onClick={handleSignIn}
            disabled={signingIn || loading}
            className="mt-8 flex min-h-[48px] w-full items-center justify-center gap-2 rounded-xl bg-white px-4 py-3 text-base font-semibold text-slate-900 transition hover:bg-slate-100 disabled:opacity-60"
          >
            {signingIn ? 'Signing in…' : 'Sign in with Google'}
          </button>
        )}

        <p className="mt-6 text-center text-xs text-slate-600">
          Only official university Google accounts are accepted.
        </p>
      </div>
    </div>
  )
}
