import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Plus, Search, ClipboardList, AlertCircle, Clock,
  CheckCircle, ChevronLeft, ChevronRight, RefreshCw,
  LayoutList, Columns, Calendar, Filter,
} from 'lucide-react'
import { tasksApi } from '@/api/tasks'
import { StatCard, StatusBadge, EmptyState, Tabs } from '@/components/ui'
import CreateTaskModal from './CreateTaskModal'
import TaskDrawer from './TaskDrawer'
import { TASK_TYPE_LABELS } from '@/types/task'
import type { Task } from '@/types/task'
import { format, parseISO, differenceInDays, isToday, isPast } from 'date-fns'
import clsx from 'clsx'

const PRIORITY_DOT: Record<string, string> = {
  LOW:      'bg-green-500',
  MEDIUM:   'bg-yellow-500',
  HIGH:     'bg-orange-500',
  CRITICAL: 'bg-red-500 animate-pulse',
}

const STATUS_COLS = [
  { key: 'PENDING',      label: 'Pending',        color: 'border-slate-400' },
  { key: 'IN_PROGRESS',  label: 'In Progress',     color: 'border-blue-500' },
  { key: 'PENDING_DOCS', label: 'Pending Docs',    color: 'border-yellow-500' },
  { key: 'UNDER_REVIEW', label: 'Under Review',    color: 'border-purple-500' },
  { key: 'COMPLETED',    label: 'Completed',       color: 'border-green-500' },
  { key: 'FILED',        label: 'Filed',           color: 'border-teal-500' },
]

function DueDateBadge({ dueDate, status }: { dueDate: string; status: string }) {
  const days = differenceInDays(parseISO(dueDate), new Date())
  const done = ['COMPLETED', 'FILED', 'CANCELLED'].includes(status)
  if (done) return <span className="text-xs text-slate-400">{format(parseISO(dueDate), 'd MMM')}</span>
  if (days < 0) return <span className="text-xs text-red-600 font-semibold">{Math.abs(days)}d overdue</span>
  if (days === 0) return <span className="text-xs text-orange-600 font-semibold">Due today</span>
  if (days <= 3) return <span className="text-xs text-orange-500">{days}d left</span>
  return <span className="text-xs text-slate-500">{format(parseISO(dueDate), 'd MMM')}</span>
}

// ── Kanban Card ───────────────────────────────────────────────────────────────
function KanbanCard({ task, onClick }: { task: Task; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl border border-slate-200 p-3.5 cursor-pointer hover:shadow-md hover:border-brand-300 transition-all group"
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="text-xs font-semibold text-brand-700 bg-brand-50 px-2 py-0.5 rounded-full">
          {TASK_TYPE_LABELS[task.task_type_code] || task.task_type_code}
        </span>
        <div className={`w-2 h-2 rounded-full flex-shrink-0 mt-1 ${PRIORITY_DOT[task.priority]}`} />
      </div>
      <p className="text-sm font-medium text-slate-900 mb-1.5 line-clamp-2 group-hover:text-brand-800">
        {task.task_title}
      </p>
      {task.customer && (
        <p className="text-xs text-slate-500 mb-2 truncate">{task.customer.display_name}</p>
      )}
      <div className="flex items-center justify-between">
        <DueDateBadge dueDate={task.due_date} status={task.status} />
        <div className="flex items-center gap-1">
          <div className="w-12 h-1 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-brand-500 rounded-full"
              style={{ width: `${task.completion_percentage}%` }}
            />
          </div>
          <span className="text-xs text-slate-400">{task.completion_percentage}%</span>
        </div>
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function TasksPage() {
  const qc = useQueryClient()
  const [view, setView] = useState<'list' | 'board'>('list')
  const [showCreate, setShowCreate] = useState(false)
  const [viewTaskId, setViewTaskId] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [priorityFilter, setPriorityFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [overdueOnly, setOverdueOnly] = useState(false)
  const [page, setPage] = useState(1)

  const { data: stats } = useQuery({
    queryKey: ['task-stats'],
    queryFn: tasksApi.stats,
  })

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['tasks', page, search, statusFilter, priorityFilter, typeFilter, overdueOnly, view],
    queryFn: () => tasksApi.list({
      page,
      page_size: view === 'board' ? 100 : 20,
      search: search || undefined,
      status: statusFilter || undefined,
      priority: priorityFilter || undefined,
      task_type_code: typeFilter || undefined,
      overdue_only: overdueOnly || undefined,
    }),
    placeholderData: prev => prev,
  })

  const tasks = data?.items || []
  const total = data?.total || 0
  const totalPages = data?.total_pages || 1

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Tasks & Workflow</h1>
          <p className="text-sm text-slate-500 mt-0.5">{total} task{total !== 1 ? 's' : ''} total</p>
        </div>
        <div className="flex items-center gap-2">
          {/* View toggle */}
          <div className="flex items-center bg-slate-100 rounded-lg p-1">
            <button
              onClick={() => setView('list')}
              className={clsx('p-1.5 rounded-md transition-all', view === 'list' ? 'bg-white shadow-sm' : 'text-slate-500')}
            >
              <LayoutList size={15} />
            </button>
            <button
              onClick={() => setView('board')}
              className={clsx('p-1.5 rounded-md transition-all', view === 'board' ? 'bg-white shadow-sm' : 'text-slate-500')}
            >
              <Columns size={15} />
            </button>
          </div>
          <button onClick={() => setShowCreate(true)} className="btn-primary">
            <Plus size={15} /> New Task
          </button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total Tasks"   value={stats.total}         icon={<ClipboardList size={18} />} color="text-blue-600"   bg="bg-blue-50" />
          <StatCard label="In Progress"   value={stats.in_progress}   icon={<Clock size={18} />}         color="text-yellow-600" bg="bg-yellow-50" />
          <StatCard label="Overdue"       value={stats.overdue}       icon={<AlertCircle size={18} />}   color="text-red-600"    bg="bg-red-50" />
          <StatCard label="Due This Week" value={stats.due_this_week} icon={<Calendar size={18} />}      color="text-orange-600" bg="bg-orange-50" />
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
              placeholder="Search tasks..."
              className="input pl-9"
            />
          </div>
          <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1) }} className="input w-36">
            <option value="">All Status</option>
            {['PENDING', 'IN_PROGRESS', 'PENDING_DOCS', 'UNDER_REVIEW', 'COMPLETED', 'FILED', 'CANCELLED'].map(s => (
              <option key={s} value={s}>{s.replace('_', ' ')}</option>
            ))}
          </select>
          <select value={priorityFilter} onChange={e => { setPriorityFilter(e.target.value); setPage(1) }} className="input w-32">
            <option value="">All Priority</option>
            {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map(p => <option key={p} value={p}>{p}</option>)}
          </select>
          <select value={typeFilter} onChange={e => { setTypeFilter(e.target.value); setPage(1) }} className="input w-40">
            <option value="">All Types</option>
            {Object.entries(TASK_TYPE_LABELS).map(([code, label]) => (
              <option key={code} value={code}>{label}</option>
            ))}
          </select>
          <button
            onClick={() => { setOverdueOnly(!overdueOnly); setPage(1) }}
            className={clsx('btn-sm flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium border transition-all',
              overdueOnly ? 'bg-red-600 text-white border-red-600' : 'bg-white text-slate-600 border-slate-200 hover:border-red-400'
            )}
          >
            <AlertCircle size={13} /> Overdue
          </button>
          <button onClick={() => qc.invalidateQueries({ queryKey: ['tasks'] })}
            className={clsx('btn-ghost', isFetching && 'opacity-50')}>
            <RefreshCw size={15} className={isFetching ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* List View */}
      {view === 'list' && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="table-th">Task</th>
                  <th className="table-th">Client</th>
                  <th className="table-th">Type</th>
                  <th className="table-th">Priority</th>
                  <th className="table-th">Status</th>
                  <th className="table-th">Progress</th>
                  <th className="table-th">Due Date</th>
                  <th className="table-th">Assigned</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {isLoading ? (
                  <tr><td colSpan={8} className="py-16 text-center">
                    <div className="animate-spin w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full mx-auto" />
                  </td></tr>
                ) : tasks.length === 0 ? (
                  <tr><td colSpan={8}>
                    <EmptyState
                      icon={<ClipboardList size={24} />}
                      title="No tasks found"
                      description="Create your first task to start tracking compliance work"
                      action={
                        <button onClick={() => setShowCreate(true)} className="btn-primary btn-sm">
                          <Plus size={13} /> New Task
                        </button>
                      }
                    />
                  </td></tr>
                ) : (
                  tasks.map(t => (
                    <tr
                      key={t.task_id}
                      onClick={() => setViewTaskId(t.task_id)}
                      className="hover:bg-blue-50/40 cursor-pointer transition-colors"
                    >
                      <td className="table-td max-w-[200px]">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full flex-shrink-0 ${PRIORITY_DOT[t.priority]}`} />
                          <span className="font-medium text-slate-900 text-sm truncate">{t.task_title}</span>
                        </div>
                        {t.return_period && <p className="text-xs text-slate-400 ml-4">{t.return_period}</p>}
                      </td>
                      <td className="table-td text-sm text-slate-600">
                        {t.customer?.display_name || '—'}
                      </td>
                      <td className="table-td">
                        <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full font-medium">
                          {TASK_TYPE_LABELS[t.task_type_code] || t.task_type_code}
                        </span>
                      </td>
                      <td className="table-td">
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                          t.priority === 'CRITICAL' ? 'bg-red-50 text-red-700' :
                          t.priority === 'HIGH'     ? 'bg-orange-50 text-orange-700' :
                          t.priority === 'MEDIUM'   ? 'bg-yellow-50 text-yellow-700' :
                          'bg-green-50 text-green-700'
                        }`}>
                          {t.priority}
                        </span>
                      </td>
                      <td className="table-td">
                        <StatusBadge status={t.status} />
                      </td>
                      <td className="table-td">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div className="h-full bg-brand-500 rounded-full" style={{ width: `${t.completion_percentage}%` }} />
                          </div>
                          <span className="text-xs text-slate-500">{t.completion_percentage}%</span>
                        </div>
                      </td>
                      <td className="table-td">
                        <DueDateBadge dueDate={t.due_date} status={t.status} />
                      </td>
                      <td className="table-td text-xs text-slate-500 truncate max-w-[100px]">
                        {t.assigned_to?.display_name || '—'}
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
      )}

      {/* Board View */}
      {view === 'board' && (
        <div className="flex gap-4 overflow-x-auto pb-4">
          {STATUS_COLS.map(col => {
            const colTasks = tasks.filter(t => t.status === col.key)
            return (
              <div key={col.key} className="flex-shrink-0 w-64">
                <div className={`flex items-center gap-2 mb-3 pb-2 border-b-2 ${col.color}`}>
                  <span className="text-sm font-semibold text-slate-700">{col.label}</span>
                  <span className="text-xs bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded-full ml-auto">
                    {colTasks.length}
                  </span>
                </div>
                <div className="space-y-2">
                  {colTasks.length === 0 ? (
                    <div className="text-center py-8 text-slate-300 text-xs">No tasks</div>
                  ) : (
                    colTasks.map(t => (
                      <KanbanCard key={t.task_id} task={t} onClick={() => setViewTaskId(t.task_id)} />
                    ))
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      <CreateTaskModal open={showCreate} onClose={() => setShowCreate(false)} />
      <TaskDrawer taskId={viewTaskId} onClose={() => setViewTaskId(null)} />
    </div>
  )
}
