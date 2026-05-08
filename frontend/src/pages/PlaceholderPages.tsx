import { Construction, Sparkles, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

function PlaceholderPage({ title, description, icon = '🚧' }: { title: string; description: string; icon?: string }) {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="card p-16 text-center">
        <div className="text-5xl mb-4">{icon}</div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">{title}</h2>
        <p className="text-slate-500 text-sm max-w-sm mx-auto">{description}</p>
        <div className="mt-6 inline-flex items-center gap-2 text-xs text-slate-400 bg-slate-50 px-4 py-2 rounded-full">
          <Construction size={12} /> Coming in next module release
        </div>
      </div>
    </div>
  )
}

function DevelopmentPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-6 relative overflow-hidden">
      {/* Subtle background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-100 rounded-full mix-blend-multiply filter blur-3xl opacity-40"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl opacity-40"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-100 rounded-full mix-blend-multiply filter blur-3xl opacity-40"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-2xl mx-auto text-center">
        {/* Animated icon */}
        <div className="mb-8 inline-block">
          <div className="relative w-24 h-24 flex items-center justify-center">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-200 to-purple-200 rounded-full opacity-40"></div>
            <div className="text-6xl animate-bounce">🚀</div>
          </div>
        </div>

        {/* Main heading */}
        <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-4 leading-tight">
          Something <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Amazing</span> is Coming
        </h1>

        {/* Description */}
        <p className="text-xl text-slate-600 mb-8 leading-relaxed">
          Our team is crafting something extraordinary for you. This feature is currently under development and will be launched soon with incredible capabilities.
        </p>

        {/* Features list */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4 hover:shadow-lg transition-all">
            <Sparkles className="w-6 h-6 text-blue-600 mx-auto mb-2" />
            <p className="text-sm text-slate-700 font-medium">Cutting-edge Design</p>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4 hover:shadow-lg transition-all">
            <Sparkles className="w-6 h-6 text-purple-600 mx-auto mb-2" />
            <p className="text-sm text-slate-700 font-medium">Powerful Features</p>
          </div>
          <div className="bg-gradient-to-br from-pink-50 to-pink-100 border border-pink-200 rounded-lg p-4 hover:shadow-lg transition-all">
            <Sparkles className="w-6 h-6 text-pink-600 mx-auto mb-2" />
            <p className="text-sm text-slate-700 font-medium">Seamless Experience</p>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => navigate(-1)}
            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg hover:shadow-blue-600/50 transition-all transform hover:scale-105"
          >
            Go Back
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-8 py-3 bg-slate-100 border border-slate-300 text-slate-900 font-semibold rounded-lg hover:bg-slate-200 transition-all flex items-center justify-center gap-2"
          >
            Back to Dashboard <ArrowRight size={18} />
          </button>
        </div>

        {/* Status badge */}
        <div className="mt-12 inline-flex items-center gap-2 text-sm text-slate-600 bg-slate-100 border border-slate-300 px-6 py-3 rounded-full">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span>Status: In Active Development</span>
        </div>
      </div>

      {/* CSS for animations */}
      <style>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  )
}

export const GSTPage       = () => <PlaceholderPage icon="📊" title="GST Management" description="Automated GSTR-1, GSTR-3B filing, reconciliation and error detection." />
export const ITRPage        = () => <PlaceholderPage icon="📋" title="Income Tax & TDS" description="Automated ITR preparation, bulk TDS returns and tax calculations." />
export const PortfolioPage  = () => <PlaceholderPage icon="📈" title="Portfolio & Wealth" description="Investment analysis, portfolio construction and performance tracking." />
export const BranchesPage   = () => <PlaceholderPage icon="🏢" title="Branches" description="Manage your firm's branch locations and assign staff." />
export const RolesPage      = () => <PlaceholderPage icon="🔐" title="Roles & Permissions" description="Define roles and granular module-level permissions for your team." />
export const SettingsPage   = () => <PlaceholderPage icon="⚙️" title="Settings" description="Application, notification, integration and billing settings." />
export const ProfilePage    = () => <PlaceholderPage icon="👤" title="My Profile" description="Update your personal details, photo and preferences." />
export const SecurityPage   = () => <PlaceholderPage icon="🛡️" title="Security" description="Manage your password, two-factor authentication and active sessions." />
export const NotFoundPage   = () => <DevelopmentPage />
