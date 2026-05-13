import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Plus, Pencil, Trash2, Loader2, ChevronLeft, ChevronRight, CheckCircle, XCircle, Paperclip } from 'lucide-react'
import toast from 'react-hot-toast'
import { leaveApplicationApi, LEAVE_STATUSES, STATUS_COLORS } from '@/api/leaveApplication'
import type { LeaveApplication, Approver } from '@/api/leaveApplication'
import { LEAVE_TYPES } from '@/api/leave'
import { Modal, FormField } from '@/components/ui'
import { useAuthStoreV2 } from '@/store/authStoreV2'

const today = new Date().toISOString().split('T')[0]

const schema = z.object({
  leave_type:     z.string().min(1, 'Required'),
  leave_date:     z.string().min(1, 'Required'),
  from_date:      z.string().min(1, 'Required'),
  to_date:        z.string().min(1, 'Required'),
  reason:         z.string().optional(),
  attachment_url: z.string().max(500).optional(),
  approver_id:    z.number().nullable().optional(),
})
type FormData = z.infer<typeof schema>

function LeaveAppFormModal({
  open, onClose, entry,
}: { open: boolean; onClose: () => void; entry: LeaveApplication | null }) {
  const qc = useQueryClient()
  const isEdit = !!entry

  const { data: approvers = [] } = useQuery<Approver[]>({
    queryKey: ['leave-approvers'],
    queryFn: leaveApplicationApi.approvers,
    staleTime: 60_000,
  })

  const { register, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { leave_type: '', leave_date: today, from_date: today, to_date: today, reason: '', attachment_url: '', approver_id: null },
  })

  useEffect(() => {
    if (entry) {
      reset({
        leave_type:     entry.leave_type,
        leave_date:     entry.leave_date,
        from_date:      entry.from_date,
        to_date:        entry.to_date,
        reason:         entry.reason ?? '',
        attachment_url: entry.attachment_url ?? '',
        approver_id:    entry.approver_id ?? null,
      })
    } else {
      reset({ leave_type: '', leave_date: today, from_date: today, to_date: today, reason: '', attachment_url: '', approver_id: null })
    }
  }, [entry, open, reset])

  const mutation = useMutation({
    mutationFn: (data: FormData) => {
      const payload = {
        ...data,
        approver_id: data.approver_id || null,
        reason: data.reason || undefined,
        attachment_url: data.attachment_url || undefined,
      }
      return isEdit
        ? leaveApplicationApi.update(entry!.leave_application_id, payload)
        : leaveApplicationApi.create(payload as any)
    },
    onSuccess: () => {
      toast.success(isEdit ? 'Application updated.' : 'Leave application submitted.')
      qc.invalidateQueries({ queryKey: ['leave-applications'] })
      onClose()
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail || 'Failed to save.'),
  })

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? 'Edit Leave Application' : 'Apply for Leave'} size="md">
      <form onSubmit={handleSubmit(d => mutation.mutate(d))} className="p-6 space-y-4">
        <FormField label="Leave Type" required error={errors.leave_type?.message}>
          <select className="input" value={watch('leave_type')} onChange={e => setValue('leave_type', e.target.value)}>
            <option value="">Select type...</option>
            {LEAVE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </FormField>

        <div className="grid grid-cols-3 gap-4">
          <FormField label="Leave Date" required error={errors.leave_date?.message}>
            <input type="date" className="input" {...register('leave_date')} />
          </FormField>
          <FormField label="From Date" required error={errors.from_date?.message}>
            <input type="date" className="input" {...register('from_date')} />
          </FormField>
          <FormField label="To Date" required error={errors.to_date?.message}>
            <input type="date" className="input" {...register('to_date')} />
          </FormField>
        </div>

        <FormField label="Reason">
          <textarea className="input min-h-[80px]" placeholder="Reason for leave..." {...register('reason')} />
        </FormField>

        <FormField label="Attachment URL">
          <div className="relative">
            <Paperclip size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input type="url" className="input pl-8" placeholder="https://..." {...register('attachment_url')} />
          </div>
        </FormField>

        <FormField label="Approver (Manager)">
          <select
            className="input"
            value={watch('approver_id') ?? ''}
            onChange={e => setValue('approver_id', e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">Select approver...</option>
            {approvers.map(a => <option key={a.user_id} value={a.user_id}>{a.name}</option>)}
          </select>
        </FormField>

        <div className="flex gap-3 pt-2 border-t border-slate-100">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button type="submit" disabled={mutation.isPending} className="btn-primary flex-1">
            {mutation.isPending
              ? <><Loader2 size={14} className="animate-spin" /> Saving...</>
              : isEdit ? 'Save Changes' : 'Submit Application'
            }
          </button>
        </div>
      </form>
    </Modal>
  )
}

function ApproveModal({
  entry, onClose,
}: { entry: LeaveApplication; onClose: () => void }) {
  const qc = useQueryClient()
  const [notes, setNotes] = useState('')

  const approveMutation = useMutation({
    mutationFn: (status: 'APPROVED' | 'REJECTED') =>
      leaveApplicationApi.update(entry.leave_application_id, { status, approval_notes: notes }),
    onSuccess: (_, status) => {
      toast.success(status === 'APPROVED' ? 'Application approved.' : 'Application rejected.')
      qc.invalidateQueries({ queryKey: ['leave-applications'] })
      onClose()
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail || 'Failed.'),
  })

  return (
    <Modal open onClose={onClose} title="Review Leave Application" size="sm">
      <div className="p-6 space-y-4">
        <div className="text-sm text-slate-600 space-y-1">
          <p><span className="font-medium">Employee:</span> {entry.employee_name}</p>
          <p><span className="font-medium">Type:</span> {entry.leave_type}</p>
          <p><span className="font-medium">Period:</span> {entry.from_date} → {entry.to_date}</p>
          {entry.reason && <p><span className="font-medium">Reason:</span> {entry.reason}</p>}
        </div>
        <div>
          <label className="label">Approval Notes</label>
          <textarea
            className="input min-h-[70px]"
            placeholder="Optional notes..."
            value={notes}
            onChange={e => setNotes(e.target.value)}
          />
        </div>
        <div className="flex gap-3 border-t border-slate-100 pt-3">
          <button onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button
            onClick={() => approveMutation.mutate('REJECTED')}
            disabled={approveMutation.isPending}
            className="flex-1 btn-secondary text-red-600 border-red-200 hover:bg-red-50"
          >
            <XCircle size={14} /> Reject
          </button>
          <button
            onClick={() => approveMutation.mutate('APPROVED')}
            disabled={approveMutation.isPending}
            className="flex-1 btn-primary bg-green-600 hover:bg-green-700"
          >
            <CheckCircle size={14} /> Approve
          </button>
        </div>
      </div>
    </Modal>
  )
}

export default function LeaveApplicationPage() {
  const qc = useQueryClient()
  const { company } = useAuthStoreV2()
  const role = company?.role
  const isManager = role === 'OWNER' || role === 'MANAGER'

  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editEntry, setEditEntry] = useState<LeaveApplication | null>(null)
  const [reviewEntry, setReviewEntry] = useState<LeaveApplication | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['leave-applications', page, statusFilter],
    queryFn: () => leaveApplicationApi.list({ page, page_size: 20, status: statusFilter || undefined }),
    placeholderData: prev => prev,
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => leaveApplicationApi.delete(id),
    onSuccess: () => { toast.success('Deleted.'); qc.invalidateQueries({ queryKey: ['leave-applications'] }) },
    onError: (err: any) => toast.error(err?.response?.data?.detail || 'Failed to delete.'),
  })

  const items = data?.items || []
  const total = data?.total || 0
  const totalPages = data?.total_pages || 1

  const diffDays = (from: string, to: string) => {
    const d = Math.round((new Date(to).getTime() - new Date(from).getTime()) / 86400000) + 1
    return d > 0 ? d : 1
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Leave Applications</h1>
          <p className="text-sm text-slate-500 mt-0.5">{total} record{total !== 1 ? 's' : ''}</p>
        </div>
        <button onClick={() => { setEditEntry(null); setShowForm(true) }} className="btn-primary">
          <Plus size={15} /> Apply for Leave
        </button>
      </div>

      {/* Filter */}
      <div className="card p-4">
        <div className="flex items-center gap-3">
          <label className="text-sm font-medium text-slate-600 shrink-0">Status</label>
          <select
            className="input w-40"
            value={statusFilter}
            onChange={e => { setStatusFilter(e.target.value); setPage(1) }}
          >
            <option value="">All</option>
            {LEAVE_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="table-th">#</th>
                {isManager && <th className="table-th">Employee</th>}
                <th className="table-th">Type</th>
                <th className="table-th">Leave Date</th>
                <th className="table-th">From → To</th>
                <th className="table-th">Days</th>
                <th className="table-th">Approver</th>
                <th className="table-th">Status</th>
                <th className="table-th">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr><td colSpan={isManager ? 9 : 8} className="py-16 text-center">
                  <div className="animate-spin w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full mx-auto" />
                </td></tr>
              ) : items.length === 0 ? (
                <tr><td colSpan={isManager ? 9 : 8} className="py-16 text-center text-slate-400 text-sm">
                  No leave applications found.
                </td></tr>
              ) : items.map((item, idx) => (
                <tr key={item.leave_application_id} className="hover:bg-slate-50 transition-colors">
                  <td className="table-td text-slate-400 text-xs">{(page - 1) * 20 + idx + 1}</td>
                  {isManager && (
                    <td className="table-td font-medium text-slate-900 text-sm">{item.employee_name || '—'}</td>
                  )}
                  <td className="table-td text-slate-700">{item.leave_type}</td>
                  <td className="table-td text-slate-500 text-sm">{item.leave_date}</td>
                  <td className="table-td text-sm">
                    <span className="text-slate-700">{item.from_date}</span>
                    <span className="text-slate-400 mx-1">→</span>
                    <span className="text-slate-700">{item.to_date}</span>
                  </td>
                  <td className="table-td text-center">
                    <span className="text-xs font-semibold text-slate-700">{diffDays(item.from_date, item.to_date)}</span>
                  </td>
                  <td className="table-td text-slate-500 text-sm">{item.approver_name || '—'}</td>
                  <td className="table-td">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${STATUS_COLORS[item.status] || 'bg-slate-100 text-slate-600'}`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="table-td">
                    <div className="flex items-center gap-1.5">
                      {isManager && item.status === 'PENDING' && (
                        <button
                          onClick={() => setReviewEntry(item)}
                          className="p-1.5 rounded-lg text-slate-500 hover:bg-green-50 hover:text-green-600 transition-colors"
                          title="Review"
                        >
                          <CheckCircle size={14} />
                        </button>
                      )}
                      {item.status === 'PENDING' && (
                        <button
                          onClick={() => { setEditEntry(item); setShowForm(true) }}
                          className="p-1.5 rounded-lg text-slate-500 hover:bg-blue-50 hover:text-blue-600 transition-colors"
                          title="Edit"
                        >
                          <Pencil size={14} />
                        </button>
                      )}
                      <button
                        onClick={() => { if (confirm('Delete this application?')) deleteMutation.mutate(item.leave_application_id) }}
                        className="p-1.5 rounded-lg text-slate-500 hover:bg-red-50 hover:text-red-600 transition-colors"
                        title="Delete"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="border-t border-slate-100 px-4 py-3 flex items-center justify-between">
            <p className="text-sm text-slate-500">
              Showing {(page - 1) * 20 + 1}–{Math.min(page * 20, total)} of {total}
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

      <LeaveAppFormModal
        open={showForm}
        onClose={() => { setShowForm(false); setEditEntry(null) }}
        entry={editEntry}
      />

      {reviewEntry && (
        <ApproveModal entry={reviewEntry} onClose={() => setReviewEntry(null)} />
      )}
    </div>
  )
}
