import { useAuthStoreV2 } from '@/store/authStoreV2'
import { CheckCircle, Clock, AlertCircle, Users, TrendingUp } from 'lucide-react'

export default function EmployeeDashboardV2() {
  const { user, company } = useAuthStoreV2()

  const myTasks = [
    { id: 1, title: 'GST Return - ABC Corp', client: 'ABC Corporation', status: 'completed', dueDate: '2026-04-15', priority: 'high' },
    { id: 2, title: 'Income Tax Return - XYZ Ltd', client: 'XYZ Limited', status: 'in-progress', dueDate: '2026-05-31', priority: 'high' },
    { id: 3, title: 'TDS Compliance - PQR Inc', client: 'PQR Industries', status: 'pending', dueDate: '2026-06-15', priority: 'medium' },
    { id: 4, title: 'Audit Report - MNO Corp', client: 'MNO Corporation', status: 'pending', dueDate: '2026-06-30', priority: 'low' },
  ]

  const teamMembers = [
    { id: 1, name: 'Rahul Verma', role: 'Manager', status: 'online' },
    { id: 2, name: 'Priya Singh', role: 'Senior Employee', status: 'online' },
    { id: 3, name: 'Amit Kumar', role: 'Employee', status: 'offline' },
  ]

  const stats = [
    { label: 'Completed Tasks', value: '24', icon: CheckCircle, color: 'bg-green-500' },
    { label: 'In Progress', value: '5', icon: Clock, color: 'bg-blue-500' },
    { label: 'Pending', value: '3', icon: AlertCircle, color: 'bg-orange-500' },
    { label: 'Completion Rate', value: '89%', icon: TrendingUp, color: 'bg-purple-500' },
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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-600'
      case 'medium':
        return 'text-yellow-600'
      case 'low':
        return 'text-green-600'
      default:
        return 'text-gray-600'
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
            Welcome back, {user?.first_name}!
          </h1>
          <p className="text-slate-400">Here's your task overview and team information</p>
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

        {/* Tasks and Team */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* My Tasks */}
          <div className="lg:col-span-2 bg-slate-800 rounded-lg border border-slate-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4">My Tasks</h2>
            <div className="space-y-3">
              {myTasks.map((task) => (
                <div
                  key={task.id}
                  className="flex items-center justify-between p-4 bg-slate-700 rounded-lg hover:bg-slate-650 transition-colors"
                >
                  <div className="flex items-center gap-3 flex-1">
                    {getStatusIcon(task.status)}
                    <div className="flex-1">
                      <h3 className="text-white font-semibold text-sm">{task.title}</h3>
                      <p className="text-slate-400 text-xs">{task.client}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(task.priority)}`}>
                      {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(task.status)}`}>
                      {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                    </span>
                    <span className="text-slate-400 text-xs whitespace-nowrap">{task.dueDate}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Team Members */}
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4">Team Members</h2>
            <div className="space-y-3">
              {teamMembers.map((member) => (
                <div
                  key={member.id}
                  className="flex items-center justify-between p-3 bg-slate-700 rounded-lg hover:bg-slate-650 transition-colors"
                >
                  <div className="flex items-center gap-3 flex-1">
                    <div className="w-8 h-8 bg-brand-600 rounded-full flex items-center justify-center">
                      <span className="text-white text-xs font-bold">
                        {member.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div className="flex-1">
                      <p className="text-white font-semibold text-sm">{member.name}</p>
                      <p className="text-slate-400 text-xs">{member.role}</p>
                    </div>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${member.status === 'online' ? 'bg-green-500' : 'bg-slate-500'}`}></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
