import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  CheckCircle, Clock, Users, UserCheck, Building,
  ExternalLink, ArrowUpRight, Zap, Calendar, CreditCard,
  AlertTriangle, Shield,
} from 'lucide-react'
import { subscriptionApi } from '@/api/subscription'
import { useAuthStore } from '@/store/authStore'
import { PLAN_COLORS, PLAN_ICONS, FEATURE_LABELS } from '@/types/subscription'
import { format, parseISO } from 'date-fns'
import clsx from 'clsx'

function UsageBar({ label, icon, used, max }: {
  label: string; icon: React.ReactNode; used: number; max: number
}) {
  const pct = max ? Math.min(100, Math.round((used / max) * 100)) : 0
  const isHigh = pct >= 80
  const isCritical = pct >= 95

  return (
    <div className="bg-slate-50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2 text-sm text-slate-700">
          <span className="text-slate-500">{icon}</span>
          {label}
        </div>
        <span className={clsx(
          'text-sm font-bold',
          isCritical ? 'text-red-600' : isHigh ? 'text-orange-600' : 'text-slate-900'
        )}>
          {used} <span className="font-normal text-slate-400">/ {max}</span>
        </span>
      </div>
      <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
        <div
          className={clsx(
            'h-full rounded-full transition-all duration-500',
            isCritical ? 'bg-red-500' : isHigh ? 'bg-orange-400' : 'bg-brand-500'
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
      {isHigh && (
        <p className={clsx('text-xs mt-1', isCritical ? 'text-red-600' : 'text-orange-600')}>
          {isCritical ? '⚠ Limit almost reached' : `${100 - pct}% remaining`}
        </p>
      )}
    </div>
  )
}

export default function SubscriptionPage() {
  const navigate = useNavigate()
  const user = useAuthStore(s => s.user)

  const { data, isLoading } = useQuery({
    queryKey: ['current-subscription'],
    queryFn: subscriptionApi.getCurrent,
  })

  if (isLoading) {
    return (
      <div className="p-6 max-w-4xl mx-auto space-y-4 animate-pulse">
        {[1,2,3].map(i => <div key={i} className="card h-32" />)}
      </div>
    )
  }

  if (!data) return null

  const colors = PLAN_COLORS[data.plan_code] || PLAN_COLORS.BASIC
  const icon = PLAN_ICONS[data.plan_code] || '📦'
  const features = data.features_json || {}

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Subscription</h1>
          <p className="text-sm text-slate-500 mt-0.5">Manage your plan, billing and usage</p>
        </div>
        <button
          onClick={() => navigate('/subscription/plans')}
          className="btn-primary"
        >
          <ArrowUpRight size={15} /> Change Plan
        </button>
      </div>

      {/* Current plan card */}
      <div className={clsx('card border-2 p-6', colors.border, colors.bg)}>
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <span className="text-4xl">{icon}</span>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-xl font-bold text-slate-900">{data.plan_name} Plan</h2>
                <span className={clsx('text-xs font-bold px-2.5 py-1 rounded-full', colors.badge)}>
                  {data.is_trial ? '14-day Trial' : data.billing_cycle}
                </span>
                {data.tenant_status === 'ACTIVE' && !data.is_trial && (
                  <span className="flex items-center gap-1 text-xs text-green-700 bg-green-50 px-2 py-0.5 rounded-full">
                    <CheckCircle size={11} /> Active
                  </span>
                )}
              </div>

              <div className="flex flex-wrap gap-4 mt-3 text-sm text-slate-600">
                <span className="flex items-center gap-1.5">
                  <Calendar size={13} />
                  {data.is_trial
                    ? `Trial ends ${format(parseISO(data.trial_end_date!), 'd MMM yyyy')}`
                    : `Current period: ${format(parseISO(data.start_date), 'd MMM')} – ${format(parseISO(data.end_date), 'd MMM yyyy')}`
                  }
                </span>
                {!data.is_trial && (
                  <span className="flex items-center gap-1.5">
                    <CreditCard size={13} />
                    ₹{(data.billing_cycle === 'YEARLY' ? data.price_yearly : data.price_monthly).toLocaleString('en-IN')} / {data.billing_cycle === 'YEARLY' ? 'year' : 'month'}
                  </span>
                )}
              </div>

              {/* Days remaining */}
              {data.days_remaining <= 7 && (
                <div className={clsx(
                  'flex items-center gap-2 mt-3 text-sm font-medium px-3 py-2 rounded-lg',
                  data.days_remaining <= 2 ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
                )}>
                  <AlertTriangle size={14} />
                  {data.is_trial
                    ? `Trial expires in ${data.days_remaining} day${data.days_remaining !== 1 ? 's' : ''}`
                    : `Subscription renews in ${data.days_remaining} day${data.days_remaining !== 1 ? 's' : ''}`
                  }
                </div>
              )}
            </div>
          </div>

          {user?.is_owner && (
            <div className="flex flex-col gap-2">
              {data.is_trial ? (
                <button
                  onClick={() => navigate('/subscription/plans')}
                  className={clsx('btn-sm font-bold px-4 py-2 rounded-xl', colors.btn)}
                >
                  <Zap size={13} /> Upgrade Now
                </button>
              ) : (
                <button
                  onClick={async () => {
                    const { portal_url } = await subscriptionApi.getPortalUrl()
                    window.open(portal_url, '_blank')
                  }}
                  className="btn-secondary btn-sm"
                >
                  <ExternalLink size={13} /> Manage on Stripe
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Usage */}
      <div>
        <h3 className="text-sm font-semibold text-slate-700 mb-3">Usage This Period</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <UsageBar
            label="Team Members"
            icon={<Users size={14} />}
            used={data.current_user_count}
            max={data.max_users}
          />
          {data.max_clients && (
            <UsageBar
              label="Clients"
              icon={<UserCheck size={14} />}
              used={data.current_client_count}
              max={data.max_clients}
            />
          )}
          <UsageBar
            label="Branches"
            icon={<Building size={14} />}
            used={data.current_branch_count}
            max={data.max_branches}
          />
        </div>
      </div>

      {/* Features included */}
      <div>
        <h3 className="text-sm font-semibold text-slate-700 mb-3">Features Included</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {Object.entries(FEATURE_LABELS).map(([key, label]) => {
            const included = !!features[key as keyof typeof features]
            return (
              <div key={key} className={clsx(
                'flex items-center gap-2.5 rounded-xl p-3 text-sm',
                included ? 'bg-green-50 text-green-800' : 'bg-slate-50 text-slate-400'
              )}>
                {included
                  ? <CheckCircle size={15} className="text-green-600 flex-shrink-0" />
                  : <div className="w-4 h-4 rounded-full border-2 border-slate-300 flex-shrink-0" />
                }
                {label}
              </div>
            )
          })}
        </div>
      </div>

      {/* Security note */}
      <div className="flex items-start gap-3 bg-slate-50 rounded-xl p-4 text-sm text-slate-600">
        <Shield size={16} className="flex-shrink-0 mt-0.5 text-slate-400" />
        <div>
          <p className="font-medium text-slate-700 mb-0.5">Secure payments by Stripe</p>
          <p className="text-xs">
            Your payment information is stored securely by Stripe. We never store your card details.
            All transactions are encrypted with TLS and processed in compliance with PCI DSS.
          </p>
        </div>
      </div>

      {/* Upgrade prompt for trial/basic */}
      {(data.is_trial || data.plan_code === 'BASIC') && (
        <div className="card border-2 border-brand-200 bg-brand-50 p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="font-bold text-brand-900 mb-1">
                {data.is_trial ? '🚀 Ready to go beyond your trial?' : '⬆️ Unlock more with Pro'}
              </h3>
              <p className="text-sm text-brand-700">
                {data.is_trial
                  ? 'Choose a plan to keep all your data and continue working without interruption.'
                  : 'Get audit workflows, investment advisory, and unlimited clients.'
                }
              </p>
            </div>
            <button
              onClick={() => navigate('/subscription/plans')}
              className="flex-shrink-0 btn-primary"
            >
              View Plans
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
