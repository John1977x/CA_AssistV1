import { useAuthStoreV2 } from '@/store/authStoreV2'
import { FileText, CheckCircle, Clock, AlertCircle, Download, MessageSquare } from 'lucide-react'

export default function ClientDashboardV2() {
  const { user, company } = useAuthStoreV2()

  const tasks = [
    { id: 1, title: 'GST Return Filing', status: 'completed', dueDate: '2026-04-15', progress: 100 },
    { id: 2, title: 'Income Tax Return', status: 'in-progress', dueDate: '2026-05-31', progress: 65 },
    { id: 3, title: 'TDS Compliance', status: 'pending', dueDate: '2026-06-15', progress: 0 },
  ]

  const documents = [
    { id: 1, name: 'GST Return - March 2026', date: '2026-04-10', size: '2.4 MB' },
    { id: 2, name: 'Income Tax Return - FY 2025-26', date: '2026-04-05', size: '3.1 MB' },
    { id: 3, name: 'TDS Certificate', date: '2026-03-31', size: '1.2 MB' },
  ]

  const stats = [
    { label: 'Completed Tasks', value: '1', icon: CheckCircle, color: 'bg-green-500' },
    { label: 'In Progress', value: '1', icon: Clock, color: 'bg-blue-500' },
    { label: 'Pending', value: '1', icon: AlertCircle, color: 'bg-orange-500' },
    { label: 'Documents', value: '3', icon: FileText, color: 'bg-purple-500' },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'in-progress':
        return 'bg-blue-100 text-blue-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} className="text-green-600" />
      case 'in-progress':
        return <Clock size={16} className="text-blue-600" />
      case 'pending':
        return <AlertCircle size={16} className="text-yellow-600" />
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome, {user?.first_name}!
          </h1>
          <p className="text-slate-400">Here's your account overview and recent activities</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, idx) => {
            const Icon = stat.icon
            return (
              <div key={idx} className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm mb-1">{stat.label}</p>
                    <p className="text-3xl font-bold text-white">{stat.value}</p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="text-white" size={24} />
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Tasks and Documents */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Your Tasks */}
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4">Your Tasks</h2>
            <div className="space-y-3">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className="p-4 bg-slate-700 rounded-lg hover:bg-slate-650 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(task.status)}
                      <h3 className="text-white font-semibold">{task.title}</h3>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(task.status)}`}>
                      {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm text-slate-400 mb-2">
                    <span>Due: {task.dueDate}</span>
                    <span>{task.progress}% Complete</span>
                  </div>
                  <div className="w-full bg-slate-600 rounded-full h-2">
                    <div
                      className="bg-brand-600 h-2 rounded-full transition-all"
                      style={{ width: `${task.progress}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Documents */}
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4">Recent Documents</h2>
            <div className="space-y-3">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-4 bg-slate-700 rounded-lg hover:bg-slate-650 transition-colors"
                >
                  <div className="flex items-center gap-3 flex-1">
                    <FileText className="text-brand-400" size={20} />
                    <div className="flex-1">
                      <p className="text-white font-semibold text-sm">{doc.name}</p>
                      <p className="text-slate-400 text-xs">{doc.date} • {doc.size}</p>
                    </div>
                  </div>
                  <button className="p-2 hover:bg-slate-600 rounded-lg transition-colors">
                    <Download className="text-brand-400" size={20} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Support Section */}
        <div className="mt-8 bg-slate-800 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-white mb-2">Need Help?</h3>
              <p className="text-slate-400">Contact our support team for any questions or issues</p>
            </div>
            <button className="flex items-center gap-2 px-6 py-3 bg-brand-600 hover:bg-brand-700 text-white rounded-lg transition-colors">
              <MessageSquare size={20} />
              Contact Support
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
