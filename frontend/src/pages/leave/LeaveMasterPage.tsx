import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Plus, Pencil, Trash2, Loader2, ChevronLeft, ChevronRight } from 'lucide-react'
import toast from 'react-hot-toast'
import { leaveMasterApi, LEAVE_TYPES, CALCULATIONS } from '@/api/leave'
import type { LeaveMaster } from '@/api/leave'
import { Modal, FormField } from '@/components/ui'

const schema = z.object({
  leave_type:    z.string().min(1, 'Required'),
  entitled:      z.number({ invalid_type_error: 'Required' }).int().min(0, 'Min 0'),
  calendar_year: z.number({ invalid_type_error: 'Required' }).int().min(2000).max(2100),
  calculation:   z.string().min(1, 'Required'),
})
type FormData = z.infer<typeof schema>

const CURRENT_YEAR = new Date().getFullYear()
const YEAR_OPTIONS = Array.from({ length: 6 }, (_, i) => CURRENT_YEAR - 1 + i)

function LeaveFormModal({
  open, onClose, entry,
}: { open: boolean; onClose: () => void; entry: LeaveMaster | null }) {
  const qc = useQueryClient()
  const isEdit = !!entry

  const { register, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { leave_type: '', entitled: 0, calendar_year: CURRENT_YEAR, calculation: 'YEARLY' },
  })

  useEffect(() => {
    if (entry) {
      reset({
        leave_type:    entry.leave_type,
        entitled:      entry.entitled,
        calendar_year: entry.calendar_year,
        calculation:   entry.calculation,
      })
    } else {
      reset({ leave_type: '', entitled: 0, calendar_year: CURRENT_YEAR, calculation: 'YEARLY' })
    }
  }, [entry, open, reset])

  const mutation = useMutation({
    mutationFn: (data: FormData) =>
      isEdit
        ? leaveMasterApi.update(entry!.leave_master_id, data)
        : leaveMasterApi.create(data),
    onSuccess: () => {
      toast.success(isEdit ? 'Leave master updated.' : 'Leave master created.')
      qc.invalidateQueries({ queryKey: ['leave-masters'] })
      onClose()
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || 'Failed to save.')
    },
  })

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? 'Edit Leave Master' : 'Add Leave Master'}
      size="md"
    >
      <form onSubmit={handleSubmit(d => mutation.mutate(d))} className="p-6 space-y-4">
        <FormField label="Leave Type" required error={errors.leave_type?.message}>
          <select
            className="input"
            value={watch('leave_type')}
            onChange={e => setValue('leave_type', e.target.value)}
          >
            <option value="">Select type...</option>
            {LEAVE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </FormField>

        <div className="grid grid-cols-2 gap-4">
          <FormField label="Entitled Days" required error={errors.entitled?.message}>
            <input
              type="number"
              min={0}
              className={`input ${errors.entitled ? 'input-error' : ''}`}
              {...register('entitled', { valueAsNumber: true })}
            />
          </FormField>

          <FormField label="Calendar Year" required error={errors.calendar_year?.message}>
            <select
              className="input"
              value={watch('calendar_year')}
              onChange={e => setValue('calendar_year', Number(e.target.value))}
            >
              {YEAR_OPTIONS.map(y => <option key={y} value={y}>{y}</option>)}
            </select>
          </FormField>
        </div>

        <FormField label="Calculation" required error={errors.calculation?.message}>
          <select
            className="input"
            value={watch('calculation')}
            onChange={e => setValue('calculation', e.target.value)}
          >
            {CALCULATIONS.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </FormField>

        <div className="flex gap-3 pt-2 border-t border-slate-100">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button type="submit" disabled={mutation.isPending} className="btn-primary flex-1">
            {mutation.isPending
              ? <><Loader2 size={14} className="animate-spin" /> Saving...</>
              : isEdit ? 'Save Changes' : 'Add'
            }
          </button>
        </div>
      </form>
    </Modal>
  )
}

export default function LeaveMasterPage() {
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [yearFilter, setYearFilter] = useState<number | undefined>(undefined)
  const [showForm, setShowForm] = useState(false)
  const [editEntry, setEditEntry] = useState<LeaveMaster | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['leave-masters', page, yearFilter],
    queryFn: () => leaveMasterApi.list({ page, page_size: 20, calendar_year: yearFilter }),
    placeholderData: prev => prev,
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => leaveMasterApi.delete(id),
    onSuccess: () => {
      toast.success('Deleted.')
      qc.invalidateQueries({ queryKey: ['leave-masters'] })
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || 'Failed to delete.')
    },
  })

  const items = data?.items || []
  const total = data?.total || 0
  const totalPages = data?.total_pages || 1

  const openCreate = () => { setEditEntry(null); setShowForm(true) }
  const openEdit = (e: LeaveMaster) => { setEditEntry(e); setShowForm(true) }
  const handleDelete = (e: LeaveMaster) => {
    if (confirm(`Delete "${e.leave_type}" (${e.calendar_year})?`)) {
      deleteMutation.mutate(e.leave_master_id)
    }
  }

  const CALC_COLORS: Record<string, string> = {
    YEARLY:    'bg-blue-100 text-blue-700',
    MONTHLY:   'bg-green-100 text-green-700',
    QUARTERLY: 'bg-purple-100 text-purple-700',
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Leave Master</h1>
          <p className="text-sm text-slate-500 mt-0.5">{total} record{total !== 1 ? 's' : ''}</p>
        </div>
        <button onClick={openCreate} className="btn-primary">
          <Plus size={15} /> Add Leave Type
        </button>
      </div>

      {/* Filter */}
      <div className="card p-4">
        <div className="flex items-center gap-3">
          <label className="text-sm font-medium text-slate-600 shrink-0">Calendar Year</label>
          <select
            className="input w-36"
            value={yearFilter ?? ''}
            onChange={e => { setYearFilter(e.target.value ? Number(e.target.value) : undefined); setPage(1) }}
          >
            <option value="">All Years</option>
            {YEAR_OPTIONS.map(y => <option key={y} value={y}>{y}</option>)}
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
                <th className="table-th">Leave Type</th>
                <th className="table-th">Entitled Days</th>
                <th className="table-th">Calendar Year</th>
                <th className="table-th">Calculation</th>
                <th className="table-th">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr><td colSpan={6} className="py-16 text-center">
                  <div className="animate-spin w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full mx-auto" />
                </td></tr>
              ) : items.length === 0 ? (
                <tr><td colSpan={6} className="py-16 text-center text-slate-400 text-sm">
                  No leave master records found. Click "Add Leave Type" to get started.
                </td></tr>
              ) : items.map((item, idx) => (
                <tr key={item.leave_master_id} className="hover:bg-slate-50 transition-colors">
                  <td className="table-td text-slate-400 text-xs">{(page - 1) * 20 + idx + 1}</td>
                  <td className="table-td font-medium text-slate-900">{item.leave_type}</td>
                  <td className="table-td">
                    <span className="font-semibold text-slate-800">{item.entitled}</span>
                    <span className="text-slate-400 text-xs ml-1">days</span>
                  </td>
                  <td className="table-td text-slate-700">{item.calendar_year}</td>
                  <td className="table-td">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${CALC_COLORS[item.calculation] || 'bg-slate-100 text-slate-600'}`}>
                      {item.calculation}
                    </span>
                  </td>
                  <td className="table-td">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => openEdit(item)}
                        className="p-1.5 rounded-lg text-slate-500 hover:bg-blue-50 hover:text-blue-600 transition-colors"
                        title="Edit"
                      >
                        <Pencil size={14} />
                      </button>
                      <button
                        onClick={() => handleDelete(item)}
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

        {/* Pagination */}
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

      <LeaveFormModal
        open={showForm}
        onClose={() => { setShowForm(false); setEditEntry(null) }}
        entry={editEntry}
      />
    </div>
  )
}
