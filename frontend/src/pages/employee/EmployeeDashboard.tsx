import { useAuthStore } from '@/store/authStore'
import { CheckCircle, Clock, AlertCircle, Users, TrendingUp, Calendar } from 'lucide-react'

export default function EmployeeDashboard() {
  const user = useAuthStore(s => s.user)

  const myTasks = [
    { id: 1, title: 'GST Return - ABC Corp', client: 'ABC Corporation', status: 'completed', dueDate: '2026-04-15', priority: 'high' },
    { id: 2, title: 'Income Tax Return - XYZ Ltd', client: 'XYZ Limited', status: 'in-progress', dueDate: '2026-05-31', priority: 'high' },
    { id: 3, title: 'TDS Compliance - PQR Inc', client: 'PQR Industries', status: 'pending', dueDate: '2026-06-15', priority: 'medium' },
    { id: 4, title: 'Audit Report - MNO Corp', client: 'MNO Corporation', status: 'pending', dueDate: '2026-06-30', priority: 'low' },
  ]

  const teamMembers = [
    { id: 1, name: 'Rahul Verma', role: 'Article Assistant', status: 'online' },
    { id: 2, name: 'Priya Singh', role: 'Senior CA', status: 'online' },
    { id: 3, name: 'Amit Kumar', role: 'Manager', status: 'offline' },
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
        <h1 className="text-3xl font-bold text-slate-900">Welcome back, {user?.first_name}!</h1>
        <p className="text-slate-500 mt-2">Here's your work overview for today</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-500 text-sm">Assigned Tasks</p>
              <p className="text-3xl font-bold text-slate-900 mt-1">4</p>
            </div>
            <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center">
              <Calendar className="text-emerald-600" size={24} />
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
              <p className="text-3xl font-bold text-yellow-600 mt-1">2</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <AlertCircle className="text-yellow-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* My Tasks */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <h2 className="text-lg font-bold text-slate-900 mb-4">My Tasks</h2>
            <div className="space-y-3">
              {myTasks.map(task => (
                <div key={task.id} className="border border-slate-200 rounded-lg p-4 hover:bg-slate-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      {getStatusIcon(task.status)}
                      <div className="flex-1">
                        <h3 className="font-medium text-slate-900">{task.title}</h3>
                        <p className="text-sm text-slate-500">{task.client}</p>
                        <div className="flex items-center gap-4 mt-2">
                          <span className="text-xs text-slate-500">Due: {task.dueDate}</span>
                          <span className={`text-xs font-medium ${getPriorityColor(task.priority)}`}>
                            {task.priority.toUpperCase()} PRIORITY
                          </span>
                        </div>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap ${getStatusColor(task.status)}`}>
                      {task.status.replace('-', ' ')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Team & Quick Actions */}
        <div className="space-y-6">
          {/* Team Members */}
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                <Users className="text-emerald-600" size={20} />
              </div>
              <h3 className="font-bold text-slate-900">Team Members</h3>
            </div>
            <div className="space-y-3">
              {teamMembers.map(member => (
                <div key={member.id} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-900">{member.name}</p>
                    <p className="text-xs text-slate-500">{member.role}</p>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${member.status === 'online' ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                </div>
              ))}
            </div>
          </div>

          {/* Performance */}
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="text-blue-600" size={20} />
              </div>
              <h3 className="font-bold text-slate-900">Performance</h3>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-slate-600 mb-1">Completion Rate</p>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                </div>
                <p className="text-xs text-slate-500 mt-1">75%</p>
              </div>
              <div>
                <p className="text-sm text-slate-600 mb-1">On-Time Delivery</p>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '90%' }}></div>
                </div>
                <p className="text-xs text-slate-500 mt-1">90%</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Upcoming Deadlines */}
      <div className="mt-6 bg-white rounded-lg border border-slate-200 p-6">
        <h2 className="text-lg font-bold text-slate-900 mb-4">Upcoming Deadlines</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { date: '2026-04-15', task: 'GST Return - ABC Corp', days: 'Today' },
            { date: '2026-05-31', task: 'Income Tax Return - XYZ Ltd', days: '31 days' },
            { date: '2026-06-15', task: 'TDS Compliance - PQR Inc', days: '46 days' },
          ].map((deadline, idx) => (
            <div key={idx} className="border border-slate-200 rounded-lg p-4">
              <p className="text-sm font-medium text-slate-900">{deadline.task}</p>
              <p className="text-xs text-slate-500 mt-1">Due: {deadline.date}</p>
              <p className="text-xs font-medium text-emerald-600 mt-2">{deadline.days}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
