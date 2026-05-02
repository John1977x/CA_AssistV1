import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Check, X, Zap, Loader2, ExternalLink,
  ArrowUp, ArrowDown, AlertCircle, Shield,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { subscriptionApi } from '@/api/subscription'
import { useAuthStore } from '@/store/authStore'
import { PLAN_COLORS, PLAN_ICONS, FEATURE_LABELS } from '@/types/subscription'
import type { SubscriptionPlan, BillingCycle, UpgradePreview } from '@/types/subscription'
import { Modal } from '@/components/ui'
import clsx from 'clsx'

// ── Feature check row ─────────────────────────────────────────────────────────
function FeatureRow({ label, included }: { label: string; included: boolean }) {
  return (
    <li className="flex items-center gap-2.5 py-1.5">
      {included
        ? <Check size={14} className="text-green-600 flex-shrink-0" />
        : <X size={14} className="text-slate-300 flex-shrink-0" />
      }
      <span className={clsx('text-sm', included ? 'text-slate-700' : 'text-slate-400')}>
        {label}
      </span>
    </li>
  )
}

// ── Confirm upgrade/downgrade modal ───────────────────────────────────────────
function ConfirmModal({
  preview, plan, billingCycle, onClose, onConfirm, isLoading
}: {
  preview: UpgradePreview
  plan: SubscriptionPlan
  billingCycle: BillingCycle
  onClose: () => void
  onConfirm: () => void
  isLoading: boolean
}) {
  const colors = PLAN_COLORS[plan.plan_code] || PLAN_COLORS.BASIC

  return (
    <Modal open onClose={onClose} title={preview.is_upgrade ? 'Confirm Upgrade' : 'Confirm Downgrade'} size="md">
      <div className="p-6 space-y-5">
        {/* Plan change summary */}
        <div className="flex items-center gap-4 bg-slate-50 rounded-xl p-4">
          <div className="text-center flex-1">
            <p className="text-xs text-slate-400 mb-1">Current Plan</p>
            <p className="font-bold text-slate-700">{preview.current_plan}</p>
            <p className="text-sm text-slate-500">₹{preview.current_price.toLocaleString('en-IN')}/mo</p>
          </div>
          <div className={clsx(
            'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0',
            preview.is_upgrade ? 'bg-green-100' : 'bg-orange-100'
          )}>
            {preview.is_upgrade
              ? <ArrowUp size={18} className="text-green-600" />
              : <ArrowDown size={18} className="text-orange-600" />
            }
          </div>
          <div className="text-center flex-1">
            <p className="text-xs text-slate-400 mb-1">New Plan</p>
            <p className={clsx('font-bold', colors.badge.replace('bg-', 'text-').replace(' text-', ' ').split(' ')[0])}>
              {preview.new_plan}
            </p>
            <p className="text-sm text-slate-500">₹{preview.new_price.toLocaleString('en-IN')}/mo</p>
          </div>
        </div>

        {/* Price difference */}
        <div className={clsx(
          'flex items-center gap-3 rounded-xl p-4',
          preview.is_upgrade ? 'bg-green-50 border border-green-100' : 'bg-orange-50 border border-orange-100'
        )}>
          <AlertCircle size={16} className={preview.is_upgrade ? 'text-green-600' : 'text-orange-600'} />
          <div>
            <p className={clsx('text-sm font-semibold', preview.is_upgrade ? 'text-green-800' : 'text-orange-800')}>
              {preview.is_upgrade
                ? `+₹${Math.abs(preview.price_difference).toLocaleString('en-IN')} / month`
                : `-₹${Math.abs(preview.price_difference).toLocaleString('en-IN')} / month`
              }
            </p>
            <p className="text-xs text-slate-600 mt-0.5">{preview.proration_note}</p>
          </div>
        </div>

        {/* Stripe note */}
        <div className="flex items-start gap-2 text-xs text-slate-500">
          <Shield size={13} className="flex-shrink-0 mt-0.5 text-slate-400" />
          <p>You'll be redirected to Stripe's secure checkout to complete this transaction. Your card is never stored on our servers.</p>
        </div>

        <div className="flex gap-3 pt-1">
          <button onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className={clsx('btn-primary flex-1', colors.btn.replace('bg-', 'bg-').replace('hover:bg-', 'hover:bg-'))}
          >
            {isLoading
              ? <><Loader2 size={14} className="animate-spin" /> Redirecting...</>
              : <><ExternalLink size={14} /> Proceed to Stripe</>
            }
          </button>
        </div>
      </div>
    </Modal>
  )
}

// ── Single plan card ──────────────────────────────────────────────────────────
function PlanCard({
  plan, billingCycle, currentPlanCode, onSelect, isOwner
}: {
  plan: SubscriptionPlan
  billingCycle: BillingCycle
  currentPlanCode: string
  onSelect: (plan: SubscriptionPlan) => void
  isOwner: boolean
}) {
  const colors = PLAN_COLORS[plan.plan_code] || PLAN_COLORS.BASIC
  const icon = PLAN_ICONS[plan.plan_code] || '📦'
  const isCurrent = plan.plan_code === currentPlanCode
  const price = billingCycle === 'YEARLY' ? plan.price_yearly : plan.price_monthly
  const monthlyIfYearly = billingCycle === 'YEARLY' ? Math.round(plan.price_yearly / 12) : null
  const isPro = plan.plan_code === 'PRO'
  const isFree = plan.plan_code === 'TRIAL'

  const features = plan.features_json || {}

  return (
    <div className={clsx(
      'relative rounded-2xl border-2 p-6 flex flex-col transition-all',
      isCurrent ? `${colors.border} ${colors.bg} shadow-lg` : 'border-slate-200 bg-white hover:border-slate-300',
      isPro && !isCurrent ? 'border-brand-400 shadow-xl scale-105' : ''
    )}>
      {/* Popular badge */}
      {isPro && (
        <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
          <span className="bg-brand-800 text-white text-xs font-bold px-4 py-1 rounded-full">
            ⭐ Most Popular
          </span>
        </div>
      )}

      {/* Current badge */}
      {isCurrent && (
        <div className="absolute -top-3 right-4">
          <span className={clsx('text-xs font-bold px-3 py-1 rounded-full', colors.badge)}>
            ✓ Current Plan
          </span>
        </div>
      )}

      {/* Plan header */}
      <div className="flex items-center gap-3 mb-4">
        <span className="text-3xl">{icon}</span>
        <div>
          <h3 className="font-bold text-slate-900 text-lg">{plan.plan_name}</h3>
          {plan.description && <p className="text-xs text-slate-500">{plan.description}</p>}
        </div>
      </div>

      {/* Price */}
      <div className="mb-6">
        {isFree ? (
          <p className="text-3xl font-bold text-slate-900">Free</p>
        ) : (
          <>
            <div className="flex items-baseline gap-1">
              <span className="text-sm text-slate-500">₹</span>
              <span className="text-3xl font-bold text-slate-900">
                {(monthlyIfYearly || price).toLocaleString('en-IN')}
              </span>
              <span className="text-slate-500 text-sm">/month</span>
            </div>
            {billingCycle === 'YEARLY' && (
              <p className="text-xs text-green-600 font-medium mt-0.5">
                ₹{plan.price_yearly.toLocaleString('en-IN')}/year · Save {Math.round((1 - plan.price_yearly / (plan.price_monthly * 12)) * 100)}%
              </p>
            )}
          </>
        )}
      </div>

      {/* Limits */}
      <div className="space-y-1.5 mb-5 pb-5 border-b border-slate-100">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-600">Users</span>
          <span className="font-semibold text-slate-900">Up to {plan.max_users}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-600">Clients</span>
          <span className="font-semibold text-slate-900">{plan.max_clients ? `Up to ${plan.max_clients}` : 'Unlimited'}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-600">Branches</span>
          <span className="font-semibold text-slate-900">Up to {plan.max_branches}</span>
        </div>
        {plan.storage_limit_gb && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600">Storage</span>
            <span className="font-semibold text-slate-900">{plan.storage_limit_gb} GB</span>
          </div>
        )}
      </div>

      {/* Features */}
      <ul className="flex-1 space-y-0.5 mb-6">
        {Object.entries(FEATURE_LABELS).map(([key, label]) => (
          <FeatureRow key={key} label={label} included={!!features[key as keyof typeof features]} />
        ))}
      </ul>

      {/* CTA button */}
      {isFree ? (
        <div className="h-10" />
      ) : isCurrent ? (
        <button disabled className="w-full py-2.5 rounded-xl bg-slate-100 text-slate-500 text-sm font-semibold cursor-default">
          ✓ Active Plan
        </button>
      ) : (
        <button
          onClick={() => onSelect(plan)}
          disabled={!isOwner}
          title={!isOwner ? 'Only the firm owner can change plans' : ''}
          className={clsx(
            'w-full py-2.5 rounded-xl text-sm font-bold transition-all',
            colors.btn,
            !isOwner && 'opacity-50 cursor-not-allowed'
          )}
        >
          {plan.plan_code === 'TRIAL' ? 'Current' : `Get ${plan.plan_name}`} →
        </button>
      )}
    </div>
  )
}

// ── Main Plans Page ───────────────────────────────────────────────────────────
export default function PlansPage() {
  const navigate = useNavigate()
  const user = useAuthStore(s => s.user)
  const [billingCycle, setBillingCycle] = useState<BillingCycle>('MONTHLY')
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(null)
  const [preview, setPreview] = useState<UpgradePreview | null>(null)
  const [showConfirm, setShowConfirm] = useState(false)

  const { data: plans = [], isLoading: plansLoading } = useQuery({
    queryKey: ['plans'],
    queryFn: subscriptionApi.getPlans,
  })

  const { data: current } = useQuery({
    queryKey: ['current-subscription'],
    queryFn: subscriptionApi.getCurrent,
  })

  const previewMutation = useMutation({
    mutationFn: ({ code, cycle }: { code: string; cycle: string }) =>
      subscriptionApi.previewChange(code, cycle),
    onSuccess: (data) => {
      setPreview(data)
      setShowConfirm(true)
    },
  })

  const checkoutMutation = useMutation({
    mutationFn: ({ code, cycle }: { code: string; cycle: string }) =>
      subscriptionApi.createCheckout(code, cycle),
    onSuccess: (data) => {
      // Redirect to Stripe Checkout
      window.location.href = data.checkout_url
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.detail
      if (detail?.includes('not configured')) {
        toast.error('Stripe is not configured yet. Add your Stripe keys to the .env file.')
      }
    },
  })

  const handleSelectPlan = (plan: SubscriptionPlan) => {
    setSelectedPlan(plan)
    previewMutation.mutate({ code: plan.plan_code, cycle: billingCycle })
  }

  const handleConfirm = () => {
    if (!selectedPlan) return
    checkoutMutation.mutate({ code: selectedPlan.plan_code, cycle: billingCycle })
  }

  const visiblePlans = plans.filter(p => p.plan_code !== 'TRIAL')

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Choose Your Plan</h1>
        <p className="text-slate-500 text-base">
          Scale your CA practice with the right plan. Upgrade, downgrade, or cancel anytime.
        </p>
        {current?.is_trial && (
          <div className="inline-flex items-center gap-2 mt-3 bg-orange-50 border border-orange-200 text-orange-800 rounded-full px-4 py-1.5 text-sm font-medium">
            <AlertCircle size={14} />
            {current.days_remaining} days left on your free trial
          </div>
        )}
      </div>

      {/* Billing toggle */}
      <div className="flex items-center justify-center gap-4">
        <div className="flex items-center bg-slate-100 rounded-xl p-1.5">
          <button
            onClick={() => setBillingCycle('MONTHLY')}
            className={clsx(
              'px-5 py-2 rounded-lg text-sm font-semibold transition-all',
              billingCycle === 'MONTHLY' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-500'
            )}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingCycle('YEARLY')}
            className={clsx(
              'px-5 py-2 rounded-lg text-sm font-semibold transition-all',
              billingCycle === 'YEARLY' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-500'
            )}
          >
            Yearly
            <span className="ml-2 text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full font-bold">
              Save 17%
            </span>
          </button>
        </div>
      </div>

      {/* Plan cards */}
      {plansLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-6 bg-slate-200 rounded w-1/2 mb-4" />
              <div className="h-10 bg-slate-200 rounded w-2/3 mb-6" />
              <div className="space-y-2">
                {[1,2,3,4,5].map(j => <div key={j} className="h-4 bg-slate-100 rounded" />)}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
          {visiblePlans.map(plan => (
            <PlanCard
              key={plan.subscription_id}
              plan={plan}
              billingCycle={billingCycle}
              currentPlanCode={current?.plan_code || 'TRIAL'}
              onSelect={handleSelectPlan}
              isOwner={!!user?.is_owner}
            />
          ))}
        </div>
      )}

      {/* Non-owner notice */}
      {!user?.is_owner && (
        <p className="text-center text-sm text-slate-500">
          Only the firm owner can change the subscription plan.
        </p>
      )}

      {/* Manage billing */}
      {current && !current.is_trial && user?.is_owner && (
        <div className="text-center">
          <button
            onClick={async () => {
              const { portal_url } = await subscriptionApi.getPortalUrl()
              window.open(portal_url, '_blank')
            }}
            className="btn-secondary"
          >
            <ExternalLink size={14} /> Manage Billing & Invoices on Stripe
          </button>
        </div>
      )}

      {/* FAQ */}
      <div className="grid md:grid-cols-3 gap-4 pt-4 border-t border-slate-100">
        {[
          { q: 'Can I change plans later?', a: 'Yes, upgrade or downgrade anytime. Changes take effect immediately for upgrades, at period end for downgrades.' },
          { q: 'Is there a free trial?', a: 'Every new account gets a 14-day free trial with full access to all features. No credit card required.' },
          { q: 'How does GST work on invoices?', a: 'Stripe invoices include 18% GST as per Indian tax regulations. A proper GST invoice is sent to your registered email.' },
        ].map(faq => (
          <div key={faq.q} className="bg-slate-50 rounded-xl p-4">
            <h4 className="text-sm font-semibold text-slate-800 mb-1.5">{faq.q}</h4>
            <p className="text-xs text-slate-500 leading-relaxed">{faq.a}</p>
          </div>
        ))}
      </div>

      {/* Confirm modal */}
      {showConfirm && preview && selectedPlan && (
        <ConfirmModal
          preview={preview}
          plan={selectedPlan}
          billingCycle={billingCycle}
          onClose={() => { setShowConfirm(false); setPreview(null) }}
          onConfirm={handleConfirm}
          isLoading={checkoutMutation.isPending}
        />
      )}
    </div>
  )
}
