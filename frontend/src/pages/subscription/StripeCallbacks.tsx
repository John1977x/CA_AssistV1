import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { CheckCircle, XCircle } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'

export function SubscriptionSuccessPage() {
  const navigate = useNavigate()
  const qc = useQueryClient()

  useEffect(() => {
    // Invalidate subscription cache so fresh data loads
    qc.invalidateQueries({ queryKey: ['current-subscription'] })
    const t = setTimeout(() => navigate('/subscription'), 4000)
    return () => clearTimeout(t)
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="card p-12 max-w-md w-full text-center">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="text-green-600" size={40} />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Payment Successful!</h1>
        <p className="text-slate-500 mb-6">
          Your subscription has been activated. Welcome to the new plan — all features are now unlocked.
        </p>
        <div className="flex items-center justify-center gap-2 text-sm text-slate-400">
          <div className="animate-spin w-4 h-4 border-2 border-brand-600 border-t-transparent rounded-full" />
          Redirecting to your dashboard...
        </div>
      </div>
    </div>
  )
}

export function SubscriptionCancelPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="card p-12 max-w-md w-full text-center">
        <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <XCircle className="text-orange-500" size={40} />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Payment Cancelled</h1>
        <p className="text-slate-500 mb-6">
          No charge was made. Your current plan remains unchanged.
        </p>
        <div className="flex gap-3">
          <button onClick={() => navigate('/subscription/plans')} className="btn-primary flex-1">
            View Plans
          </button>
          <button onClick={() => navigate('/dashboard')} className="btn-secondary flex-1">
            Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  )
}
