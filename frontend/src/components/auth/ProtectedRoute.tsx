import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import { useEffect, useState } from 'react'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStoreV2(s => s.isAuthenticated)
  const location = useLocation()
  const [isHydrated, setIsHydrated] = useState(false)

  useEffect(() => {
    // Give Zustand persist middleware time to hydrate from localStorage
    const timer = setTimeout(() => setIsHydrated(true), 150)
    return () => clearTimeout(timer)
  }, [])

  // Show loading while hydrating
  if (!isHydrated) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-brand-600 rounded-lg mb-4">
            <span className="text-white font-bold text-lg">CA</span>
          </div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return <>{children}</>
}

export function PublicRoute({ children }: { children: React.ReactNode }) {
  // Public routes don't need to check auth state
  // Users can navigate to login/register even if authenticated
  // They can manually logout if needed
  return <>{children}</>
}
