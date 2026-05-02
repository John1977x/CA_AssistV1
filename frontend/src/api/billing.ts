import api from './client'
import type { Invoice, TimeLog, Expense, Payment, BillingStats } from '@/types/billing'
import type { PaginatedResponse } from '@/types/auth'

export const billingApi = {
  stats: () => api.get<BillingStats>('/billing/stats').then(r => r.data),

  // Invoices
  listInvoices: (params?: {
    page?: number; page_size?: number; search?: string
    status?: string; customer_id?: number; overdue_only?: boolean
  }) => api.get<PaginatedResponse<Invoice>>('/billing/invoices', { params }).then(r => r.data),

  getInvoice: (id: number) =>
    api.get<Invoice>(`/billing/invoices/${id}`).then(r => r.data),

  createInvoice: (data: {
    customer_id: number; invoice_date: string; due_date: string
    is_igst?: boolean; gst_rate_pct?: number; discount_pct?: number
    notes?: string; terms_conditions?: string; task_id?: number
    payment_terms_days?: number
    line_items: { description: string; quantity: number; unit_price: number; unit?: string; gst_rate_pct?: number; task_id?: number }[]
  }) => api.post<Invoice>('/billing/invoices', data).then(r => r.data),

  updateInvoice: (id: number, data: Partial<Invoice>) =>
    api.patch<Invoice>(`/billing/invoices/${id}`, data).then(r => r.data),

  sendInvoice: (id: number) =>
    api.post<Invoice>(`/billing/invoices/${id}/send`).then(r => r.data),

  cancelInvoice: (id: number) =>
    api.post<Invoice>(`/billing/invoices/${id}/cancel`).then(r => r.data),

  deleteInvoice: (id: number) =>
    api.delete(`/billing/invoices/${id}`).then(r => r.data),

  recordPayment: (invoiceId: number, data: {
    payment_date: string; amount: number; payment_mode: string
    reference_number?: string; bank_name?: string; tds_deducted?: number; notes?: string
  }) => api.post<Payment>(`/billing/invoices/${invoiceId}/payments`, data).then(r => r.data),

  tallyExport: (invoice_ids: number[]) =>
    api.post('/billing/invoices/tally-export', { invoice_ids }, { responseType: 'blob' }).then(r => r.data),

  // Time Logs
  listTimeLogs: (params?: {
    page?: number; page_size?: number
    customer_id?: number; task_id?: number; user_id?: number
    is_billed?: boolean; date_from?: string; date_to?: string
  }) => api.get<PaginatedResponse<TimeLog>>('/billing/time-logs', { params }).then(r => r.data),

  createTimeLog: (data: {
    customer_id: number; task_id?: number; log_date: string
    duration_minutes: number; description: string
    is_billable?: boolean; hourly_rate?: number
    start_time?: string; end_time?: string
  }) => api.post<TimeLog>('/billing/time-logs', data).then(r => r.data),

  updateTimeLog: (id: number, data: Partial<TimeLog>) =>
    api.patch<TimeLog>(`/billing/time-logs/${id}`, data).then(r => r.data),

  deleteTimeLog: (id: number) =>
    api.delete(`/billing/time-logs/${id}`).then(r => r.data),

  // Expenses
  listExpenses: (params?: { page?: number; page_size?: number; status?: string; user_id?: number }) =>
    api.get<PaginatedResponse<Expense>>('/billing/expenses', { params }).then(r => r.data),

  createExpense: (data: {
    expense_date: string; category: string; description: string
    amount: number; gst_amount?: number; is_billable?: boolean
    customer_id?: number; task_id?: number; vendor_name?: string; payment_mode?: string
  }) => api.post<Expense>('/billing/expenses', data).then(r => r.data),

  approveExpense: (id: number, approve: boolean) =>
    api.post<Expense>(`/billing/expenses/${id}/approve`, null, { params: { approve } }).then(r => r.data),
}
