import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  CheckCircle2, Circle, Clock, AlertTriangle, XCircle,
  User, Calendar, FileText, Plus, Loader2, ChevronDown,
  Tag, IndianRupee, RefreshCw,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { tasksApi } from '@/api/tasks'
import { Drawer, StatusBadge, Tabs } from '@/components/ui'
import { TASK_TYPE_LABELS } from '@/types/task'
import type { Task, TaskStep } from '@/types/task'
import clsx from 'clsx'
import { differenceInDays, parseISO, format } from 'date-fns'

const STEP_ICON: Record<string, React.ReactNode> = {
  COMPLETED:   <CheckCircle2 size={16} className="text-green-600" />,
  IN_PROGRESS: <Clock size={16} className="text-blue-500" />,
  BLOCKED:     <AlertTriangle size={16} className="text-red-500" />,
  SKIPPED:     <XCircle size={16} className="text-slate-300" />,
  PENDING:     <Circle size={16} className="text-slate-300" />,
}

const TASK_STATUSES = ['PENDING', 'IN_PROGRESS', 'PENDING_DOCS', 'UNDER_REVIEW', 'COMPLETED', 'FILED', 'CANCELLED']
const BILLING_STATUSES = ['UNBILLED', 'INVOICED', 'PAID']

const PRIORITY_BADGE: Record<string, string> = {
  LOW:      'bg-green-50 text-green-700',
  MEDIUM:   'bg-yellow-50 text-yellow-700',
  HIGH:     'bg-orange-50 text-orange-700',
  CRITICAL: 'bg-red-50 text-red-700 font-bold',
}

function ProgressRing({ pct }: { pct: number }) {
  const r = 20, circ = 2 * Math.PI * r
  const dash = (pct / 100) * circ
  return (
    <svg width="52" height="52" className="-rotate-90">
      <circle cx="26" cy="26" r={r} fill="none" stroke="#e2e8f0" strokeWidth="4" />
      <circle cx="26" cy="26" r={r} fill="none" stroke="#1e40af" strokeWidth="4"
        strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
        style={{ transition: 'stroke-dasharray 0.4s ease' }} />
      <text x="26" y="26" textAnchor="middle" dominantBaseline="middle"
        className="rotate-90" fill="#1e40af" fontSize="10" fontWeight="700"
        style={{ transform: 'rotate(90deg)', transformOrigin: '26px 26px' }}>
        {pct}%
      </text>
    </svg>
  )
}

function StepRow({ step, taskId, onToggle }: {
  step: TaskStep; taskId: number; onToggle: (stepId: number, status: string) => void
}) {
  const [expanded, setExpanded] = useState(false)
  const isDone = step.status === 'COMPLETED'
  const isSkipped = step.status === 'SKIPPED'

  return (
    <div className={clsx(
      'border rounded-xl transition-all',
      isDone ? 'border-green-200 bg-green-50/40' :
      isSkipped ? 'border-slate-100 bg-slate-50 opacity-60' :
      step.is_client_action ? 'border-blue-200 bg-blue-50/30' :
      'border-slate-200 bg-white'
    )}>
      <div className="flex items-start gap-3 p-3">
        <button
          onClick={() => onToggle(step.task_detail_id, isDone ? 'PENDING' : 'COMPLETED')}
          className="mt-0.5 flex-shrink-0 hover:scale-110 transition-transform"
          disabled={isSkipped}
        >
          {STEP_ICON[step.status]}
        </button>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={clsx(
              'text-sm font-medium',
              isDone ? 'line-through text-slate-400' : 'text-slate-800'
            )}>
              {step.step_title}
            </span>
            {step.is_client_action && (
              <span className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full">
                Client action
              </span>
            )}
            {!step.is_required && (
              <span className="text-xs text-slate-400">(optional)</span>
            )}
          </div>

          {step.step_description && !isDone && (
            <p className="text-xs text-slate-500 mt-0.5">{step.step_description}</p>
          )}

          <div className="flex items-center gap-3 mt-1">
            {step.due_date && (
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Calendar size={10} />
                {format(parseISO(step.due_date), 'd MMM')}
              </span>
            )}
            {step.completed_at && (
              <span className="text-xs text-green-600">
                ✓ {format(parseISO(step.completed_at), 'd MMM HH:mm')}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1">
          <select
            value={step.status}
            onChange={e => onToggle(step.task_detail_id, e.target.value)}
            onClick={e => e.stopPropagation()}
            className="text-xs border border-slate-200 rounded-lg px-1.5 py-1 bg-white focus:outline-none"
          >
            {['PENDING', 'IN_PROGRESS', 'COMPLETED', 'BLOCKED', 'SKIPPED'].map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}

interface Props {
  taskId:  number | null
  onClose: () => void
}

export default function TaskDrawer({ taskId, onClose }: Props) {
  const qc = useQueryClient()
  const [tab, setTab] = useState('checklist')
  const [newNote, setNewNote] = useState('')

  const { data: task, isLoading } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => tasksApi.get(taskId!),
    enabled: !!taskId,
  })

  const updateTask = useMutation({
    mutationFn: (data: Partial<Task> & any) => tasksApi.update(taskId!, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['task', taskId] })
      qc.invalidateQueries({ queryKey: ['tasks'] })
      qc.invalidateQueries({ queryKey: ['task-stats'] })
    },
  })

  const updateStep = useMutation({
    mutationFn: ({ stepId, status }: { stepId: number; status: string }) =>
      tasksApi.updateStep(taskId!, stepId, { status }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['task', taskId] })
      qc.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  if (!taskId) return null

  const daysUntilDue = task ? differenceInDays(parseISO(task.due_date), new Date()) : 0
  const isOverdue = task && daysUntilDue < 0 && !['COMPLETED', 'FILED', 'CANCELLED'].includes(task.status)

  return (
    <Drawer
      open={!!taskId}
      onClose={onClose}
      title={task?.task_title || 'Loading...'}
      subtitle={task ? `${TASK_TYPE_LABELS[task.task_type_code] || task.task_type_code} · ${task.financial_year || ''}` : ''}
      width="lg"
    >
      {isLoading ? (
        <div className="flex items-center justify-center h-48">
          <Loader2 className="animate-spin text-brand-600" size={28} />
        </div>
      ) : task ? (
        <div>
          {/* Summary bar */}
          <div className="flex items-center gap-4 px-6 py-4 bg-slate-50 border-b border-slate-100">
            <ProgressRing pct={task.completion_percentage} />
            <div className="flex-1 space-y-2">
              <div className="flex flex-wrap gap-2">
                <StatusBadge status={task.status} />
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${PRIORITY_BADGE[task.priority]}`}>
                  {task.priority}
                </span>
                <StatusBadge status={task.billing_status} />
              </div>
              <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                <span className={clsx('flex items-center gap-1 font-medium',
                  isOverdue ? 'text-red-600' : daysUntilDue <= 3 ? 'text-orange-600' : 'text-slate-600'
                )}>
                  <Calendar size={11} />
                  Due: {format(parseISO(task.due_date), 'd MMM yyyy')}
                  {isOverdue && ' (Overdue)'}
                  {!isOverdue && daysUntilDue <= 7 && ` (${daysUntilDue}d)`}
                </span>
                {task.customer && (
                  <span className="flex items-center gap-1">
                    <User size={11} />
                    {task.customer.display_name}
                  </span>
                )}
                {task.assigned_to && (
                  <span className="flex items-center gap-1">
                    <User size={11} />
                    {task.assigned_to.display_name || task.assigned_to.email}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Quick actions */}
          <div className="flex gap-2 px-6 py-3 border-b border-slate-100 overflow-x-auto">
            <select
              value={task.status}
              onChange={e => updateTask.mutate({ status: e.target.value })}
              className="text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 bg-white focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              {TASK_STATUSES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
            </select>
            <select
              value={task.billing_status}
              onChange={e => updateTask.mutate({ billing_status: e.target.value })}
              className="text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 bg-white focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              {BILLING_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            {task.status === 'FILED' && !task.acknowledgement_number && (
              <input
                type="text"
                placeholder="Acknowledgement no."
                className="text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 bg-white focus:outline-none focus:ring-1 focus:ring-brand-500 w-44"
                onBlur={e => e.target.value && updateTask.mutate({ acknowledgement_number: e.target.value })}
              />
            )}
            {task.acknowledgement_number && (
              <span className="text-xs bg-green-50 text-green-700 border border-green-200 rounded-lg px-2.5 py-1.5">
                Ack: {task.acknowledgement_number}
              </span>
            )}
          </div>

          {/* Tabs */}
          <div className="px-6 pt-4">
            <Tabs
              tabs={[
                { key: 'checklist', label: 'Checklist', count: task.details?.filter(s => s.status !== 'SKIPPED').length },
                { key: 'details',   label: 'Details' },
                { key: 'billing',   label: 'Billing' },
              ]}
              active={tab}
              onChange={setTab}
            />
          </div>

          <div className="px-6 py-4">
            {/* Checklist */}
            {tab === 'checklist' && (
              <div className="space-y-2">
                {task.details && task.details.length > 0 ? (
                  <>
                    {/* Progress bar */}
                    <div className="mb-4">
                      <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                        <span>{task.details.filter(s => s.status === 'COMPLETED').length} of {task.details.filter(s => s.status !== 'SKIPPED').length} steps done</span>
                        <span>{task.completion_percentage}%</span>
                      </div>
                      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-brand-600 rounded-full transition-all duration-500"
                          style={{ width: `${task.completion_percentage}%` }}
                        />
                      </div>
                    </div>

                    {task.details.map(step => (
                      <StepRow
                        key={step.task_detail_id}
                        step={step}
                        taskId={task.task_id}
                        onToggle={(stepId, status) => updateStep.mutate({ stepId, status })}
                      />
                    ))}
                  </>
                ) : (
                  <p className="text-slate-400 text-sm text-center py-8">No checklist steps for this task.</p>
                )}
              </div>
            )}

            {/* Details */}
            {tab === 'details' && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {[
                    { label: 'Task Type', value: TASK_TYPE_LABELS[task.task_type_code] },
                    { label: 'Financial Year', value: task.financial_year },
                    { label: 'Return Period', value: task.return_period },
                    { label: 'Internal Due', value: task.internal_due_date ? format(parseISO(task.internal_due_date), 'd MMM yyyy') : null },
                    { label: 'Est. Hours', value: task.estimated_hours ? `${task.estimated_hours}h` : null },
                    { label: 'Actual Hours', value: task.actual_hours ? `${task.actual_hours}h` : null },
                    { label: 'Filed At', value: task.filed_at ? format(parseISO(task.filed_at), 'd MMM yyyy HH:mm') : null },
                    { label: 'Reviewer', value: task.reviewer?.display_name || task.reviewer?.email },
                  ].filter(r => r.value).map(row => (
                    <div key={row.label} className="bg-slate-50 rounded-lg p-3">
                      <p className="text-xs text-slate-400 mb-0.5">{row.label}</p>
                      <p className="font-medium text-slate-800">{row.value}</p>
                    </div>
                  ))}
                </div>

                {task.description && (
                  <div>
                    <p className="text-xs text-slate-400 mb-1.5">Description</p>
                    <div className="bg-slate-50 rounded-xl p-4 text-sm text-slate-700 whitespace-pre-wrap">
                      {task.description}
                    </div>
                  </div>
                )}

                {task.tags?.length ? (
                  <div className="flex flex-wrap gap-1.5">
                    {task.tags.map(t => (
                      <span key={t} className="flex items-center gap-1 text-xs bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full">
                        <Tag size={10} />{t}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
            )}

            {/* Billing */}
            {tab === 'billing' && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="card p-4">
                    <p className="text-xs text-slate-400 mb-1">Billing Status</p>
                    <StatusBadge status={task.billing_status} />
                  </div>
                  <div className="card p-4">
                    <p className="text-xs text-slate-400 mb-1">Billed Amount</p>
                    <p className="text-lg font-bold text-slate-900 flex items-center gap-1">
                      <IndianRupee size={14} />
                      {task.billed_amount ? task.billed_amount.toLocaleString('en-IN') : '—'}
                    </p>
                  </div>
                  <div className="card p-4">
                    <p className="text-xs text-slate-400 mb-1">Estimated Hours</p>
                    <p className="text-lg font-bold text-slate-900">{task.estimated_hours || '—'}</p>
                  </div>
                  <div className="card p-4">
                    <p className="text-xs text-slate-400 mb-1">Actual Hours</p>
                    <p className="text-lg font-bold text-slate-900">{task.actual_hours || '—'}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="label">Log Actual Hours</label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      step="0.25"
                      defaultValue={task.actual_hours || ''}
                      className="input flex-1"
                      id="actual-hours-input"
                    />
                    <button
                      onClick={() => {
                        const val = parseFloat((document.getElementById('actual-hours-input') as HTMLInputElement).value)
                        if (!isNaN(val)) updateTask.mutate({ actual_hours: val })
                      }}
                      className="btn-primary"
                    >
                      Save
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="label">Billed Amount (₹)</label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      defaultValue={task.billed_amount || ''}
                      className="input flex-1"
                      id="billed-amount-input"
                    />
                    <button
                      onClick={() => {
                        const val = parseFloat((document.getElementById('billed-amount-input') as HTMLInputElement).value)
                        if (!isNaN(val)) updateTask.mutate({ billed_amount: val })
                      }}
                      className="btn-primary"
                    >
                      Save
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </Drawer>
  )
}
