import { Users, UserCheck, ClipboardList, AlertCircle, TrendingUp, Calendar } from 'lucide-react'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import DocumentRequestsWidget from '@/components/owner/DocumentRequestsWidget'

const quickLinks = [
  { label: 'Add Team Member', desc: 'Team management', href: '/users', color: 'bg-blue-500' },
  { label: 'Add Client', desc: 'Client management', href: '/clients', color: 'bg-green-500' },
  { label: 'Create Task', desc: 'Task management', href: '/tasks', color: 'bg-orange-500' },
  { label: 'View Reports', desc: 'Performance metrics', href: '/billing', color: 'bg-purple-500' },
]

export default function ManagerDashboard() {
  const user = useAuthStoreV2(s => s.user)
  const company = useAuthStoreV2(s => s.company)
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Welcome */}
      <div className="bg-gradient-to-r from-brand-800 to-brand-700 rounded-2xl p-6 text-white">
        <h2 className="text-xl font-bold mb-1">
          {greeting}, {user?.first_name}! 👋
        </h2>
        <p className="text-brand-200 text-sm">Manage your team and clients in {company?.company_name}</p>
        <div className="mt-4 flex items-center gap-3">
          <div className="bg-white/10 rounded-lg px-3 py-1.5 text-xs font-medium">
            <Calendar size={12} className="inline mr-1" />
            {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
          </div>
          <div className="bg-brand-600/50 text-brand-100 rounded-lg px-3 py-1.5 text-xs font-medium">📊 Manager</div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Quick Actions */}
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-2">
              {quickLinks.map(q => (
                <a key={q.label} href={q.href}
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors group">
                  <div className={`w-8 h-8 ${q.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
                    <TrendingUp size={14} className="text-white" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-900 group-hover:text-brand-800">{q.label}</div>
                    <div className="text-xs text-slate-500">{q.desc}</div>
                  </div>
                </a>
              ))}
            </div>
          </div>

          {/* Team Performance */}
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-900 mb-4">Team Performance</h3>
            <div className="space-y-3">
              {[
                { name: 'John Doe', role: 'Senior Associate', tasks: 12, completed: 10, status: 'active' },
                { name: 'Jane Smith', role: 'Associate', tasks: 8, completed: 7, status: 'active' },
                { name: 'Mike Johnson', role: 'Junior Associate', tasks: 5, completed: 3, status: 'active' },
                { name: 'Sarah Williams', role: 'Intern', tasks: 3, completed: 2, status: 'active' },
              ].map(member => (
                <div key={member.name} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-brand-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-brand-700">{member.name.charAt(0)}</span>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-slate-900">{member.name}</div>
                      <div className="text-xs text-slate-500">{member.role}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-slate-900">{member.completed}/{member.tasks}</div>
                    <div className="text-xs text-slate-500">tasks done</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column — Stats and Document Requests */}
        <div className="space-y-4">
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-900 mb-4">Team Stats</h3>
            <div className="space-y-4">
              {[
                { label: 'Team Members', value: '8', icon: '👥' },
                { label: 'Active Clients', value: '24', icon: '🏢' },
                { label: 'Tasks Completed', value: '156', icon: '✅' },
                { label: 'Pending Tasks', value: '12', icon: '⏳' },
              ].map(stat => (
                <div key={stat.label} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{stat.icon}</span>
                    <span className="text-sm text-slate-600">{stat.label}</span>
                  </div>
                  <span className="font-semibold text-slate-900">{stat.value}</span>
                </div>
              ))}
            </div>
          </div>
          <DocumentRequestsWidget />
        </div>
      </div>
    </div>
  )
}
