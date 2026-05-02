import api from './client'
import type { SubscriptionPlan, CurrentSubscription, UpgradePreview } from '@/types/subscription'

export const subscriptionApi = {
  // Public — no auth required
  getPlans: () =>
    api.get<SubscriptionPlan[]>('/subscription/plans').then(r => r.data),

  // Authenticated
  getCurrent: () =>
    api.get<CurrentSubscription>('/subscription/current').then(r => r.data),

  previewChange: (plan_code: string, billing_cycle: string) =>
    api.get<UpgradePreview>('/subscription/preview', { params: { plan_code, billing_cycle } }).then(r => r.data),

  // Owner only
  createCheckout: (plan_code: string, billing_cycle: string) =>
    api.post<{ session_id: string; checkout_url: string; publishable_key: string }>(
      '/subscription/checkout', { plan_code, billing_cycle }
    ).then(r => r.data),

  getPortalUrl: () =>
    api.post<{ portal_url: string }>('/subscription/portal').then(r => r.data),
}
