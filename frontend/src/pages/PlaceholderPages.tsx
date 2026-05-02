import { Construction } from 'lucide-react'

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

export const GSTPage       = () => <PlaceholderPage icon="📊" title="GST Management" description="Automated GSTR-1, GSTR-3B filing, reconciliation and error detection." />
export const ITRPage        = () => <PlaceholderPage icon="📋" title="Income Tax & TDS" description="Automated ITR preparation, bulk TDS returns and tax calculations." />
export const PortfolioPage  = () => <PlaceholderPage icon="📈" title="Portfolio & Wealth" description="Investment analysis, portfolio construction and performance tracking." />
export const BranchesPage   = () => <PlaceholderPage icon="🏢" title="Branches" description="Manage your firm's branch locations and assign staff." />
export const RolesPage      = () => <PlaceholderPage icon="🔐" title="Roles & Permissions" description="Define roles and granular module-level permissions for your team." />
export const SettingsPage   = () => <PlaceholderPage icon="⚙️" title="Settings" description="Application, notification, integration and billing settings." />
export const ProfilePage    = () => <PlaceholderPage icon="👤" title="My Profile" description="Update your personal details, photo and preferences." />
export const SecurityPage   = () => <PlaceholderPage icon="🛡️" title="Security" description="Manage your password, two-factor authentication and active sessions." />
export const NotFoundPage   = () => <PlaceholderPage icon="404" title="Page Not Found" description="The page you're looking for doesn't exist." />
