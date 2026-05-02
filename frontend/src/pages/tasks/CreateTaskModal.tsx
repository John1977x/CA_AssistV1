import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Loader2, Search, ChevronDown } from 'lucide-react'
import toast from 'react-hot-toast'
import { tasksApi } from '@/api/tasks'
import { customersApi } from '@/api/customers'
import { usersApi } from '@/api/users'
import { Modal, FormField } from '@/components/ui'
import { TASK_TYPE_LABELS, TASK_TYPE_GROUPS } from '@/types/task'
import clsx from 'clsx'

const schema = z.object({
  customer_id:         z.number({ required_error: 'Select a client' }),
  task_type_code:      z.string().min(1, 'Select task type'),
  task_title:          z.string().min(2, 'Title required'),
  due_date:            z.string().min(1, 'Due date required'),
  internal_due_date:   z.string().optional(),
  financial_year:      z.string().optional(),
  return_period:       z.string().optional(),
  priority:            z.string().default('MEDIUM'),
  assigned_to_user_id: z.number().optional(),
  assigned_to_type:    z.enum(['employee', 'customer']).optional(),
  description:         z.string().optional(),
  estimated_hours:     z.number().optional(),
})

type FormData = z.infer<typeof schema>

const PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
const PRIORITY_COLORS: Record<string, string> = {
  LOW: 'text-green-600 bg-green-50 border-green-200',
  MEDIUM: 'text-yellow-700 bg-yellow-50 border-yellow-200',
  HIGH: 'text-orange-600 bg-orange-50 border-orange-200',
  CRITICAL: 'text-red-600 bg-red-50 border-red-200',
}

// Financial years
const currentYear = new Date().getFullYear()
const FY_OPTIONS = Array.from({ length: 5 }, (_, i) => {
  const y = currentYear - i
  return `${y}-${String(y + 1).slice(2)}`
})

interface Props {
  open: boolean
  onClose: () => void
  preCustomerId?: number
}

export default function CreateTaskModal({ open, onClose, preCustomerId }: Props) {
  const qc = useQueryClient()
  const [customerSearch, setCustomerSearch] = useState('')
  const [typeGroup, setTypeGroup] = useState('')

  const { register, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { priority: 'MEDIUM', customer_id: preCustomerId },
  })

  const taskType = watch('task_type_code')
  const priority = watch('priority')
  const customerId = watch('customer_id')

  // Customers search
  const { data: customersData } = useQuery({
    queryKey: ['customers-search', customerSearch],
    queryFn: () => customersApi.list({ search: customerSearch, page_size: 10 }),
    enabled: !preCustomerId,
  })

  // Users
  const { data: usersData } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.list({ page_size: 50 }),
  })

  const users = usersData?.items || []

  // Auto-generate title when type changes
  const handleTypeChange = (code: string) => {
    setValue('task_type_code', code)
    const label = TASK_TYPE_LABELS[code] || code
    const fy = watch('financial_year')
    const period = watch('return_period')
    setValue('task_title', `${label}${period ? ` - ${period}` : fy ? ` - ${fy}` : ''}`)
  }

  const handleFYChange = (fy: string) => {
    setValue('financial_year', fy)
    const label = TASK_TYPE_LABELS[taskType] || taskType
    setValue('task_title', `${label}${fy ? ` - ${fy}` : ''}`)
  }

  const mutation = useMutation({
    mutationFn: (data: FormData) => tasksApi.create(data as any),
    onSuccess: () => {
      toast.success('Task created with checklist!')
      qc.invalidateQueries({ queryKey: ['tasks'] })
      qc.invalidateQueries({ queryKey: ['task-stats'] })
      reset({ priority: 'MEDIUM' })
      onClose()
    },
  })

  return (
    <Modal open={open} onClose={onClose} title="Create New Task" subtitle="A checklist will be auto-generated" size="lg">
      <form onSubmit={handleSubmit(d => mutation.mutate(d))} className="p-6 space-y-5">

        {/* Client selection */}
        {!preCustomerId && (
          <FormField label="Client" required error={errors.customer_id?.message}>
            <div className="relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                value={customerSearch}
                onChange={e => setCustomerSearch(e.target.value)}
                placeholder="Search client by name, PAN..."
                className="input pl-9"
              />
            </div>
            {customerSearch && customersData?.items && (
              <div className="mt-1 border border-slate-200 rounded-xl bg-white shadow-lg max-h-48 overflow-y-auto z-10">
                {customersData.items.map(c => (
                  <button
                    key={c.customer_id}
                    type="button"
                    onClick={() => {
                      setValue('customer_id', c.customer_id)
                      setCustomerSearch(c.display_name)
                    }}
                    className={clsx(
                      'w-full text-left px-4 py-2.5 hover:bg-slate-50 transition-colors text-sm',
                      customerId === c.customer_id && 'bg-brand-50 text-brand-800'
                    )}
                  >
                    <span className="font-medium">{c.display_name}</span>
                    <span className="text-slate-400 text-xs ml-2">{c.pan || c.phone}</span>
                  </button>
                ))}
              </div>
            )}
          </FormField>
        )}

        {/* Task type */}
        <FormField label="Task Type" required error={errors.task_type_code?.message}>
          <div className="space-y-2">
            <div className="flex flex-wrap gap-1.5 mb-2">
              {['', ...Object.keys(TASK_TYPE_GROUPS)].map(g => (
                <button
                  key={g}
                  type="button"
                  onClick={() => setTypeGroup(g)}
                  className={clsx(
                    'text-xs px-3 py-1 rounded-full border transition-all',
                    typeGroup === g
                      ? 'bg-brand-800 text-white border-brand-800'
                      : 'border-slate-200 text-slate-600 hover:border-slate-400'
                  )}
                >
                  {g || 'All'}
                </button>
              ))}
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 max-h-40 overflow-y-auto">
              {Object.entries(TASK_TYPE_GROUPS)
                .filter(([group]) => !typeGroup || group === typeGroup)
                .flatMap(([, codes]) => codes)
                .map(code => (
                  <button
                    key={code}
                    type="button"
                    onClick={() => handleTypeChange(code)}
                    className={clsx(
                      'text-xs px-2.5 py-2 rounded-lg border text-left transition-all',
                      taskType === code
                        ? 'bg-brand-800 text-white border-brand-800'
                        : 'border-slate-200 text-slate-700 hover:border-brand-400 hover:bg-brand-50'
                    )}
                  >
                    {TASK_TYPE_LABELS[code]}
                  </button>
                ))
              }
            </div>
          </div>
        </FormField>

        {/* Title */}
        <FormField label="Task Title" required error={errors.task_title?.message}>
          <input {...register('task_title')} className={`input ${errors.task_title ? 'input-error' : ''}`}
            placeholder="Auto-generated from type, or customise" />
        </FormField>

        {/* FY + Period + Due Date */}
        <div className="grid grid-cols-3 gap-3">
          <FormField label="Financial Year">
            <select {...register('financial_year')} onChange={e => handleFYChange(e.target.value)} className="input">
              <option value="">Select FY</option>
              {FY_OPTIONS.map(fy => <option key={fy} value={fy}>{fy}</option>)}
            </select>
          </FormField>
          <FormField label="Return Period">
            <input {...register('return_period')} className="input" placeholder="e.g. Apr-2024" />
          </FormField>
          <FormField label="Due Date" required error={errors.due_date?.message}>
            <input {...register('due_date')} type="date" className={`input ${errors.due_date ? 'input-error' : ''}`} />
          </FormField>
        </div>

        {/* Priority */}
        <FormField label="Priority">
          <div className="flex gap-2">
            {PRIORITIES.map(p => (
              <button
                key={p}
                type="button"
                onClick={() => setValue('priority', p)}
                className={clsx(
                  'flex-1 text-xs font-semibold py-2 rounded-lg border transition-all',
                  priority === p
                    ? PRIORITY_COLORS[p]
                    : 'border-slate-200 text-slate-500 hover:border-slate-300'
                )}
              >
                {p}
              </button>
            ))}
          </div>
        </FormField>

        {/* Assign */}
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Assign To">
            <select {...register('assigned_to_user_id', { valueAsNumber: true })} className="input">
              <option value="">Unassigned</option>
              <optgroup label="Employees">
                {users.map(u => (
                  <option key={`emp-${u.user_id}`} value={u.user_id}>
                    {u.display_name || u.email}
                  </option>
                ))}
              </optgroup>
            </select>
          </FormField>
          <FormField label="Estimated Hours">
            <input {...register('estimated_hours', { valueAsNumber: true })} type="number" step="0.5"
              className="input" placeholder="e.g. 2.5" />
          </FormField>
        </div>

        {/* Description */}
        <FormField label="Description / Notes">
          <textarea {...register('description')} rows={2} className="input resize-none"
            placeholder="Any additional instructions..." />
        </FormField>

        <div className="bg-blue-50 border border-blue-100 rounded-xl p-3 text-xs text-blue-700">
          📋 A default checklist will be auto-created based on the task type. You can customise steps after creation.
        </div>

        <div className="flex gap-3 pt-2 border-t border-slate-100">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button type="submit" disabled={mutation.isPending} className="btn-primary flex-1">
            {mutation.isPending ? <><Loader2 size={14} className="animate-spin" /> Creating...</> : 'Create Task'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
