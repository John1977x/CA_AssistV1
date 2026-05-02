import api from './client'
import type { Customer, CustomerDetails, CustomerStats, Enquiry, EnquiryStats } from '@/types/customer'
import type { PaginatedResponse } from '@/types/auth'

// ── Customers ─────────────────────────────────────────────────────────────────
export const customersApi = {
  stats: () =>
    api.get<CustomerStats>('/customers/stats').then(r => r.data),

  list: (params?: {
    page?: number; page_size?: number; search?: string
    status?: string; customer_type?: string; kyc_status?: string
    assigned_user_id?: number; branch_id?: number; tag?: string
  }) =>
    api.get<PaginatedResponse<Customer>>('/customers', { params }).then(r => r.data),

  get: (id: number) =>
    api.get<Customer>(`/customers/${id}`).then(r => r.data),

  create: (data: Partial<Customer> & { phone: string; display_name: string }) =>
    api.post<Customer>('/customers', data).then(r => r.data),

  update: (id: number, data: Partial<Customer>) =>
    api.patch<Customer>(`/customers/${id}`, data).then(r => r.data),

  delete: (id: number) =>
    api.delete(`/customers/${id}`).then(r => r.data),

  upsertDetails: (id: number, data: Partial<CustomerDetails>) =>
    api.put<CustomerDetails>(`/customers/${id}/details`, data).then(r => r.data),

  updateKyc: (id: number, kyc_status: string) =>
    api.patch<Customer>(`/customers/${id}/kyc`, null, { params: { kyc_status } }).then(r => r.data),
}

// ── Enquiries ─────────────────────────────────────────────────────────────────
export const enquiriesApi = {
  stats: () =>
    api.get<EnquiryStats>('/enquiries/stats').then(r => r.data),

  list: (params?: {
    page?: number; page_size?: number; search?: string
    status?: string; source?: string; assigned_to_user_id?: number; is_converted?: boolean
  }) =>
    api.get<PaginatedResponse<Enquiry>>('/enquiries', { params }).then(r => r.data),

  get: (id: number) =>
    api.get<Enquiry>(`/enquiries/${id}`).then(r => r.data),

  create: (data: Partial<Enquiry> & { phone: string; full_name: string }) =>
    api.post<Enquiry>('/enquiries', data).then(r => r.data),

  update: (id: number, data: Partial<Enquiry>) =>
    api.patch<Enquiry>(`/enquiries/${id}`, data).then(r => r.data),

  delete: (id: number) =>
    api.delete(`/enquiries/${id}`).then(r => r.data),

  convert: (id: number, data: {
    customer_type?: string; display_name?: string
    pan?: string; gstin?: string; onboarded_at?: string
    assigned_user_id?: number; branch_id?: number
  }) =>
    api.post<Customer>(`/enquiries/${id}/convert`, data).then(r => r.data),
}
