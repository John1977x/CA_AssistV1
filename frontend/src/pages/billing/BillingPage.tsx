import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import {
  Plus, Search, FileText, Clock, IndianRupee, AlertCircle,
  ChevronLeft, ChevronRight, RefreshCw, TrendingUp, Download,
  CheckCircle, XCircle, Loader2, Receipt,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { format, parseISO, isPast } from 'date-fns'
import { billingApi } from '@/api/billing'
import { customersApi } from '@/api/customers'
import { StatCard, StatusBadge, EmptyState, Modal, FormField, Tabs } from '@/components/ui'
import InvoiceFormModal from './InvoiceFormModal'
import InvoiceDrawer from './InvoiceDrawer'
import { EXPENSE_CATEGORIES, PAYMENT_MODES } from '@/types/billing'
import type { Invoice, TimeLog, Expense } from '@/types/billing'
import clsx from 'clsx'

// ── Invoice status color ───────────────────────────────────────────────────────
const INV_STATUS: Record<string, string> = {
  DRAFT:          'badge-gray',
  SENT:           'badge-blue',
  PARTIALLY_PAID: 'badge-yellow',
  PAID:           'badge-green',
  CANCELLED:      'badge-red',
  OVERDUE:        'badge-red',
}

// ── Add Time Log modal ────────────────────────────────────────────────────────
function AddTimeLogModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const qc = useQueryClient()
  const [custSearch, setCustSearch] = useState('')
  const { register, handleSubmit, watch, setValue, reset } = useForm({
    defaultValues: { log_date: new Date().toISOString().slice(0, 10), duration_minutes: 60, is_billable: true, hourly_rate: 0 },
  })
  const custId = watch('customer_id')

  const { data: customers } = useQuery({
    queryKey: ['cust-search-tl', custSearch],
    queryFn: () => customersApi.list({ search: custSearch, page_size: 8 }),
    enabled: custSearch.length > 0,
  })

  const mutation = useMutation({
    mutationFn: (d: any) => billingApi.createTimeLog(d),
    onSuccess: () => {
      toast.success('Time logged!')
      qc.invalidateQueries({ queryKey: ['time-logs'] })
      qc.invalidateQueries({ queryKey: ['billing-stats'] })
      reset()
      onClose()
    },
  })

  return (
    <Modal open={open} onClose={onClose} title="Log Time" size="md">
      <form onSubmit={handleSubmit(d => mutation.mutate(d))} className="p-6 space-y-4">
        <FormField label="Client" required>
          <input value={custSearch} onChange={e => setCustSearch(e.target.value)}
            placeholder="Search client..." className="input" />
          {custSearch && customers?.items && (
            <div className="mt-1 border border-slate-200 rounded-xl bg-white shadow-lg max-h-36 overflow-y-auto">
              {customers.items.map(c => (
                <button key={c.customer_id} type="button"
                  onClick={() => { setValue('customer_id' as any, c.customer_id); setCustSearch(c.display_name) }}
                  className="w-full text-left px-4 py-2 hover:bg-slate-50 text-sm">
                  {c.display_name}
                </button>
              ))}
            </div>
          )}
        </FormField>

        <div className="grid grid-cols-2 gap-3">
          <FormField label="Date" required>
            <input {...register('log_date')} type="date" className="input" />
          </FormField>
          <FormField label="Duration (minutes)" required>
            <input {...register('duration_minutes', { valueAsNumber: true })} type="number" min="1" className="input" />
          </FormField>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <FormField label="Start Time">
            <input {...register('start_time' as any)} type="time" className="input" />
          </FormField>
          <FormField label="End Time">
            <input {...register('end_time' as any)} type="time" className="input" />
          </FormField>
        </div>

        <FormField label="Description" required>
          <textarea {...register('description')} rows={2} className="input resize-none"
            placeholder="What work was done..." />
        </FormField>

        <div className="grid grid-cols-2 gap-3">
          <div className="flex items-center gap-2 bg-slate-50 rounded-lg p-3">
            <input {...register('is_billable')} type="checkbox" id="billable" className="w-4 h-4" />
            <label htmlFor="billable" className="text-sm font-medium">Billable</label>
          </div>
          <FormField label="Hourly Rate (₹)">
            <input {...register('hourly_rate', { valueAsNumber: true })} type="number" step="50" className="input" />
          </FormField>
        </div>

        <div className="flex gap-3 pt-2">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button type="submit" disabled={mutation.isPending} className="btn-primary flex-1">
            {mutation.isPending ? <><Loader2 size={14} className="animate-spin" /> Saving...</> : 'Log Time'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

// ── Add Expense modal ─────────────────────────────────────────────────────────
function AddExpenseModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const qc = useQueryClient()
  const { register, handleSubmit, reset } = useForm({
    defaultValues: { expense_date: new Date().toISOString().slice(0, 10), gst_amount: 0, is_billable: false },
  })
  const mutation = useMutation({
    mutationFn: (d: any) => billingApi.createExpense(d),
    onSuccess: () => {
      toast.success('Expense added!')
      qc.invalidateQueries({ queryKey: ['expenses'] })
      reset()
      onClose()
    },
  })

  return (
    <Modal open={open} onClose={onClose} title="Add Expense" size="md">
      <form onSubmit={handleSubmit(d => mutation.mutate(d))} className="p-6 space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Date" required>
            <input {...register('expense_date')} type="date" className="input" />
          </FormField>
          <FormField label="Category" required>
            <select {...register('category')} className="input">
              <option value="">Select...</option>
              {EXPENSE_CATEGORIES.map(c => <option key={c} value={c}>{c.replace('_', ' ')}</option>)}
            </select>
          </FormField>
        </div>
        <FormField label="Description" required>
          <textarea {...register('description')} rows={2} className="input resize-none" />
        </FormField>
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Amount (₹)" required>
            <input {...register('amount', { valueAsNumber: true })} type="number" step="0.01" className="input" />
          </FormField>
          <FormField label="GST Amount (₹)">
            <input {...register('gst_amount', { valueAsNumber: true })} type="number" step="0.01" className="input" />
          </FormField>
          <FormField label="Vendor">
            <input {...register('vendor_name')} className="input" />
          </FormField>
          <FormField label="Payment Mode">
            <select {...register('payment_mode')} className="input">
              <option value="">Select...</option>
              {PAYMENT_MODES.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </FormField>
        </div>
        <div className="flex gap-3 pt-2">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button type="submit" disabled={mutation.isPending} className="btn-primary flex-1">
            {mutation.isPending ? <Loader2 size={14} className="animate-spin" /> : 'Add Expense'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

// ── Main Billing Page ─────────────────────────────────────────────────────────
export default function BillingPage() {
  const qc = useQueryClient()
  const [tab, setTab] = useState('invoices')
  const [showInvoiceForm, setShowInvoiceForm] = useState(false)
  const [showTimeLog, setShowTimeLog] = useState(false)
  const [showExpense, setShowExpense] = useState(false)
  const [viewInvoiceId, setViewInvoiceId] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [overdueOnly, setOverdueOnly] = useState(false)
  const [page, setPage] = useState(1)
  const [selectedIds, setSelectedIds] = useState<number[]>([])

  const { data: stats } = useQuery({ queryKey: ['billing-stats'], queryFn: billingApi.stats })

  const { data: invoiceData, isLoading: invLoading, isFetching: invFetching } = useQuery({
    queryKey: ['invoices', page, search, statusFilter, overdueOnly],
    queryFn: () => billingApi.listInvoices({ page, page_size: 15, search: search || undefined, status: statusFilter || undefined, overdue_only: overdueOnly }),
    enabled: tab === 'invoices',
    placeholderData: p => p,
  })

  const { data: timeLogData, isLoading: tlLoading } = useQuery({
    queryKey: ['time-logs', page],
    queryFn: () => billingApi.listTimeLogs({ page, page_size: 20 }),
    enabled: tab === 'timelogs',
    placeholderData: p => p,
  })

  const { data: expenseData, isLoading: expLoading } = useQuery({
    queryKey: ['expenses', page],
    queryFn: () => billingApi.listExpenses({ page, page_size: 20 }),
    enabled: tab === 'expenses',
    placeholderData: p => p,
  })

  const approveExpense = useMutation({
    mutationFn: ({ id, approve }: { id: number; approve: boolean }) => billingApi.approveExpense(id, approve),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['expenses'] }),
  })

  const handleTallyBulkExport = async () => {
    if (!selectedIds.length) { toast.error('Select at least one invoice.'); return }
    const blob = await billingApi.tallyExport(selectedIds)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'tally_bulk_export.xml'; a.click()
    URL.revokeObjectURL(url)
    toast.success(`${selectedIds.length} invoice(s) exported!`)
    setSelectedIds([])
  }

  const invoices = invoiceData?.items || []
  const timeLogs = timeLogData?.items || []
  const expenses = expenseData?.items || []

  const addBtn = tab === 'invoices' ? { label: 'New Invoice', action: () => setShowInvoiceForm(true) }
    : tab === 'timelogs' ? { label: 'Log Time', action: () => setShowTimeLog(true) }
    : { label: 'Add Expense', action: () => setShowExpense(true) }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Billing & Time Tracking</h1>
          <p className="text-sm text-slate-500 mt-0.5">Invoices, time logs, expenses and payments</p>
        </div>
        <div className="flex gap-2">
          {tab === 'invoices' && selectedIds.length > 0 && (
            <button onClick={handleTallyBulkExport} className="btn-secondary btn-sm">
              <Download size={14} /> Tally Export ({selectedIds.length})
            </button>
          )}
          <button onClick={addBtn.action} className="btn-primary">
            <Plus size={15} /> {addBtn.label}
          </button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total Invoiced"    value={`₹${(stats.total_invoiced / 1000).toFixed(0)}K`}    icon={<FileText size={18} />}     color="text-blue-600"   bg="bg-blue-50" />
          <StatCard label="Collected"         value={`₹${(stats.total_collected / 1000).toFixed(0)}K`}   icon={<CheckCircle size={18} />}  color="text-green-600"  bg="bg-green-50" />
          <StatCard label="Outstanding"       value={`₹${(stats.total_outstanding / 1000).toFixed(0)}K`} icon={<IndianRupee size={18} />}  color="text-orange-600" bg="bg-orange-50" />
          <StatCard label="Unbilled Hours"    value={`${stats.unbilled_hours}h`}                          icon={<Clock size={18} />}        color="text-purple-600" bg="bg-purple-50" />
        </div>
      )}

      {/* Tabs */}
      <Tabs
        tabs={[
          { key: 'invoices',  label: 'Invoices',   count: invoiceData?.total },
          { key: 'timelogs',  label: 'Time Logs',  count: timeLogData?.total },
          { key: 'expenses',  label: 'Expenses',   count: expenseData?.total },
        ]}
        active={tab}
        onChange={t => { setTab(t); setPage(1) }}
      />

      {/* Invoice filters */}
      {tab === 'invoices' && (
        <div className="card p-4">
          <div className="flex flex-wrap gap-3">
            <div className="relative flex-1 min-w-48">
              <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input value={search} onChange={e => { setSearch(e.target.value); setPage(1) }}
                placeholder="Search invoice number..." className="input pl-9" />
            </div>
            <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1) }} className="input w-40">
              <option value="">All Status</option>
              {['DRAFT', 'SENT', 'PARTIALLY_PAID', 'PAID', 'CANCELLED'].map(s => (
                <option key={s} value={s}>{s.replace('_', ' ')}</option>
              ))}
            </select>
            <button onClick={() => { setOverdueOnly(!overdueOnly); setPage(1) }}
              className={clsx('btn-sm flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium border transition-all',
                overdueOnly ? 'bg-red-600 text-white border-red-600' : 'bg-white text-slate-600 border-slate-200')}>
              <AlertCircle size={13} /> Overdue
            </button>
            <button onClick={() => qc.invalidateQueries({ queryKey: ['invoices'] })}
              className={clsx('btn-ghost', invFetching && 'opacity-50')}>
              <RefreshCw size={15} className={invFetching ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>
      )}

      {/* Invoice table */}
      {tab === 'invoices' && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="table-th w-8">
                    <input type="checkbox"
                      checked={selectedIds.length === invoices.length && invoices.length > 0}
                      onChange={e => setSelectedIds(e.target.checked ? invoices.map(i => i.invoice_id) : [])}
                      className="w-4 h-4" />
                  </th>
                  <th className="table-th">Invoice #</th>
                  <th className="table-th">Client</th>
                  <th className="table-th">Date</th>
                  <th className="table-th">Due Date</th>
                  <th className="table-th">Amount</th>
                  <th className="table-th">Balance</th>
                  <th className="table-th">Status</th>
                  <th className="table-th">Tally</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {invLoading ? (
                  <tr><td colSpan={9} className="py-16 text-center">
                    <div className="animate-spin w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full mx-auto" />
                  </td></tr>
                ) : invoices.length === 0 ? (
                  <tr><td colSpan={9}>
                    <EmptyState icon={<Receipt size={24} />} title="No invoices yet"
                      description="Create your first invoice"
                      action={<button onClick={() => setShowInvoiceForm(true)} className="btn-primary btn-sm"><Plus size={13} /> New Invoice</button>} />
                  </td></tr>
                ) : invoices.map(inv => {
                  const isOverdue = isPast(parseISO(inv.due_date)) && !['PAID', 'CANCELLED'].includes(inv.status)
                  return (
                    <tr key={inv.invoice_id} onClick={() => setViewInvoiceId(inv.invoice_id)}
                      className="hover:bg-blue-50/40 cursor-pointer transition-colors">
                      <td className="px-4 py-3.5" onClick={e => e.stopPropagation()}>
                        <input type="checkbox" className="w-4 h-4"
                          checked={selectedIds.includes(inv.invoice_id)}
                          onChange={e => setSelectedIds(e.target.checked
                            ? [...selectedIds, inv.invoice_id]
                            : selectedIds.filter(id => id !== inv.invoice_id)
                          )} />
                      </td>
                      <td className="table-td font-mono text-sm font-medium text-brand-800">{inv.invoice_number}</td>
                      <td className="table-td text-sm text-slate-700">{inv.customer?.display_name || '—'}</td>
                      <td className="table-td text-xs text-slate-500">{format(parseISO(inv.invoice_date), 'd MMM yyyy')}</td>
                      <td className={clsx('table-td text-xs', isOverdue ? 'text-red-600 font-semibold' : 'text-slate-500')}>
                        {format(parseISO(inv.due_date), 'd MMM yyyy')}
                        {isOverdue && ' ⚠'}
                      </td>
                      <td className="table-td text-sm font-semibold text-slate-900">
                        ₹{inv.total_amount.toLocaleString('en-IN')}
                      </td>
                      <td className="table-td text-sm">
                        {inv.balance_due > 0
                          ? <span className="text-red-600 font-medium">₹{inv.balance_due.toLocaleString('en-IN')}</span>
                          : <span className="text-green-600">Paid</span>
                        }
                      </td>
                      <td className="table-td">
                        <span className={INV_STATUS[inv.status] || 'badge-gray'}>
                          {inv.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="table-td text-xs">
                        {inv.tally_synced_at
                          ? <span className="text-green-600">✓ Synced</span>
                          : <span className="text-slate-400">—</span>
                        }
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {(invoiceData?.total_pages || 1) > 1 && (
            <div className="border-t border-slate-100 px-4 py-3 flex items-center justify-between">
              <p className="text-sm text-slate-500">Showing {((page - 1) * 15) + 1}–{Math.min(page * 15, invoiceData?.total || 0)} of {invoiceData?.total}</p>
              <div className="flex items-center gap-1">
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="btn-ghost btn-sm"><ChevronLeft size={14} /></button>
                <span className="text-sm text-slate-600 px-2">{page} / {invoiceData?.total_pages}</span>
                <button onClick={() => setPage(p => Math.min(invoiceData?.total_pages || 1, p + 1))} disabled={page === invoiceData?.total_pages} className="btn-ghost btn-sm"><ChevronRight size={14} /></button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Time logs table */}
      {tab === 'timelogs' && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="table-th">Date</th>
                  <th className="table-th">Client</th>
                  <th className="table-th">Description</th>
                  <th className="table-th">Duration</th>
                  <th className="table-th">Billable</th>
                  <th className="table-th">Rate</th>
                  <th className="table-th">Amount</th>
                  <th className="table-th">Billed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {tlLoading ? (
                  <tr><td colSpan={8} className="py-16 text-center"><div className="animate-spin w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full mx-auto" /></td></tr>
                ) : timeLogs.length === 0 ? (
                  <tr><td colSpan={8}>
                    <EmptyState icon={<Clock size={24} />} title="No time logs" description="Start tracking time spent on client work"
                      action={<button onClick={() => setShowTimeLog(true)} className="btn-primary btn-sm"><Plus size={13} /> Log Time</button>} />
                  </td></tr>
                ) : timeLogs.map((log: TimeLog) => (
                  <tr key={log.time_log_id} className="hover:bg-slate-50 transition-colors">
                    <td className="table-td text-xs text-slate-600">{format(parseISO(log.log_date), 'd MMM yyyy')}</td>
                    <td className="table-td text-sm text-slate-700">{log.customer?.display_name || '—'}</td>
                    <td className="table-td text-sm text-slate-700 max-w-xs truncate">{log.description}</td>
                    <td className="table-td text-sm font-medium">
                      {Math.floor(log.duration_minutes / 60)}h {log.duration_minutes % 60}m
                    </td>
                    <td className="table-td">
                      {log.is_billable
                        ? <span className="badge-green">Yes</span>
                        : <span className="badge-gray">No</span>}
                    </td>
                    <td className="table-td text-sm text-slate-600">
                      {log.hourly_rate ? `₹${log.hourly_rate}/hr` : '—'}
                    </td>
                    <td className="table-td text-sm font-medium text-slate-900">
                      {log.line_amount ? `₹${log.line_amount.toLocaleString('en-IN')}` : '—'}
                    </td>
                    <td className="table-td">
                      {log.is_billed
                        ? <span className="badge-green">Billed</span>
                        : <span className="badge-yellow">Unbilled</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Expenses table */}
      {tab === 'expenses' && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="table-th">Date</th>
                  <th className="table-th">Category</th>
                  <th className="table-th">Description</th>
                  <th className="table-th">Vendor</th>
                  <th className="table-th">Amount</th>
                  <th className="table-th">Status</th>
                  <th className="table-th">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {expLoading ? (
                  <tr><td colSpan={7} className="py-16 text-center"><div className="animate-spin w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full mx-auto" /></td></tr>
                ) : expenses.length === 0 ? (
                  <tr><td colSpan={7}>
                    <EmptyState icon={<Receipt size={24} />} title="No expenses" description="Log your firm's expenses here"
                      action={<button onClick={() => setShowExpense(true)} className="btn-primary btn-sm"><Plus size={13} /> Add Expense</button>} />
                  </td></tr>
                ) : expenses.map((exp: Expense) => (
                  <tr key={exp.expense_id} className="hover:bg-slate-50 transition-colors">
                    <td className="table-td text-xs text-slate-600">{format(parseISO(exp.expense_date), 'd MMM yyyy')}</td>
                    <td className="table-td">
                      <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full">
                        {exp.category.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="table-td text-sm text-slate-700 max-w-xs truncate">{exp.description}</td>
                    <td className="table-td text-sm text-slate-500">{exp.vendor_name || '—'}</td>
                    <td className="table-td text-sm font-semibold text-slate-900">
                      ₹{exp.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="table-td">
                      <StatusBadge status={exp.status} />
                    </td>
                    <td className="table-td">
                      {exp.status === 'PENDING' && (
                        <div className="flex gap-1">
                          <button onClick={() => approveExpense.mutate({ id: exp.expense_id, approve: true })}
                            className="p-1.5 rounded-lg text-green-600 hover:bg-green-50">
                            <CheckCircle size={14} />
                          </button>
                          <button onClick={() => approveExpense.mutate({ id: exp.expense_id, approve: false })}
                            className="p-1.5 rounded-lg text-red-500 hover:bg-red-50">
                            <XCircle size={14} />
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modals */}
      <InvoiceFormModal open={showInvoiceForm} onClose={() => setShowInvoiceForm(false)} />
      <InvoiceDrawer invoiceId={viewInvoiceId} onClose={() => setViewInvoiceId(null)} />
      <AddTimeLogModal open={showTimeLog} onClose={() => setShowTimeLog(false)} />
      <AddExpenseModal open={showExpense} onClose={() => setShowExpense(false)} />
    </div>
  )
}
