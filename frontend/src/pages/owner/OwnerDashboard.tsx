import { Users, UserCheck, ClipboardList, AlertCircle, TrendingUp, Calendar } from 'lucide-react'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import { SubscriptionWidget } from '@/components/subscription/SubscriptionWidget'

const quickLinks = [
  { label: 'File GSTR-1',    desc: 'GST Management',   href: '/gst',      color: 'bg-blue-500' },
  { label: 'File GSTR-3B',   desc: 'GST Management',   href: '/gst',      color: 'bg-indigo-500' },
  { label: 'Add New Client', desc: 'Client management', href: '/clients',  color: 'bg-green-500' },
  { label: 'Create Task',    desc: 'Workflow management',href: '/tasks',   color: 'bg-orange-500' },
]

export default function OwnerDashboard() {
  const user = useAuthStoreV2(s => s.user)
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Welcome */}
      <div className="bg-gradient-to-r from-brand-800 to-brand-700 rounded-2xl p-6 text-white">
        <h2 className="text-xl font-bold mb-1">
          {greeting}, {user?.first_name}! 👋
        </h2>
        <p className="text-brand-200 text-sm">Here's what's happening in your firm today.</p>
        <div className="mt-4 flex items-center gap-3">
          <div className="bg-white/10 rounded-lg px-3 py-1.5 text-xs font-medium">
            <Calendar size={12} className="inline mr-1" />
            {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
          </div>
          {user?.is_owner && (
            <div className="bg-yellow-400/20 text-yellow-200 rounded-lg px-3 py-1.5 text-xs font-medium">✨ Owner</div>
          )}
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

          {/* Upcoming Deadlines */}
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-900 mb-4">Upcoming Compliance Deadlines</h3>
            <div className="space-y-3">
              {[
                { name: 'GSTR-1 Filing',  date: '11 May 2024', type: 'GST', days: 5,  urgent: true },
                { name: 'TDS Return Q4',  date: '31 May 2024', type: 'TDS', days: 25, urgent: false },
                { name: 'GSTR-3B Filing', date: '20 May 2024', type: 'GST', days: 14, urgent: false },
                { name: 'PT Return',      date: '30 May 2024', type: 'PT',  days: 24, urgent: false },
              ].map(d => (
                <div key={d.name} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className={`px-2 py-0.5 rounded text-xs font-semibold
                      ${d.type === 'GST' ? 'bg-blue-100 text-blue-700' :
                        d.type === 'TDS' ? 'bg-purple-100 text-purple-700' :
                        'bg-slate-200 text-slate-600'}`}>
                      {d.type}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-slate-900">{d.name}</div>
                      <div className="text-xs text-slate-500">{d.date}</div>
                    </div>
                  </div>
                  <div className={`text-xs font-semibold px-2.5 py-1 rounded-full
                    ${d.urgent ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                    {d.days}d left
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column — Subscription widget */}
        <div className="space-y-4">
          <SubscriptionWidget />
        </div>
      </div>
    </div>
  )
}
