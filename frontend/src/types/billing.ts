export interface Invoice {
  invoice_id:         number
  tenant_id:          number
  customer_id:        number
  invoice_number:     string
  invoice_date:       string
  due_date:           string
  subtotal:           number
  discount_amount:    number
  taxable_amount:     number
  cgst_amount:        number
  sgst_amount:        number
  igst_amount:        number
  total_tax:          number
  total_amount:       number
  amount_paid:        number
  balance_due:        number
  currency_code:      string
  is_igst:            boolean
  gst_rate_pct:       number
  status:             InvoiceStatus
  payment_terms_days: number
  notes:              string | null
  terms_conditions:   string | null
  tally_voucher_number: string | null
  tally_synced_at:    string | null
  sent_at:            string | null
  task_id:            number | null
  branch_id:          number | null
  created_at:         string
  updated_at:         string
  customer:           BillingCustomerBrief | null
  created_by:         BillingUserBrief | null
  line_items:         LineItem[] | null
}

export interface LineItem {
  line_item_id:   number
  description:    string
  hsn_sac_code:   string | null
  quantity:       number
  unit:           string | null
  unit_price:     number
  discount_pct:   number
  taxable_amount: number
  gst_rate_pct:   number
  cgst_amount:    number
  sgst_amount:    number
  igst_amount:    number
  line_total:     number
  sort_order:     number
  task_id:        number | null
}

export interface BillingCustomerBrief {
  customer_id:  number
  display_name: string
  gstin:        string | null
  pan:          string | null
  phone:        string
  email:        string | null
}

export interface BillingUserBrief {
  user_id:      number
  display_name: string | null
  email:        string
}

export interface Payment {
  payment_id:       number
  invoice_id:       number
  customer_id:      number
  payment_date:     string
  amount:           number
  payment_mode:     string
  reference_number: string | null
  bank_name:        string | null
  notes:            string | null
  tds_deducted:     number
  net_received:     number
  created_at:       string
  recorded_by:      BillingUserBrief | null
}

export interface TimeLog {
  time_log_id:      number
  tenant_id:        number
  user_id:          number
  customer_id:      number
  task_id:          number | null
  log_date:         string
  start_time:       string | null
  end_time:         string | null
  duration_minutes: number
  billable_minutes: number
  description:      string
  is_billable:      boolean
  is_billed:        boolean
  hourly_rate:      number | null
  line_amount:      number | null
  invoice_id:       number | null
  created_at:       string
  user:             BillingUserBrief | null
  customer:         BillingCustomerBrief | null
}

export interface Expense {
  expense_id:    number
  tenant_id:     number
  user_id:       number
  customer_id:   number | null
  task_id:       number | null
  expense_date:  string
  category:      string
  description:   string
  amount:        number
  gst_amount:    number
  total_amount:  number
  is_billable:   boolean
  is_reimbursed: boolean
  payment_mode:  string | null
  vendor_name:   string | null
  receipt_url:   string | null
  status:        ExpenseStatus
  approved_at:   string | null
  created_at:    string
  user:          BillingUserBrief | null
}

export interface BillingStats {
  total_invoiced:     number
  total_collected:    number
  total_outstanding:  number
  total_overdue:      number
  invoice_count:      number
  draft_count:        number
  overdue_count:      number
  unbilled_hours:     number
  this_month_revenue: number
}

export type InvoiceStatus = 'DRAFT' | 'SENT' | 'PARTIALLY_PAID' | 'PAID' | 'CANCELLED' | 'OVERDUE'
export type ExpenseStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'REIMBURSED'

export const PAYMENT_MODES = ['CASH', 'NEFT', 'RTGS', 'UPI', 'CHEQUE', 'CARD']
export const EXPENSE_CATEGORIES = [
  'TRAVEL', 'FILING_FEE', 'OFFICE_SUPPLIES', 'COURIER',
  'GOVERNMENT_FEE', 'PROFESSIONAL_FEE', 'MEALS', 'SOFTWARE',
  'INTERNET', 'PRINTING', 'MISCELLANEOUS',
]
