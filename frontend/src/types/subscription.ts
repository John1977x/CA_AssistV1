// ── Types ─────────────────────────────────────────────────────────────────────
export interface SubscriptionPlan {
  subscription_id:  number
  plan_name:        string
  plan_code:        PlanCode
  description:      string | null
  price_monthly:    number
  price_yearly:     number
  max_users:        number
  max_clients:      number | null
  max_branches:     number
  storage_limit_gb: number | null
  features_json:    PlanFeatures
  trial_days:       number
  is_active:        boolean
  sort_order:       number
}

export interface PlanFeatures {
  gst?:         boolean
  itr?:         boolean
  tds?:         boolean
  audit?:       boolean
  investment?:  boolean
  api_access?:  boolean
}

export interface CurrentSubscription {
  // Plan
  subscription_id:  number
  plan_name:        string
  plan_code:        PlanCode
  price_monthly:    number
  price_yearly:     number
  max_users:        number
  max_clients:      number | null
  max_branches:     number
  features_json:    PlanFeatures
  // Period
  history_id:       number
  billing_cycle:    'MONTHLY' | 'YEARLY'
  start_date:       string
  end_date:         string
  amount_paid:      number
  action:           string
  // Tenant
  tenant_status:    string
  trial_end_date:   string | null
  is_trial:         boolean
  days_remaining:   number
  // Usage
  current_user_count:    number
  current_client_count:  number
  current_branch_count:  number
}

export interface UpgradePreview {
  current_plan:     string
  new_plan:         string
  billing_cycle:    string
  current_price:    number
  new_price:        number
  price_difference: number
  is_upgrade:       boolean
  effective_date:   string
  proration_note:   string
}

export type PlanCode = 'TRIAL' | 'BASIC' | 'PRO' | 'ENT'
export type BillingCycle = 'MONTHLY' | 'YEARLY'

// ── Plan metadata ──────────────────────────────────────────────────────────────
export const PLAN_COLORS: Record<string, { bg: string; border: string; badge: string; btn: string }> = {
  TRIAL: { bg: 'bg-slate-50',  border: 'border-slate-200', badge: 'bg-slate-100 text-slate-600', btn: 'bg-slate-700 hover:bg-slate-800 text-white' },
  BASIC: { bg: 'bg-blue-50',   border: 'border-blue-200',  badge: 'bg-blue-100 text-blue-700',   btn: 'bg-blue-700 hover:bg-blue-800 text-white' },
  PRO:   { bg: 'bg-brand-50',  border: 'border-brand-300', badge: 'bg-brand-100 text-brand-800', btn: 'bg-brand-800 hover:bg-brand-900 text-white' },
  ENT:   { bg: 'bg-purple-50', border: 'border-purple-300',badge: 'bg-purple-100 text-purple-800',btn: 'bg-purple-700 hover:bg-purple-800 text-white' },
}

export const PLAN_ICONS: Record<string, string> = {
  TRIAL: '🔬', BASIC: '⚡', PRO: '🚀', ENT: '🏢',
}

export const FEATURE_LABELS: Record<string, string> = {
  gst: 'GST Filing',
  itr: 'Income Tax & ITR',
  tds: 'TDS Returns',
  audit: 'Audit Workflow',
  investment: 'Investment Advisory',
  api_access: 'API Access',
}
