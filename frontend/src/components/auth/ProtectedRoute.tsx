import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import { useEffect, useState } from 'react'

function useHydrated() {
  const [isHydrated, setIsHydrated] = useState(
    () => useAuthStoreV2.persist.hasHydrated()
  )

  useEffect(() => {
    if (useAuthStoreV2.persist.hasHydrated()) {
      setIsHydrated(true)
      return
    }
    const unsub = useAuthStoreV2.persist.onFinishHydration(() => setIsHydrated(true))
    return unsub
  }, [])

  return isHydrated
}

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStoreV2(s => s.isAuthenticated)
  const location = useLocation()
  const isHydrated = useHydrated()

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
  const isAuthenticated = useAuthStoreV2(s => s.isAuthenticated)
  const company = useAuthStoreV2(s => s.company)
  const isHydrated = useHydrated()

  if (isHydrated && isAuthenticated) {
    const role = company?.role
    const dashboard =
      role === 'OWNER' ? '/owner/dashboard' :
      role === 'MANAGER' ? '/manager/dashboard' :
      role === 'EMPLOYEE' ? '/employee/dashboard' :
      role === 'CLIENT' ? '/client/dashboard' :
      '/dashboard'
    return <Navigate to={dashboard} replace />
  }

  return <>{children}</>
}
