import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, Zap, CheckCircle, Clock, Users, UserCheck, Building } from 'lucide-react'
import { subscriptionApi } from '@/api/subscription'
import { PLAN_COLORS, PLAN_ICONS } from '@/types/subscription'
import clsx from 'clsx'

// ── Trial Countdown Banner ─────────────────────────────────────────────────────
export function TrialBanner() {
  const navigate = useNavigate()
  const { data } = useQuery({
    queryKey: ['current-subscription'],
    queryFn: subscriptionApi.getCurrent,
  })

  if (!data?.is_trial) return null

  const days = data.days_remaining
  const urgent = days <= 3
  const warning = days <= 7

  return (
    <div className={clsx(
      'flex items-center justify-between px-4 py-2.5 text-sm font-medium',
      urgent  ? 'bg-red-600 text-white' :
      warning ? 'bg-orange-500 text-white' :
                'bg-brand-800 text-white'
    )}>
      <div className="flex items-center gap-2">
        {urgent ? <AlertTriangle size={15} /> : <Clock size={15} />}
        {days === 0
          ? 'Your free trial expires today!'
          : days === 1
          ? '1 day left on your free trial.'
          : `${days} days left on your free trial.`
        }
        <span className="opacity-80 font-normal hidden sm:inline">
          Upgrade now to keep access to all features.
        </span>
      </div>
      <button
        onClick={() => navigate('/subscription/plans')}
        className="flex-shrink-0 bg-white/20 hover:bg-white/30 text-white text-xs px-3 py-1 rounded-lg transition-all font-semibold"
      >
        Upgrade →
      </button>
    </div>
  )
}


// ── Subscription Status Widget ────────────────────────────────────────────────
export function SubscriptionWidget() {
  const navigate = useNavigate()
  const { data, isLoading } = useQuery({
    queryKey: ['current-subscription'],
    queryFn: subscriptionApi.getCurrent,
  })

  if (isLoading) return (
    <div className="card p-5 animate-pulse">
      <div className="h-4 bg-slate-200 rounded w-1/3 mb-3" />
      <div className="h-8 bg-slate-200 rounded w-1/2" />
    </div>
  )

  if (!data) return null

  const colors = PLAN_COLORS[data.plan_code] || PLAN_COLORS.BASIC
  const icon = PLAN_ICONS[data.plan_code] || '📦'

  // Usage percentages
  const userPct   = data.max_users   ? Math.min(100, Math.round((data.current_user_count   / data.max_users)   * 100)) : 0
  const clientPct = data.max_clients ? Math.min(100, Math.round((data.current_client_count / data.max_clients) * 100)) : 0

  return (
    <div className={clsx('card border-2 p-5', colors.border)}>
      {/* Plan badge */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <span className="text-2xl">{icon}</span>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900 text-sm">{data.plan_name}</span>
              <span className={clsx('text-xs px-2 py-0.5 rounded-full font-semibold', colors.badge)}>
                {data.is_trial ? 'Trial' : data.billing_cycle}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              {data.is_trial
                ? `${data.days_remaining} days remaining`
                : `Renews ${new Date(data.end_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}`
              }
            </p>
          </div>
        </div>
        <button
          onClick={() => navigate('/subscription')}
          className="text-xs text-brand-700 hover:underline font-medium"
        >
          Manage →
        </button>
      </div>

      {/* Usage bars */}
      <div className="space-y-3">
        <UsageBar
          icon={<Users size={12} />}
          label="Users"
          used={data.current_user_count}
          max={data.max_users}
          pct={userPct}
        />
        {data.max_clients && (
          <UsageBar
            icon={<UserCheck size={12} />}
            label="Clients"
            used={data.current_client_count}
            max={data.max_clients}
            pct={clientPct}
          />
        )}
      </div>

      {/* Upgrade CTA for trial or near-limit */}
      {(data.is_trial || userPct >= 80 || clientPct >= 80) && (
        <button
          onClick={() => navigate('/subscription/plans')}
          className={clsx(
            'w-full mt-4 py-2 rounded-xl text-sm font-semibold transition-all',
            colors.btn
          )}
        >
          {data.is_trial ? '🚀 Upgrade Plan' : '⬆️ Increase Limits'}
        </button>
      )}
    </div>
  )
}

function UsageBar({ icon, label, used, max, pct }: {
  icon: React.ReactNode; label: string; used: number; max: number; pct: number
}) {
  return (
    <div>
      <div className="flex items-center justify-between text-xs text-slate-600 mb-1">
        <span className="flex items-center gap-1">{icon} {label}</span>
        <span className={clsx('font-medium', pct >= 90 ? 'text-red-600' : pct >= 70 ? 'text-orange-600' : 'text-slate-600')}>
          {used} / {max}
        </span>
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={clsx(
            'h-full rounded-full transition-all duration-500',
            pct >= 90 ? 'bg-red-500' : pct >= 70 ? 'bg-orange-400' : 'bg-brand-500'
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
