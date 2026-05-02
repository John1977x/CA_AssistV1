import { useAuthStore } from '@/store/authStore'
import { FileText, CheckCircle, Clock, AlertCircle, MessageSquare, Download } from 'lucide-react'

export default function ClientDashboard() {
  const user = useAuthStore(s => s.user)

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
        return <CheckCircle size={16} />
      case 'in-progress':
        return <Clock size={16} />
      case 'pending':
        return <AlertCircle size={16} />
      default:
        return null
    }
  }

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
              <p className="text-3xl font-bold text-slate-900 mt-1">3</p>
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
              <p className="text-3xl font-bold text-green-600 mt-1">1</p>
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
              <p className="text-3xl font-bold text-blue-600 mt-1">1</p>
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
              <p className="text-3xl font-bold text-yellow-600 mt-1">1</p>
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
            <div className="space-y-4">
              {tasks.map(task => (
                <div key={task.id} className="border border-slate-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(task.status)}
                      <div>
                        <h3 className="font-medium text-slate-900">{task.title}</h3>
                        <p className="text-sm text-slate-500">Due: {task.dueDate}</p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                      {task.status.replace('-', ' ')}
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${task.progress}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-slate-500 mt-2">{task.progress}% complete</p>
                </div>
              ))}
            </div>
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
