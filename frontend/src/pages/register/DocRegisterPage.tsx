import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Plus, Search, BookOpen, ArrowDown, ArrowUp, Clock,
  ChevronLeft, ChevronRight, RefreshCw, Pencil, Trash2,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { registerApi, DOC_TYPES } from '@/api/register'
import type { RegisterEntry, RegisterCreatePayload } from '@/api/register'
import { StatCard, EmptyState, Modal, FormField } from '@/components/ui'
import { customersApi } from '@/api/customers'
import { usersApi } from '@/api/users'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import type { Customer } from '@/types/customer'
import type { User } from '@/types/auth'
import { format, parseISO } from 'date-fns'
import clsx from 'clsx'

// ── Schema (no owner_id — comes from auth context) ────────────────────────────
const schema = z.object({
  in_out_ward:     z.enum(['INWARD', 'OUTWARD']),
  doc_date:        z.string().min(1, 'Required'),
  doc_type:        z.string().min(1, 'Required'),
  doc_description: z.string().min(2, 'Required'),
  client_id:       z.number().nullable().optional(),
  employee_id:     z.number().nullable().optional(),
  sent_date:       z.string().nullable().optional(),
  acknowledgement: z.string().max(200).nullable().optional(),
})
type FormData = z.infer<typeof schema>

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmt(d: string | null) {
  if (!d) return '—'
  try { return format(parseISO(d), 'd MMM yyyy') } catch { return d }
}

function userName(u: User) {
  return u.display_name || `${u.first_name} ${u.last_name}`.trim()
}

function WardBadge({ ward }: { ward: string }) {
  return (
    <span className={clsx(
      'inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full',
      ward === 'INWARD' ? 'bg-blue-50 text-blue-700' : 'bg-orange-50 text-orange-700'
    )}>
      {ward === 'INWARD' ? <ArrowDown size={11} /> : <ArrowUp size={11} />}
      {ward}
    </span>
  )
}

// ── Create / Edit Modal ───────────────────────────────────────────────────────
interface RegisterModalProps {
  open:       boolean
  onClose:    () => void
  entry?:     RegisterEntry | null
  clients:    Customer[]
  employees:  User[]
  ownerId:    number
}

function RegisterModal({ open, onClose, entry, clients, employees, ownerId }: RegisterModalProps) {
  const qc     = useQueryClient()
  const isEdit = !!entry

  const { register, handleSubmit, reset, control, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { in_out_ward: 'INWARD', doc_date: '', doc_type: '', doc_description: '' },
  })

  // Re-populate form whenever the entry being edited changes
  useEffect(() => {
    if (entry) {
      reset({
        in_out_ward:     entry.in_out_ward,
        doc_date:        entry.doc_date,
        doc_type:        entry.doc_type,
        doc_description: entry.doc_description,
        client_id:       entry.client_id   ?? null,
        employee_id:     entry.employee_id ?? null,
        sent_date:       entry.sent_date   ?? '',
        acknowledgement: entry.acknowledgement ?? '',
      })
    } else {
      reset({ in_out_ward: 'INWARD', doc_date: '', doc_type: '', doc_description: '' })
    }
  }, [entry, reset])

  const mutation = useMutation({
    mutationFn: (data: FormData) => {
      const payload: RegisterCreatePayload = {
        ...data,
        owner_id:        ownerId,
        sent_date:       data.sent_date || null,
        acknowledgement: data.acknowledgement || null,
        client_id:       data.client_id   || null,
        employee_id:     data.employee_id || null,
      }
      return isEdit
        ? registerApi.update(entry!.register_id, payload)
        : registerApi.create(payload)
    },
    onSuccess: () => {
      toast.success(isEdit ? 'Entry updated.' : 'Entry added.')
      qc.invalidateQueries({ queryKey: ['registers'] })
      qc.invalidateQueries({ queryKey: ['register-stats'] })
      reset()
      onClose()
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || 'Failed to save entry.'
      toast.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    },
  })

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? 'Edit Register Entry' : 'New Register Entry'}
      subtitle="Inward / Outward document register"
      size="lg"
    >
      <form onSubmit={handleSubmit(d => mutation.mutate(d))} className="p-6 space-y-4">
        {/* Direction */}
        <FormField label="Direction" required error={errors.in_out_ward?.message}>
          <Controller
            name="in_out_ward"
            control={control}
            render={({ field }) => (
              <div className="flex gap-3 mt-1">
                {(['INWARD', 'OUTWARD'] as const).map(w => (
                  <button
                    key={w}
                    type="button"
                    onClick={() => field.onChange(w)}
                    className={clsx(
                      'flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl border text-sm font-semibold transition-all',
                      field.value === w
                        ? w === 'INWARD'
                          ? 'bg-blue-600 border-blue-600 text-white'
                          : 'bg-orange-500 border-orange-500 text-white'
                        : 'border-slate-200 text-slate-600 hover:border-slate-400'
                    )}
                  >
                    {w === 'INWARD' ? <ArrowDown size={14} /> : <ArrowUp size={14} />}
                    {w}
                  </button>
                ))}
              </div>
            )}
          />
        </FormField>

        <div className="grid grid-cols-2 gap-4">
          <FormField label="Document Date" required error={errors.doc_date?.message}>
            <input type="date" {...register('doc_date')} className={`input ${errors.doc_date ? 'input-error' : ''}`} />
          </FormField>
          <FormField label="Document Type" required error={errors.doc_type?.message}>
            <select {...register('doc_type')} className={`input ${errors.doc_type ? 'input-error' : ''}`}>
              <option value="">Select type</option>
              {DOC_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </FormField>
        </div>

        <FormField label="Description" required error={errors.doc_description?.message}>
          <textarea
            {...register('doc_description')}
            rows={2}
            placeholder="Brief description of the document..."
            className={`input resize-none ${errors.doc_description ? 'input-error' : ''}`}
          />
        </FormField>

        <div className="grid grid-cols-2 gap-4">
          {/* Client from customer table */}
          <FormField label="Client">
            <select
              {...register('client_id', { setValueAs: v => v === '' ? null : Number(v) })}
              className="input"
            >
              <option value="">— None —</option>
              {clients.map(c => (
                <option key={c.customer_id} value={c.customer_id}>{c.display_name}</option>
              ))}
            </select>
          </FormField>

          {/* Employee from user table */}
          <FormField label="Employee">
            <select
              {...register('employee_id', { setValueAs: v => v === '' ? null : Number(v) })}
              className="input"
            >
              <option value="">— None —</option>
              {employees.map(u => (
                <option key={u.user_id} value={u.user_id}>{userName(u)}</option>
              ))}
            </select>
          </FormField>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <FormField label="Sent Date">
            <input type="date" {...register('sent_date')} className="input" />
          </FormField>
          <FormField label="Acknowledgement" error={errors.acknowledgement?.message}>
            <input
              {...register('acknowledgement')}
              placeholder="Ack. number or note"
              className="input"
              maxLength={200}
            />
          </FormField>
        </div>

        <div className="flex justify-end gap-3 pt-2 border-t border-slate-100">
          <button type="button" onClick={onClose} className="btn-ghost">Cancel</button>
          <button type="submit" className="btn-primary" disabled={mutation.isPending}>
            {mutation.isPending ? 'Saving…' : isEdit ? 'Save Changes' : 'Add Entry'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function DocRegisterPage() {
  const qc               = useQueryClient()
  const { user, company } = useAuthStoreV2()
  const role             = company?.role   // 'OWNER' | 'MANAGER' | 'EMPLOYEE' | 'CLIENT'
  const canCreate        = true
  const canDelete        = role === 'OWNER' || role === 'MANAGER'

  const [wardFilter,    setWardFilter]    = useState<'' | 'INWARD' | 'OUTWARD'>('')
  const [docTypeFilter, setDocTypeFilter] = useState('')
  const [search,        setSearch]        = useState('')
  const [page,          setPage]          = useState(1)
  const [modalOpen,     setModalOpen]     = useState(false)
  const [editEntry,     setEditEntry]     = useState<RegisterEntry | null>(null)

  // Pre-load clients and employees for dropdowns and table name resolution
  const { data: customersData } = useQuery({
    queryKey: ['customers-dropdown'],
    queryFn: () => customersApi.list({ page_size: 100 }),
    staleTime: 60_000,
  })
  const { data: usersData } = useQuery({
    queryKey: ['users-dropdown'],
    queryFn: () => usersApi.list({ page_size: 100 }),
    staleTime: 60_000,
  })

  const clients   = customersData?.items ?? []
  const employees = usersData?.items     ?? []

  // Lookup maps for table display
  const clientMap:   Record<number, string> = {}
  const employeeMap: Record<number, string> = {}
  clients.forEach(c   => { clientMap[c.customer_id]  = c.display_name })
  employees.forEach(u => { employeeMap[u.user_id]    = userName(u) })

  const { data: stats } = useQuery({
    queryKey: ['register-stats'],
    queryFn: registerApi.getStats,
  })

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['registers', page, wardFilter, docTypeFilter, search],
    queryFn: () => registerApi.list({
      page,
      page_size:   20,
      in_out_ward: wardFilter    || undefined,
      doc_type:    docTypeFilter || undefined,
      search:      search        || undefined,
    }),
    placeholderData: prev => prev,
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => registerApi.delete(id),
    onSuccess: () => {
      toast.success('Entry deleted.')
      qc.invalidateQueries({ queryKey: ['registers'] })
      qc.invalidateQueries({ queryKey: ['register-stats'] })
    },
    onError: () => toast.error('Delete failed.'),
  })

  const entries    = data?.items    ?? []
  const total      = data?.total    ?? 0
  const totalPages = data?.total_pages ?? 1

  const openCreate = () => { setEditEntry(null); setModalOpen(true) }
  const openEdit   = (e: RegisterEntry) => { setEditEntry(e); setModalOpen(true) }
  const closeModal = () => { setModalOpen(false); setEditEntry(null) }

  const confirmDelete = (e: RegisterEntry) => {
    if (confirm(`Delete "${e.doc_type} – ${e.doc_description.slice(0, 40)}"?`)) {
      deleteMutation.mutate(e.register_id)
    }
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Inward / Outward Register</h1>
          <p className="text-sm text-slate-500 mt-0.5">{total} entr{total !== 1 ? 'ies' : 'y'}</p>
        </div>
        {canCreate && (
          <button onClick={openCreate} className="btn-primary">
            <Plus size={15} /> New Entry
          </button>
        )}
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total"       value={stats.total}       icon={<BookOpen size={18} />}  color="text-blue-600"   bg="bg-blue-50" />
          <StatCard label="Inward"      value={stats.inward}      icon={<ArrowDown size={18} />} color="text-indigo-600" bg="bg-indigo-50" />
          <StatCard label="Outward"     value={stats.outward}     icon={<ArrowUp size={18} />}   color="text-orange-600" bg="bg-orange-50" />
          <StatCard label="Pending Ack" value={stats.pending_ack} icon={<Clock size={18} />}     color="text-red-600"    bg="bg-red-50" />
        </div>
      )}

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-wrap gap-3">
          <div className="flex rounded-lg border border-slate-200 overflow-hidden text-sm font-medium">
            {(['', 'INWARD', 'OUTWARD'] as const).map(w => (
              <button
                key={w}
                onClick={() => { setWardFilter(w); setPage(1) }}
                className={clsx(
                  'px-3 py-1.5 transition-colors',
                  wardFilter === w ? 'bg-brand-700 text-white' : 'text-slate-600 hover:bg-slate-50'
                )}
              >
                {w === '' ? 'All' : w}
              </button>
            ))}
          </div>

          <select
            value={docTypeFilter}
            onChange={e => { setDocTypeFilter(e.target.value); setPage(1) }}
            className="input w-40"
          >
            <option value="">All Types</option>
            {DOC_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
          </select>

          <div className="relative flex-1 min-w-48">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1) }}
              placeholder="Search description / acknowledgement…"
              className="input pl-9"
            />
          </div>

          <button
            onClick={() => qc.invalidateQueries({ queryKey: ['registers'] })}
            className={clsx('btn-ghost', isFetching && 'opacity-50')}
          >
            <RefreshCw size={14} className={isFetching ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="table-th">Date</th>
                <th className="table-th">Direction</th>
                <th className="table-th">Type</th>
                <th className="table-th">Description</th>
                <th className="table-th">Client</th>
                <th className="table-th">Employee</th>
                <th className="table-th">Sent Date</th>
                <th className="table-th">Acknowledgement</th>
                <th className="table-th w-20">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={9} className="py-16 text-center">
                    <div className="animate-spin w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full mx-auto" />
                  </td>
                </tr>
              ) : entries.length === 0 ? (
                <tr>
                  <td colSpan={9}>
                    <EmptyState
                      icon={<BookOpen size={24} />}
                      title="No entries found"
                      description="Start tracking your inward and outward correspondence"
                      action={canCreate ? (
                        <button onClick={openCreate} className="btn-primary btn-sm">
                          <Plus size={13} /> New Entry
                        </button>
                      ) : undefined}
                    />
                  </td>
                </tr>
              ) : (
                entries.map(e => (
                  <tr key={e.register_id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="table-td text-sm text-slate-700 whitespace-nowrap">{fmt(e.doc_date)}</td>
                    <td className="table-td"><WardBadge ward={e.in_out_ward} /></td>
                    <td className="table-td">
                      <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full font-medium">
                        {e.doc_type}
                      </span>
                    </td>
                    <td className="table-td text-sm text-slate-700 max-w-[200px]">
                      <span className="line-clamp-2">{e.doc_description}</span>
                    </td>
                    <td className="table-td text-sm text-slate-600">
                      {e.client_id ? (clientMap[e.client_id] ?? `#${e.client_id}`) : '—'}
                    </td>
                    <td className="table-td text-sm text-slate-600">
                      {e.employee_id ? (employeeMap[e.employee_id] ?? `#${e.employee_id}`) : '—'}
                    </td>
                    <td className="table-td text-sm text-slate-500 whitespace-nowrap">{fmt(e.sent_date)}</td>
                    <td className="table-td text-sm max-w-[140px]">
                      {e.acknowledgement
                        ? <span className="text-green-700 font-medium truncate block">{e.acknowledgement}</span>
                        : <span className="text-slate-300 italic text-xs">pending</span>}
                    </td>
                    <td className="table-td">
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => openEdit(e)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-brand-600 hover:bg-brand-50 transition-colors"
                          title="Edit"
                        >
                          <Pencil size={13} />
                        </button>
                        {canDelete && (
                          <button
                            onClick={() => confirmDelete(e)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                            title="Delete"
                            disabled={deleteMutation.isPending}
                          >
                            <Trash2 size={13} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="border-t border-slate-100 px-4 py-3 flex items-center justify-between">
            <p className="text-sm text-slate-500">
              Showing {((page - 1) * 20) + 1}–{Math.min(page * 20, total)} of {total}
            </p>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-ghost btn-sm"
              >
                <ChevronLeft size={14} />
              </button>
              <span className="text-sm text-slate-600 px-2">{page} / {totalPages}</span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="btn-ghost btn-sm"
              >
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      <RegisterModal
        open={modalOpen}
        onClose={closeModal}
        entry={editEntry}
        clients={clients}
        employees={employees}
        ownerId={user?.user_id ?? 0}
      />
    </div>
  )
}
