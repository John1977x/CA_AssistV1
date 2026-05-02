import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Plus, Search, MessageSquare, TrendingUp, UserPlus, RefreshCw,
  ChevronLeft, ChevronRight, Loader2, Phone, Mail, ArrowRightCircle,
  Calendar, IndianRupee,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { enquiriesApi } from '@/api/customers'
import { StatCard, StatusBadge, EmptyState, Modal, FormField, Tabs } from '@/components/ui'
import type { Enquiry } from '@/types/customer'
import clsx from 'clsx'

// ── Add Enquiry Form ──────────────────────────────────────────────────────────
const enquirySchema = z.object({
  full_name:          z.string().min(2, 'Required'),
  phone:              z.string().min(10, 'Valid phone required'),
  email:              z.string().email('Invalid email').optional().or(z.literal('')),
  company_name:       z.string().optional(),
  service_interested: z.array(z.string()).optional(),
  source:             z.string().optional(),
  message:            z.string().optional(),
  estimated_value:    z.number().optional(),
  follow_up_date:     z.string().optional(),
})

const SERVICES = ['GST', 'ITR', 'TDS', 'Audit', 'ROC', 'Accounting', 'Payroll', 'Investment Advisory', 'Other']
const SOURCES  = ['WALK_IN', 'WEBSITE', 'REFERRAL', 'SOCIAL_MEDIA', 'ADVERTISEMENT', 'OTHER']

function AddEnquiryModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const qc = useQueryClient()
  const { register, handleSubmit, reset, watch, setValue, formState: { errors } } = useForm({
    resolver: zodResolver(enquirySchema),
  })
  const services = watch('service_interested') || []

  const mutation = useMutation({
    mutationFn: (data: any) => enquiriesApi.create(data),
    onSuccess: () => {
      toast.success('Enquiry added!')
      qc.invalidateQueries({ queryKey: ['enquiries'] })
      qc.invalidateQueries({ queryKey: ['enquiry-stats'] })
      reset()
      onClose()
    },
  })

  const toggleService = (s: string) => {
    const current = services as string[]
    setValue('service_interested',
      current.includes(s) ? current.filter(x => x !== s) : [...current, s]
    )
  }

  return (
    <Modal open={open} onClose={onClose} title="New Enquiry" subtitle="Log a new potential client enquiry" size="lg">
      <form onSubmit={handleSubmit(d => mutation.mutate(d))} className="p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Full Name" required error={errors.full_name?.message as string}>
            <input {...register('full_name')} className={`input ${errors.full_name ? 'input-error' : ''}`} placeholder="Prospect name" />
          </FormField>
          <FormField label="Phone" required error={errors.phone?.message as string}>
            <input {...register('phone')} type="tel" className={`input ${errors.phone ? 'input-error' : ''}`} placeholder="9876543210" />
          </FormField>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <FormField label="Email" error={errors.email?.message as string}>
            <input {...register('email')} type="email" className="input" placeholder="optional@email.com" />
          </FormField>
          <FormField label="Company Name">
            <input {...register('company_name')} className="input" placeholder="If applicable" />
          </FormField>
        </div>

        <FormField label="Services Interested">
          <div className="flex flex-wrap gap-2 mt-1">
            {SERVICES.map(s => (
              <button
                key={s} type="button"
                onClick={() => toggleService(s)}
                className={clsx(
                  'text-xs px-3 py-1.5 rounded-full border transition-all',
                  (services as string[]).includes(s)
                    ? 'bg-brand-800 text-white border-brand-800'
                    : 'border-slate-200 text-slate-600 hover:border-brand-400'
                )}
              >
                {s}
              </button>
            ))}
          </div>
        </FormField>

        <div className="grid grid-cols-2 gap-4">
          <FormField label="Source">
            <select {...register('source')} className="input">
              <option value="">Select source...</option>
              {SOURCES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
            </select>
          </FormField>
          <FormField label="Estimated Annual Value (₹)">
            <input {...register('estimated_value', { valueAsNumber: true })} type="number" className="input" placeholder="e.g. 50000" />
          </FormField>
        </div>

        <FormField label="Follow-up Date">
          <input {...register('follow_up_date')} type="date" className="input" />
        </FormField>

        <FormField label="Message / Notes">
          <textarea {...register('message')} rows={3} className="input resize-none" placeholder="What are they looking for?" />
        </FormField>

        <div className="flex gap-3 pt-2 border-t border-slate-100">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button type="submit" disabled={mutation.isPending} className="btn-primary flex-1">
            {mutation.isPending ? <><Loader2 size={14} className="animate-spin" /> Saving...</> : 'Add Enquiry'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

// ── Convert Modal ─────────────────────────────────────────────────────────────
function ConvertModal({ enquiry, onClose }: { enquiry: Enquiry | null; onClose: () => void }) {
  const qc = useQueryClient()
  const [customerType, setCustomerType] = useState('INDIVIDUAL')

  const mutation = useMutation({
    mutationFn: () => enquiriesApi.convert(enquiry!.enquiry_id, { customer_type: customerType }),
    onSuccess: () => {
      toast.success(`${enquiry?.full_name} converted to client!`)
      qc.invalidateQueries({ queryKey: ['enquiries'] })
      qc.invalidateQueries({ queryKey: ['customers'] })
      qc.invalidateQueries({ queryKey: ['enquiry-stats'] })
      onClose()
    },
  })

  return (
    <Modal open={!!enquiry} onClose={onClose} title="Convert to Client" size="sm">
      <div className="p-6 space-y-4">
        <div className="bg-green-50 border border-green-100 rounded-xl p-4">
          <p className="text-sm font-medium text-green-800 mb-1">Converting Enquiry</p>
          <p className="text-sm text-green-700">{enquiry?.full_name}</p>
          <p className="text-xs text-green-600">{enquiry?.phone} · {enquiry?.enquiry_number}</p>
        </div>
        <FormField label="Client Type">
          <select value={customerType} onChange={e => setCustomerType(e.target.value)} className="input">
            {['INDIVIDUAL', 'COMPANY', 'HUF', 'LLP', 'PARTNERSHIP', 'TRUST'].map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </FormField>
        <div className="flex gap-3">
          <button onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button onClick={() => mutation.mutate()} disabled={mutation.isPending} className="btn-primary flex-1">
            {mutation.isPending ? <><Loader2 size={14} className="animate-spin" /> Converting...</> : 'Convert to Client'}
          </button>
        </div>
      </div>
    </Modal>
  )
}

// ── Enquiry Row ───────────────────────────────────────────────────────────────
function EnquiryRow({
  enquiry, onConvert, onStatusChange
}: {
  enquiry: Enquiry
  onConvert: (e: Enquiry) => void
  onStatusChange: (id: number, status: string) => void
}) {
  return (
    <tr className="hover:bg-slate-50 transition-colors">
      <td className="table-td">
        <div>
          <p className="font-medium text-slate-900 text-sm">{enquiry.full_name}</p>
          <p className="text-xs text-slate-400">{enquiry.enquiry_number}</p>
        </div>
      </td>
      <td className="table-td">
        <div className="flex items-center gap-1.5 text-sm text-slate-700">
          <Phone size={12} className="text-slate-400" />
          {enquiry.phone}
        </div>
        {enquiry.email && (
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-0.5">
            <Mail size={11} />
            {enquiry.email}
          </div>
        )}
      </td>
      <td className="table-td">
        <div className="flex flex-wrap gap-1">
          {enquiry.service_interested?.map(s => (
            <span key={s} className="text-xs bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded">{s}</span>
          ))}
          {!enquiry.service_interested?.length && <span className="text-slate-300 text-xs">—</span>}
        </div>
      </td>
      <td className="table-td text-sm text-slate-600">
        {enquiry.source?.replace('_', ' ') || '—'}
      </td>
      <td className="table-td">
        {enquiry.estimated_value ? (
          <div className="flex items-center gap-0.5 text-sm font-medium text-green-700">
            <IndianRupee size={12} />
            {enquiry.estimated_value.toLocaleString('en-IN')}
          </div>
        ) : <span className="text-slate-300 text-xs">—</span>}
      </td>
      <td className="table-td">
        {enquiry.is_converted ? (
          <span className="badge-green">Converted</span>
        ) : (
          <select
            value={enquiry.status}
            onChange={e => onStatusChange(enquiry.enquiry_id, e.target.value)}
            onClick={e => e.stopPropagation()}
            className={clsx(
              'text-xs border rounded-lg px-2 py-1 focus:outline-none focus:ring-1 focus:ring-brand-500 bg-white',
              enquiry.status === 'NEW' ? 'border-blue-200 text-blue-700' :
              enquiry.status === 'WON' ? 'border-green-200 text-green-700' :
              enquiry.status === 'LOST' ? 'border-red-200 text-red-700' :
              'border-slate-200 text-slate-600'
            )}
          >
            {['NEW', 'IN_PROGRESS', 'PROPOSAL_SENT', 'WON', 'LOST', 'DEFERRED'].map(s => (
              <option key={s} value={s}>{s.replace('_', ' ')}</option>
            ))}
          </select>
        )}
      </td>
      <td className="table-td">
        {enquiry.follow_up_date ? (
          <div className="flex items-center gap-1 text-xs text-slate-600">
            <Calendar size={11} />
            {new Date(enquiry.follow_up_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}
          </div>
        ) : <span className="text-slate-300 text-xs">—</span>}
      </td>
      <td className="table-td">
        {!enquiry.is_converted && (
          <button
            onClick={e => { e.stopPropagation(); onConvert(enquiry) }}
            className="btn-ghost btn-sm text-green-600 hover:bg-green-50"
            title="Convert to client"
          >
            <ArrowRightCircle size={15} />
          </button>
        )}
      </td>
    </tr>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function EnquiriesPage() {
  const qc = useQueryClient()
  const [showAdd, setShowAdd] = useState(false)
  const [convertEnquiry, setConvertEnquiry] = useState<Enquiry | null>(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showConverted, setShowConverted] = useState<boolean | undefined>(undefined)
  const [page, setPage] = useState(1)

  const { data: stats } = useQuery({
    queryKey: ['enquiry-stats'],
    queryFn: enquiriesApi.stats,
  })

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['enquiries', page, search, statusFilter, showConverted],
    queryFn: () => enquiriesApi.list({
      page, page_size: 15,
      search: search || undefined,
      status: statusFilter || undefined,
      is_converted: showConverted,
    }),
    placeholderData: prev => prev,
  })

  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      enquiriesApi.update(id, { status } as any),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['enquiries'] }),
  })

  const enquiries = data?.items || []
  const total = data?.total || 0
  const totalPages = data?.total_pages || 1
  const convRate = stats ? Math.round((stats.converted / (stats.total || 1)) * 100) : 0

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Enquiries</h1>
          <p className="text-sm text-slate-500 mt-0.5">{total} enquir{total !== 1 ? 'ies' : 'y'}</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="btn-primary">
          <Plus size={15} /> New Enquiry
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total Enquiries"  value={stats.total}     icon={<MessageSquare size={18} />} color="text-blue-600"   bg="bg-blue-50" />
          <StatCard label="New / Unactioned" value={stats.new}       icon={<Plus size={18} />}          color="text-orange-600" bg="bg-orange-50" />
          <StatCard label="Converted"        value={stats.converted} icon={<UserPlus size={18} />}      color="text-green-600"  bg="bg-green-50" />
          <StatCard label="Conversion Rate"  value={`${convRate}%`}  icon={<TrendingUp size={18} />}    color="text-purple-600" bg="bg-purple-50" />
        </div>
      )}

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-wrap gap-3">
          <div className="relative flex-1 min-w-48">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1) }}
              placeholder="Search by name, phone, email..."
              className="input pl-9"
            />
          </div>
          <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1) }} className="input w-40">
            <option value="">All Status</option>
            {['NEW', 'IN_PROGRESS', 'PROPOSAL_SENT', 'WON', 'LOST', 'DEFERRED'].map(s => (
              <option key={s} value={s}>{s.replace('_', ' ')}</option>
            ))}
          </select>
          <div className="flex items-center gap-2 bg-slate-100 rounded-lg px-3 py-1.5">
            <input
              type="checkbox"
              id="converted"
              checked={showConverted === true}
              onChange={e => { setShowConverted(e.target.checked ? true : undefined); setPage(1) }}
              className="w-3.5 h-3.5"
            />
            <label htmlFor="converted" className="text-xs text-slate-600 font-medium">Show Converted</label>
          </div>
          <button onClick={() => qc.invalidateQueries({ queryKey: ['enquiries'] })}
            className={clsx('btn-ghost', isFetching && 'opacity-50')}>
            <RefreshCw size={15} className={isFetching ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="table-th">Name</th>
                <th className="table-th">Contact</th>
                <th className="table-th">Services</th>
                <th className="table-th">Source</th>
                <th className="table-th">Est. Value</th>
                <th className="table-th">Status</th>
                <th className="table-th">Follow-up</th>
                <th className="table-th w-12"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr><td colSpan={8} className="py-16 text-center">
                  <div className="animate-spin w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full mx-auto" />
                </td></tr>
              ) : enquiries.length === 0 ? (
                <tr><td colSpan={8}>
                  <EmptyState
                    icon={<MessageSquare size={24} />}
                    title="No enquiries yet"
                    description="Log your first potential client enquiry"
                    action={
                      <button onClick={() => setShowAdd(true)} className="btn-primary btn-sm">
                        <Plus size={13} /> New Enquiry
                      </button>
                    }
                  />
                </td></tr>
              ) : (
                enquiries.map(e => (
                  <EnquiryRow
                    key={e.enquiry_id}
                    enquiry={e}
                    onConvert={setConvertEnquiry}
                    onStatusChange={(id, status) => updateStatus.mutate({ id, status })}
                  />
                ))
              )}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="border-t border-slate-100 px-4 py-3 flex items-center justify-between">
            <p className="text-sm text-slate-500">
              Showing {((page - 1) * 15) + 1}–{Math.min(page * 15, total)} of {total}
            </p>
            <div className="flex items-center gap-1">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="btn-ghost btn-sm">
                <ChevronLeft size={14} />
              </button>
              <span className="text-sm text-slate-600 px-2">{page} / {totalPages}</span>
              <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="btn-ghost btn-sm">
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      <AddEnquiryModal open={showAdd} onClose={() => setShowAdd(false)} />
      <ConvertModal enquiry={convertEnquiry} onClose={() => setConvertEnquiry(null)} />
    </div>
  )
}
