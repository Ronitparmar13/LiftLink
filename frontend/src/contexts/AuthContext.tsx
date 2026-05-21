import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithPopup,
  signOut as firebaseSignOut,
  type User,
} from 'firebase/auth'
import { ALLOWED_EMAIL_DOMAIN, getFirebaseAuth, isFirebaseConfigured } from '../services/firebase'
import { setAuthToken, setTokenRefresher, syncUser } from '../services/api'
import type { UserProfile } from '../types/user'
import { getApiErrorMessage } from '../utils/errors'

interface AuthContextValue {
  firebaseUser: User | null
  profile: UserProfile | null
  loading: boolean
  error: string | null
  signInWithGoogle: () => Promise<void>
  signOut: () => Promise<void>
  refreshProfile: () => Promise<void>
  clearError: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

function isAllowedEmail(email: string | null | undefined): boolean {
  return Boolean(email?.toLowerCase().endsWith(`@${ALLOWED_EMAIL_DOMAIN}`))
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [firebaseUser, setFirebaseUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refreshToken = useCallback(async (): Promise<string | null> => {
    const auth = getFirebaseAuth()
    if (!auth?.currentUser) return null
    return auth.currentUser.getIdToken(true)
  }, [])

  useEffect(() => {
    setTokenRefresher(refreshToken)
  }, [refreshToken])

  const refreshProfile = useCallback(async () => {
    const data = await syncUser()
    setProfile(data)
  }, [])

  useEffect(() => {
    const auth = getFirebaseAuth()
    if (!auth) {
      setLoading(false)
      return
    }

    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setLoading(true)
      setError(null)

      if (!user) {
        setFirebaseUser(null)
        setProfile(null)
        setAuthToken(null)
        setLoading(false)
        return
      }

      if (!isAllowedEmail(user.email)) {
        await firebaseSignOut(auth)
        setFirebaseUser(null)
        setProfile(null)
        setAuthToken(null)
        setError(`Only @${ALLOWED_EMAIL_DOMAIN} email addresses can use LiftLink.`)
        setLoading(false)
        return
      }

      try {
        const token = await user.getIdToken()
        setAuthToken(token)
        setFirebaseUser(user)
        const synced = await syncUser()
        setProfile(synced)
      } catch (err) {
        setError(getApiErrorMessage(err))
        await firebaseSignOut(auth)
        setFirebaseUser(null)
        setProfile(null)
        setAuthToken(null)
      } finally {
        setLoading(false)
      }
    })

    return () => unsubscribe()
  }, [])

  const signInWithGoogle = useCallback(async () => {
    setError(null)
    const auth = getFirebaseAuth()
    if (!auth) {
      setError('Firebase is not configured. Add VITE_FIREBASE_* to frontend/.env')
      return
    }
    const provider = new GoogleAuthProvider()
    provider.setCustomParameters({ hd: ALLOWED_EMAIL_DOMAIN })
    const result = await signInWithPopup(auth, provider)
    if (!isAllowedEmail(result.user.email)) {
      await firebaseSignOut(auth)
      setError(`Only @${ALLOWED_EMAIL_DOMAIN} email addresses can use LiftLink.`)
    }
  }, [])

  const signOut = useCallback(async () => {
    const auth = getFirebaseAuth()
    if (auth) await firebaseSignOut(auth)
    setProfile(null)
    setFirebaseUser(null)
    setAuthToken(null)
  }, [])

  const value = useMemo(
    () => ({
      firebaseUser,
      profile,
      loading,
      error,
      signInWithGoogle,
      signOut,
      refreshProfile,
      clearError: () => setError(null),
    }),
    [firebaseUser, profile, loading, error, signInWithGoogle, signOut, refreshProfile]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export { isFirebaseConfigured }
