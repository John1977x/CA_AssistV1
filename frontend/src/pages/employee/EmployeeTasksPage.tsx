import { useEffect, useState } from 'react'
import { tasksApi } from '@/api/tasks'
import type { Task } from '@/types/task'
import { CheckCircle, Clock, AlertCircle, Search } from 'lucide-react'

export default function EmployeeTasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true)
        const response = await tasksApi.employeeTasks({ page: 1, page_size: 100 })
        setTasks(response.items || [])
      } catch (err) {
        console.error('Failed to fetch tasks:', err)
        setError('Failed to load tasks')
      } finally {
        setLoading(false)
      }
    }

    fetchTasks()
  }, [])

  const getStatusColor = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'COMPLETED':
      case 'FILED':
        return 'bg-green-100 text-green-800'
      case 'IN_PROGRESS':
        return 'bg-blue-100 text-blue-800'
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800'
      case 'CANCELLED':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'COMPLETED':
      case 'FILED':
        return <CheckCircle size={18} className="text-green-600" />
      case 'IN_PROGRESS':
        return <Clock size={18} className="text-blue-600" />
      case 'PENDING':
        return <AlertCircle size={18} className="text-yellow-600" />
      default:
        return null
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority?.toUpperCase()) {
      case 'HIGH':
        return 'bg-red-100 text-red-800'
      case 'MEDIUM':
        return 'bg-orange-100 text-orange-800'
      case 'LOW':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.task_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         task.task_type_code.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || task.status?.toUpperCase() === statusFilter.toUpperCase()
    return matchesSearch && matchesStatus
  })

  const stats = {
    total: tasks.length,
    completed: tasks.filter(t => ['COMPLETED', 'FILED'].includes(t.status?.toUpperCase() || '')).length,
    inProgress: tasks.filter(t => t.status?.toUpperCase() === 'IN_PROGRESS').length,
    pending: tasks.filter(t => t.status?.toUpperCase() === 'PENDING').length,
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">My Tasks</h1>
        <p className="text-slate-500 mt-2">View all tasks assigned to you</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-slate-500 text-sm">Total Tasks</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{stats.total}</p>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-slate-500 text-sm">Completed</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{stats.completed}</p>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-slate-500 text-sm">In Progress</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">{stats.inProgress}</p>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-slate-500 text-sm">Pending</p>
          <p className="text-2xl font-bold text-yellow-600 mt-1">{stats.pending}</p>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-3 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            <option value="PENDING">Pending</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
            <option value="FILED">Filed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Tasks List */}
      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <p className="text-slate-500">Loading tasks...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center">
            <p className="text-red-500">{error}</p>
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-slate-500">
              {tasks.length === 0 ? 'No tasks assigned yet' : 'No tasks match your search'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Task</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Type</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Customer</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Due Date</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Priority</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Progress</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {filteredTasks.map(task => (
                  <tr key={task.task_id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-start gap-3">
                        {getStatusIcon(task.status)}
                        <div>
                          <p className="font-medium text-slate-900">{task.task_title}</p>
                          {task.description && (
                            <p className="text-sm text-slate-500 line-clamp-1">{task.description}</p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-slate-600">{task.task_type_code}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-slate-600">{task.customer?.display_name || 'N/A'}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-slate-600">
                        {new Date(task.due_date).toLocaleDateString('en-IN')}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {task.priority && (
                        <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-slate-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{ width: `${task.completion_percentage || 0}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-slate-600 w-8">{task.completion_percentage || 0}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                        {task.status?.replace(/_/g, ' ') || 'PENDING'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
