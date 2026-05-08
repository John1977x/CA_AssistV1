import { useAuthStore } from '@/store/authStore'
import { FileText, CheckCircle, Clock, AlertCircle, MessageSquare, Download } from 'lucide-react'
import { useEffect, useState } from 'react'
import { tasksApi } from '@/api/tasks'
import type { Task } from '@/types/task'

export default function ClientDashboard() {
  const user = useAuthStore(s => s.user)
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true)
        const response = await tasksApi.clientTasks({ page: 1, page_size: 50 })
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

  const documents = [
    { id: 1, name: 'GST Return - March 2026', date: '2026-04-10', size: '2.4 MB' },
    { id: 2, name: 'Income Tax Return - FY 2025-26', date: '2026-04-05', size: '3.1 MB' },
    { id: 3, name: 'TDS Certificate', date: '2026-03-31', size: '1.2 MB' },
  ]

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
        return <CheckCircle size={16} />
      case 'IN_PROGRESS':
        return <Clock size={16} />
      case 'PENDING':
        return <AlertCircle size={16} />
      default:
        return null
    }
  }

  const getTaskStats = () => {
    const total = tasks.length
    const completed = tasks.filter(t => ['COMPLETED', 'FILED'].includes(t.status?.toUpperCase() || '')).length
    const inProgress = tasks.filter(t => t.status?.toUpperCase() === 'IN_PROGRESS').length
    const pending = tasks.filter(t => t.status?.toUpperCase() === 'PENDING').length
    return { total, completed, inProgress, pending }
  }

  const stats = getTaskStats()

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Welcome, {user?.first_name}!</h1>
        <p className="text-slate-500 mt-2">Here's your account overview and recent activities</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-500 text-sm">Total Tasks</p>
              <p className="text-3xl font-bold text-slate-900 mt-1">{stats.total}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="text-blue-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-500 text-sm">Completed</p>
              <p className="text-3xl font-bold text-green-600 mt-1">{stats.completed}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="text-green-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-500 text-sm">In Progress</p>
              <p className="text-3xl font-bold text-blue-600 mt-1">{stats.inProgress}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Clock className="text-blue-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-500 text-sm">Pending</p>
              <p className="text-3xl font-bold text-yellow-600 mt-1">{stats.pending}</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <AlertCircle className="text-yellow-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tasks */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Your Tasks</h2>
            {loading ? (
              <div className="text-center py-8">
                <p className="text-slate-500">Loading tasks...</p>
              </div>
            ) : error ? (
              <div className="text-center py-8">
                <p className="text-red-500">{error}</p>
              </div>
            ) : tasks.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-slate-500">No tasks assigned yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {tasks.map(task => (
                  <div key={task.task_id} className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3 flex-1">
                        {getStatusIcon(task.status)}
                        <div className="flex-1">
                          <h3 className="font-medium text-slate-900">{task.task_title}</h3>
                          <p className="text-sm text-slate-500">
                            Due: {new Date(task.due_date).toLocaleDateString('en-IN')}
                          </p>
                          <p className="text-xs text-slate-400 mt-1">{task.task_type_code}</p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap ml-2 ${getStatusColor(task.status)}`}>
                        {task.status?.replace(/_/g, ' ') || 'PENDING'}
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${task.completion_percentage || 0}%` }}
                      ></div>
                    </div>
                    <div className="flex items-center justify-between mt-2">
                      <p className="text-xs text-slate-500">{task.completion_percentage || 0}% complete</p>
                      {task.priority && (
                        <span className="text-xs font-medium text-slate-600 bg-slate-100 px-2 py-1 rounded">
                          {task.priority}
                        </span>
                      )}
                    </div>
                    {task.description && (
                      <p className="text-sm text-slate-600 mt-3 line-clamp-2">{task.description}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="space-y-6">
          {/* Messages */}
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <MessageSquare className="text-blue-600" size={20} />
              </div>
              <h3 className="font-bold text-slate-900">Messages</h3>
            </div>
            <p className="text-sm text-slate-600 mb-4">You have 2 unread messages from your CA</p>
            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors">
              View Messages
            </button>
          </div>

          {/* Support */}
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <h3 className="font-bold text-slate-900 mb-4">Need Help?</h3>
            <p className="text-sm text-slate-600 mb-4">Contact your CA firm for support</p>
            <button className="w-full bg-slate-200 hover:bg-slate-300 text-slate-900 font-medium py-2 rounded-lg transition-colors">
              Contact Support
            </button>
          </div>
        </div>
      </div>

      {/* Documents */}
      <div className="mt-6 bg-white rounded-lg border border-slate-200 p-6">
        <h2 className="text-lg font-bold text-slate-900 mb-4">Recent Documents</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-600">Document Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-600">Date</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-600">Size</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-600">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {documents.map(doc => (
                <tr key={doc.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-sm text-slate-900">{doc.name}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{doc.date}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{doc.size}</td>
                  <td className="px-4 py-3 text-sm">
                    <button className="text-blue-600 hover:text-blue-700 flex items-center gap-1">
                      <Download size={16} /> Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
