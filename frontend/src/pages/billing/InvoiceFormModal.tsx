import { useState, useEffect } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, Loader2, IndianRupee } from 'lucide-react'
import toast from 'react-hot-toast'
import { billingApi } from '@/api/billing'
import { customersApi } from '@/api/customers'
import { Modal, FormField } from '@/components/ui'

interface LineItemForm {
  description: string
  quantity:    number
  unit_price:  number
  unit:        string
  gst_rate_pct: number
  hsn_sac_code: string
}

interface FormData {
  customer_id:        number
  invoice_date:       string
  due_date:           string
  is_igst:            boolean
  gst_rate_pct:       number
  discount_pct:       number
  payment_terms_days: number
  notes:              string
  terms_conditions:   string
  line_items:         LineItemForm[]
}

const DEFAULT_LINE: LineItemForm = {
  description: '', quantity: 1, unit_price: 0,
  unit: 'flat', gst_rate_pct: 18, hsn_sac_code: '998231',
}

const today = new Date().toISOString().slice(0, 10)
const in30 = new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10)

interface Props { open: boolean; onClose: () => void; preCustomerId?: number }

export default function InvoiceFormModal({ open, onClose, preCustomerId }: Props) {
  const qc = useQueryClient()
  const [customerSearch, setCustomerSearch] = useState('')

  const { register, handleSubmit, control, watch, setValue, reset } = useForm<FormData>({
    defaultValues: {
      invoice_date: today, due_date: in30,
      is_igst: false, gst_rate_pct: 18, discount_pct: 0,
      payment_terms_days: 30,
      line_items: [{ ...DEFAULT_LINE }],
      customer_id: preCustomerId || 0,
    },
  })

  const { fields, append, remove } = useFieldArray({ control, name: 'line_items' })
  const lineItems = watch('line_items')
  const isIGST = watch('is_igst')
  const gstRate = watch('gst_rate_pct')
  const discPct = watch('discount_pct')
  const customerId = watch('customer_id')

  const { data: customersData } = useQuery({
    queryKey: ['customers-search-billing', customerSearch],
    queryFn: () => customersApi.list({ search: customerSearch, page_size: 8 }),
    enabled: !preCustomerId && customerSearch.length > 0,
  })

  // Tax calculations
  const subtotal = lineItems.reduce((s, li) => s + (li.quantity || 0) * (li.unit_price || 0), 0)
  const discAmt = subtotal * (discPct || 0) / 100
  const taxable = subtotal - discAmt
  const totalGst = taxable * (gstRate || 18) / 100
  const totalAmount = taxable + totalGst

  const mutation = useMutation({
    mutationFn: (data: FormData) => billingApi.createInvoice(data as any),
    onSuccess: () => {
      toast.success('Invoice created!')
      qc.invalidateQueries({ queryKey: ['invoices'] })
      qc.invalidateQueries({ queryKey: ['billing-stats'] })
      reset()
      onClose()
    },
  })

  return (
    <Modal open={open} onClose={onClose} title="New Invoice" size="lg">
      <form onSubmit={handleSubmit(d => mutation.mutate(d))} className="p-6 space-y-5">
        {/* Client */}
        {!preCustomerId && (
          <FormField label="Client" required>
            <input
              value={customerSearch}
              onChange={e => setCustomerSearch(e.target.value)}
              placeholder="Search client..."
              className="input"
            />
            {customerSearch && customersData?.items && (
              <div className="mt-1 border border-slate-200 rounded-xl bg-white shadow-lg max-h-40 overflow-y-auto">
                {customersData.items.map(c => (
                  <button key={c.customer_id} type="button"
                    onClick={() => { setValue('customer_id', c.customer_id); setCustomerSearch(c.display_name) }}
                    className="w-full text-left px-4 py-2.5 hover:bg-slate-50 text-sm">
                    <span className="font-medium">{c.display_name}</span>
                    {c.gstin && <span className="text-slate-400 ml-2 text-xs">{c.gstin}</span>}
                  </button>
                ))}
              </div>
            )}
          </FormField>
        )}

        {/* Dates */}
        <div className="grid grid-cols-3 gap-3">
          <FormField label="Invoice Date" required>
            <input {...register('invoice_date')} type="date" className="input" />
          </FormField>
          <FormField label="Due Date" required>
            <input {...register('due_date')} type="date" className="input" />
          </FormField>
          <FormField label="Payment Terms (days)">
            <input {...register('payment_terms_days', { valueAsNumber: true })} type="number" className="input" />
          </FormField>
        </div>

        {/* GST settings */}
        <div className="flex items-center gap-4 p-3 bg-slate-50 rounded-xl">
          <div className="flex items-center gap-2">
            <input {...register('is_igst')} type="checkbox" id="igst" className="w-4 h-4" />
            <label htmlFor="igst" className="text-sm font-medium text-slate-700">IGST (Interstate)</label>
          </div>
          <div className="flex items-center gap-2 ml-4">
            <label className="text-sm text-slate-600">GST Rate:</label>
            <select {...register('gst_rate_pct', { valueAsNumber: true })} className="input w-20 py-1.5">
              {[0, 5, 12, 18, 28].map(r => <option key={r} value={r}>{r}%</option>)}
            </select>
          </div>
          <div className="flex items-center gap-2 ml-4">
            <label className="text-sm text-slate-600">Discount:</label>
            <input {...register('discount_pct', { valueAsNumber: true })} type="number" step="0.5"
              className="input w-20 py-1.5" />
            <span className="text-sm text-slate-500">%</span>
          </div>
        </div>

        {/* Line Items */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-700">Line Items</h3>
            <button type="button" onClick={() => append({ ...DEFAULT_LINE })} className="btn-ghost btn-sm text-brand-700">
              <Plus size={13} /> Add Line
            </button>
          </div>

          <div className="space-y-2">
            {/* Header */}
            <div className="grid grid-cols-12 gap-2 text-xs font-medium text-slate-500 px-1">
              <span className="col-span-5">Description</span>
              <span className="col-span-1">Qty</span>
              <span className="col-span-2">Unit</span>
              <span className="col-span-2">Rate (₹)</span>
              <span className="col-span-1">Amount</span>
              <span className="col-span-1"></span>
            </div>

            {fields.map((field, idx) => {
              const li = lineItems[idx] || {}
              const lineTotal = (li.quantity || 0) * (li.unit_price || 0)
              const lineTax = lineTotal * (gstRate || 18) / 100
              return (
                <div key={field.id} className="grid grid-cols-12 gap-2 items-center bg-slate-50 rounded-lg p-2">
                  <div className="col-span-5">
                    <input {...register(`line_items.${idx}.description`)}
                      placeholder="e.g. GST Filing Services - Apr 2024"
                      className="input text-sm py-1.5" />
                  </div>
                  <div className="col-span-1">
                    <input {...register(`line_items.${idx}.quantity`, { valueAsNumber: true })}
                      type="number" step="0.5" min="0.1"
                      className="input text-sm py-1.5 text-center" />
                  </div>
                  <div className="col-span-2">
                    <select {...register(`line_items.${idx}.unit`)} className="input text-sm py-1.5">
                      <option value="flat">Flat</option>
                      <option value="hrs">Hours</option>
                      <option value="months">Months</option>
                      <option value="units">Units</option>
                    </select>
                  </div>
                  <div className="col-span-2">
                    <input {...register(`line_items.${idx}.unit_price`, { valueAsNumber: true })}
                      type="number" step="1" min="0"
                      className="input text-sm py-1.5" />
                  </div>
                  <div className="col-span-1 text-sm font-medium text-slate-700 text-right">
                    ₹{lineTotal.toLocaleString('en-IN')}
                  </div>
                  <div className="col-span-1 flex justify-end">
                    {fields.length > 1 && (
                      <button type="button" onClick={() => remove(idx)}
                        className="p-1 text-slate-400 hover:text-red-500">
                        <Trash2 size={13} />
                      </button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Totals summary */}
        <div className="bg-brand-50 border border-brand-100 rounded-xl p-4 ml-auto w-72">
          <div className="space-y-1.5 text-sm">
            <div className="flex justify-between text-slate-600">
              <span>Subtotal</span>
              <span>₹{subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
            </div>
            {discPct > 0 && (
              <div className="flex justify-between text-green-700">
                <span>Discount ({discPct}%)</span>
                <span>- ₹{discAmt.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
            )}
            <div className="flex justify-between text-slate-600">
              <span>Taxable</span>
              <span>₹{taxable.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
            </div>
            {isIGST ? (
              <div className="flex justify-between text-slate-600">
                <span>IGST ({gstRate}%)</span>
                <span>₹{totalGst.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
            ) : (
              <>
                <div className="flex justify-between text-slate-600">
                  <span>CGST ({gstRate / 2}%)</span>
                  <span>₹{(totalGst / 2).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>SGST ({gstRate / 2}%)</span>
                  <span>₹{(totalGst / 2).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                </div>
              </>
            )}
            <div className="flex justify-between font-bold text-slate-900 pt-2 border-t border-brand-200 text-base">
              <span>Total</span>
              <span className="flex items-center gap-0.5">
                <IndianRupee size={14} />
                {totalAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>
        </div>

        {/* Notes */}
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Notes (shown on invoice)">
            <textarea {...register('notes')} rows={2} className="input resize-none text-sm"
              placeholder="Payment details, thank you note..." />
          </FormField>
          <FormField label="Terms & Conditions">
            <textarea {...register('terms_conditions')} rows={2} className="input resize-none text-sm"
              placeholder="e.g. Payment due within 30 days..." />
          </FormField>
        </div>

        <div className="flex gap-3 pt-2 border-t border-slate-100">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button type="submit" disabled={mutation.isPending} className="btn-primary flex-1">
            {mutation.isPending ? <><Loader2 size={14} className="animate-spin" /> Creating...</> : 'Create Invoice'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
