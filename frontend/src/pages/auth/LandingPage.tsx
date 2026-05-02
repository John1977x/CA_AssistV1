import { useNavigate } from 'react-router-dom'
import { Building2, Users, ArrowRight } from 'lucide-react'

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-brand-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">CA</span>
            </div>
            <span className="text-white text-xl font-bold">CA Assists</span>
          </div>
          <button
            onClick={() => navigate('/login')}
            className="text-slate-300 hover:text-white transition-colors"
          >
            Firm Login
          </button>
        </div>
      </div>

      {/* Hero */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Your Complete CA Practice Suite
          </h1>
          <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
            GST filing, ITR preparation, task management, and client communication — all in one place.
          </p>
        </div>

        {/* Login Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-2xl mx-auto">
          {/* Client Login */}
          <div
            onClick={() => navigate('/client/login')}
            className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl p-8 cursor-pointer hover:shadow-2xl hover:scale-105 transition-all"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Client Portal</h2>
                <p className="text-blue-100">Access your documents and track tasks</p>
              </div>
              <div className="w-16 h-16 bg-white/20 rounded-lg flex items-center justify-center">
                <Building2 className="text-white" size={32} />
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex items-center gap-2 text-blue-100">
                <span className="text-lg">📄</span>
                <span>View documents and filings</span>
              </div>
              <div className="flex items-center gap-2 text-blue-100">
                <span className="text-lg">✅</span>
                <span>Track task progress</span>
              </div>
              <div className="flex items-center gap-2 text-blue-100">
                <span className="text-lg">💬</span>
                <span>Communicate with your CA</span>
              </div>
            </div>

            <div className="bg-white/10 border border-white/20 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-100">
                <strong>Demo Login:</strong><br />
                Email: client@example.com<br />
                Password: CAassist@2026
              </p>
            </div>

            <button className="w-full bg-white text-blue-600 font-bold py-3 rounded-lg hover:bg-blue-50 transition-colors flex items-center justify-center gap-2">
              Login as Client <ArrowRight size={20} />
            </button>
          </div>

          {/* Employee Login */}
          <div
            onClick={() => navigate('/employee/login')}
            className="bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-2xl p-8 cursor-pointer hover:shadow-2xl hover:scale-105 transition-all"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Employee Portal</h2>
                <p className="text-emerald-100">Manage tasks and collaborate with team</p>
              </div>
              <div className="w-16 h-16 bg-white/20 rounded-lg flex items-center justify-center">
                <Users className="text-white" size={32} />
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex items-center gap-2 text-emerald-100">
                <span className="text-lg">📋</span>
                <span>Manage assigned tasks</span>
              </div>
              <div className="flex items-center gap-2 text-emerald-100">
                <span className="text-lg">👥</span>
                <span>Collaborate with team</span>
              </div>
              <div className="flex items-center gap-2 text-emerald-100">
                <span className="text-lg">📊</span>
                <span>Track work progress</span>
              </div>
            </div>

            <div className="bg-white/10 border border-white/20 rounded-lg p-4 mb-6">
              <p className="text-sm text-emerald-100">
                <strong>Demo Login:</strong><br />
                Email: employee@firm.com<br />
                Password: CAassist@2026
              </p>
            </div>

            <button className="w-full bg-white text-emerald-600 font-bold py-3 rounded-lg hover:bg-emerald-50 transition-colors flex items-center justify-center gap-2">
              Login as Employee <ArrowRight size={20} />
            </button>
          </div>
        </div>

        {/* Features */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { icon: '🔒', title: 'Bank-Grade Security', desc: 'Your data is encrypted and secure' },
            { icon: '⚡', title: 'Real-Time Updates', desc: 'Get instant notifications and updates' },
            { icon: '📱', title: 'Mobile Friendly', desc: 'Access from any device, anywhere' },
          ].map((feature, idx) => (
            <div key={idx} className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 text-center">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-slate-400">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-slate-700 mt-20 py-8 text-center text-slate-400">
        <p>© 2026 CA Assists. All rights reserved.</p>
      </div>
    </div>
  )
}
