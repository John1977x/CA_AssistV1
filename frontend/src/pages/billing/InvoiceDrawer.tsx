import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import {
  IndianRupee, Send, Download, XCircle, CheckCircle, Loader2, Plus,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { format, parseISO, isPast } from 'date-fns'
import { billingApi } from '@/api/billing'
import { Drawer, StatusBadge, Tabs, FormField } from '@/components/ui'
import { PAYMENT_MODES } from '@/types/billing'
import clsx from 'clsx'

const STATUS_COLORS: Record<string, string> = {
  DRAFT:          'bg-slate-100 text-slate-600',
  SENT:           'bg-blue-50 text-blue-700',
  PARTIALLY_PAID: 'bg-yellow-50 text-yellow-700',
  PAID:           'bg-green-50 text-green-700',
  CANCELLED:      'bg-red-50 text-red-600',
  OVERDUE:        'bg-red-100 text-red-700 font-bold',
}

function RecordPaymentForm({ invoiceId, balanceDue, onSuccess }: {
  invoiceId: number; balanceDue: number; onSuccess: () => void
}) {
  const { register, handleSubmit, reset } = useForm({
    defaultValues: { payment_date: new Date().toISOString().slice(0, 10), amount: balanceDue, payment_mode: 'NEFT', tds_deducted: 0 }
  })

  const mutation = useMutation({
    mutationFn: (data: any) => billingApi.recordPayment(invoiceId, data),
    onSuccess: () => {
      toast.success('Payment recorded!')
      reset()
      onSuccess()
    },
  })

  return (
    <form onSubmit={handleSubmit(d => mutation.mutate(d))} className="space-y-3 bg-green-50 border border-green-100 rounded-xl p-4">
      <h4 className="text-sm font-semibold text-green-800">Record Payment</h4>
      <div className="grid grid-cols-2 gap-3">
        <FormField label="Payment Date">
          <input {...register('payment_date')} type="date" className="input text-sm py-1.5" />
        </FormField>
        <FormField label="Amount (₹)">
          <input {...register('amount', { valueAsNumber: true })} type="number" step="0.01" className="input text-sm py-1.5" />
        </FormField>
        <FormField label="Mode">
          <select {...register('payment_mode')} className="input text-sm py-1.5">
            {PAYMENT_MODES.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </FormField>
        <FormField label="Reference / UTR">
          <input {...register('reference_number')} className="input text-sm py-1.5" placeholder="UTR / cheque no." />
        </FormField>
        <FormField label="TDS Deducted (₹)">
          <input {...register('tds_deducted', { valueAsNumber: true })} type="number" step="0.01" className="input text-sm py-1.5" placeholder="0" />
        </FormField>
        <FormField label="Bank Name">
          <input {...register('bank_name')} className="input text-sm py-1.5" placeholder="Optional" />
        </FormField>
      </div>
      <button type="submit" disabled={mutation.isPending} className="btn-primary w-full">
        {mutation.isPending ? <><Loader2 size={13} className="animate-spin" /> Saving...</> : <><CheckCircle size={13} /> Record Payment</>}
      </button>
    </form>
  )
}

interface Props { invoiceId: number | null; onClose: () => void }

export default function InvoiceDrawer({ invoiceId, onClose }: Props) {
  const qc = useQueryClient()
  const [tab, setTab] = useState('items')
  const [showPayForm, setShowPayForm] = useState(false)

  const { data: invoice, isLoading } = useQuery({
    queryKey: ['invoice', invoiceId],
    queryFn: () => billingApi.getInvoice(invoiceId!),
    enabled: !!invoiceId,
  })

  const sendMutation = useMutation({
    mutationFn: () => billingApi.sendInvoice(invoiceId!),
    onSuccess: () => {
      toast.success('Invoice marked as sent!')
      qc.invalidateQueries({ queryKey: ['invoice', invoiceId] })
      qc.invalidateQueries({ queryKey: ['invoices'] })
    },
  })

  const cancelMutation = useMutation({
    mutationFn: () => billingApi.cancelInvoice(invoiceId!),
    onSuccess: () => {
      toast.success('Invoice cancelled.')
      qc.invalidateQueries({ queryKey: ['invoice', invoiceId] })
      qc.invalidateQueries({ queryKey: ['invoices'] })
    },
  })

  const handleTallyExport = async () => {
    if (!invoiceId) return
    const blob = await billingApi.tallyExport([invoiceId])
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `tally_${invoice?.invoice_number}.xml`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Tally XML exported!')
  }

  const paidPct = invoice ? Math.min(100, Math.round((invoice.amount_paid / invoice.total_amount) * 100)) : 0

  return (
    <Drawer
      open={!!invoiceId}
      onClose={onClose}
      title={invoice?.invoice_number || 'Loading...'}
      subtitle={invoice?.customer?.display_name || ''}
      width="lg"
    >
      {isLoading ? (
        <div className="flex items-center justify-center h-48">
          <Loader2 className="animate-spin text-brand-600" size={28} />
        </div>
      ) : invoice ? (
        <div>
          {/* Summary card */}
          <div className="px-6 py-4 bg-slate-50 border-b border-slate-100">
            <div className="flex items-start justify-between mb-3">
              <div>
                <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${STATUS_COLORS[invoice.status] || ''}`}>
                  {invoice.status.replace('_', ' ')}
                </span>
                <p className="text-xs text-slate-500 mt-1.5">
                  Invoice date: {format(parseISO(invoice.invoice_date), 'd MMM yyyy')} ·
                  Due: <span className={clsx(
                    isPast(parseISO(invoice.due_date)) && !['PAID', 'CANCELLED'].includes(invoice.status)
                      ? 'text-red-600 font-semibold' : ''
                  )}>
                    {format(parseISO(invoice.due_date), 'd MMM yyyy')}
                  </span>
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-slate-900 flex items-center gap-0.5">
                  <IndianRupee size={16} />
                  {invoice.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </p>
                {invoice.balance_due > 0 && (
                  <p className="text-xs text-red-600 font-medium mt-0.5">
                    Balance: ₹{invoice.balance_due.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </p>
                )}
              </div>
            </div>

            {/* Payment progress */}
            <div>
              <div className="flex justify-between text-xs text-slate-500 mb-1">
                <span>₹{invoice.amount_paid.toLocaleString('en-IN')} collected</span>
                <span>{paidPct}%</span>
              </div>
              <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className={clsx('h-full rounded-full transition-all', paidPct === 100 ? 'bg-green-500' : 'bg-brand-600')}
                  style={{ width: `${paidPct}%` }}
                />
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 px-6 py-3 border-b border-slate-100 overflow-x-auto">
            {invoice.status === 'DRAFT' && (
              <button onClick={() => sendMutation.mutate()} disabled={sendMutation.isPending}
                className="btn-primary btn-sm">
                <Send size={13} /> Mark Sent
              </button>
            )}
            {!['PAID', 'CANCELLED'].includes(invoice.status) && invoice.balance_due > 0 && (
              <button onClick={() => setShowPayForm(!showPayForm)}
                className="btn-secondary btn-sm text-green-700 border-green-200 hover:bg-green-50">
                <Plus size={13} /> Record Payment
              </button>
            )}
            <button onClick={handleTallyExport} className="btn-ghost btn-sm">
              <Download size={13} /> Tally XML
            </button>
            {invoice.status !== 'CANCELLED' && invoice.status !== 'PAID' && (
              <button onClick={() => { if (confirm('Cancel this invoice?')) cancelMutation.mutate() }}
                className="btn-ghost btn-sm text-red-600 hover:bg-red-50 ml-auto">
                <XCircle size={13} /> Cancel
              </button>
            )}
          </div>

          {/* Payment form */}
          {showPayForm && (
            <div className="px-6 py-4 border-b border-slate-100">
              <RecordPaymentForm
                invoiceId={invoice.invoice_id}
                balanceDue={invoice.balance_due}
                onSuccess={() => {
                  setShowPayForm(false)
                  qc.invalidateQueries({ queryKey: ['invoice', invoiceId] })
                  qc.invalidateQueries({ queryKey: ['invoices'] })
                  qc.invalidateQueries({ queryKey: ['billing-stats'] })
                }}
              />
            </div>
          )}

          {/* Tabs */}
          <div className="px-6 pt-4">
            <Tabs
              tabs={[
                { key: 'items',    label: 'Line Items' },
                { key: 'tax',      label: 'Tax Summary' },
                { key: 'payments', label: 'Payments', count: invoice.payments?.length },
              ]}
              active={tab}
              onChange={setTab}
            />
          </div>

          <div className="px-6 py-4">
            {tab === 'items' && (
              <div>
                {/* Client info */}
                <div className="bg-slate-50 rounded-xl p-3 mb-4 text-sm">
                  <p className="font-semibold text-slate-900">{invoice.customer?.display_name}</p>
                  {invoice.customer?.gstin && <p className="text-slate-500 text-xs">GSTIN: {invoice.customer.gstin}</p>}
                  {invoice.customer?.pan && <p className="text-slate-500 text-xs">PAN: {invoice.customer.pan}</p>}
                </div>

                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-xs text-slate-500 border-b border-slate-200">
                      <th className="text-left py-2 font-medium">Description</th>
                      <th className="text-right py-2 font-medium">Qty</th>
                      <th className="text-right py-2 font-medium">Rate</th>
                      <th className="text-right py-2 font-medium">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {invoice.line_items?.map(li => (
                      <tr key={li.line_item_id}>
                        <td className="py-2.5">
                          <p className="font-medium text-slate-800">{li.description}</p>
                          {li.hsn_sac_code && <p className="text-xs text-slate-400">SAC: {li.hsn_sac_code}</p>}
                        </td>
                        <td className="py-2.5 text-right text-slate-600">{li.quantity} {li.unit}</td>
                        <td className="py-2.5 text-right text-slate-600">₹{li.unit_price.toLocaleString('en-IN')}</td>
                        <td className="py-2.5 text-right font-medium text-slate-900">₹{li.line_total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {invoice.notes && (
                  <div className="mt-4 p-3 bg-yellow-50 rounded-lg text-sm text-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Notes</p>
                    {invoice.notes}
                  </div>
                )}
              </div>
            )}

            {tab === 'tax' && (
              <div className="space-y-2 text-sm max-w-xs ml-auto">
                {[
                  { label: 'Subtotal', value: invoice.subtotal, plain: true },
                  invoice.discount_amount > 0 ? { label: `Discount`, value: -invoice.discount_amount, plain: false } : null,
                  { label: 'Taxable Amount', value: invoice.taxable_amount, plain: true },
                  invoice.is_igst
                    ? { label: `IGST @ ${invoice.gst_rate_pct}%`, value: invoice.igst_amount, plain: false }
                    : null,
                  !invoice.is_igst && invoice.cgst_amount > 0
                    ? { label: `CGST @ ${invoice.gst_rate_pct / 2}%`, value: invoice.cgst_amount, plain: false }
                    : null,
                  !invoice.is_igst && invoice.sgst_amount > 0
                    ? { label: `SGST @ ${invoice.gst_rate_pct / 2}%`, value: invoice.sgst_amount, plain: false }
                    : null,
                ].filter(Boolean).map((row: any) => (
                  <div key={row.label} className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-600">{row.label}</span>
                    <span className={row.value < 0 ? 'text-green-600' : 'text-slate-900'}>
                      ₹{Math.abs(row.value).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                ))}
                <div className="flex justify-between py-2 font-bold text-slate-900 text-base border-t-2 border-slate-300 mt-1">
                  <span>Total</span>
                  <span>₹{invoice.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                </div>
              </div>
            )}

            {tab === 'payments' && (
              <div>
                {invoice.payments && invoice.payments.length > 0 ? (
                  <div className="space-y-3">
                    {invoice.payments.map((p: any) => (
                      <div key={p.payment_id} className="bg-green-50 border border-green-100 rounded-xl p-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-semibold text-green-800 text-sm flex items-center gap-0.5">
                              <IndianRupee size={12} />
                              {p.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                            </p>
                            <p className="text-xs text-green-700 mt-0.5">
                              {format(parseISO(p.payment_date), 'd MMM yyyy')} · {p.payment_mode}
                            </p>
                          </div>
                          {p.reference_number && (
                            <span className="text-xs text-slate-500 font-mono bg-white px-2 py-0.5 rounded-full border border-slate-200">
                              {p.reference_number}
                            </span>
                          )}
                        </div>
                        {p.tds_deducted > 0 && (
                          <p className="text-xs text-orange-700 mt-1">TDS: ₹{p.tds_deducted.toLocaleString('en-IN')}</p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-400 text-sm text-center py-8">No payments recorded yet.</p>
                )}
              </div>
            )}
          </div>
        </div>
      ) : null}
    </Drawer>
  )
}
