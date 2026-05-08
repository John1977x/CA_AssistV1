import { useState } from 'react'
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom'
import {
  LayoutDashboard, Users, Building2, UserCheck, Settings, CreditCard,
  ChevronDown, LogOut, Bell, Menu, X, Shield, Building,
  FileText, ClipboardList, BookOpen, TrendingUp, ChevronRight,
  Calendar, Briefcase, BarChart3, Ticket, Mail, DollarSign,
  GitBranch, User, Clock, CheckSquare, Edit3,
} from 'lucide-react'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import { authV2Api } from '@/api/authV2'
import toast from 'react-hot-toast'
import clsx from 'clsx'
import { TrialBanner } from '@/components/subscription/SubscriptionWidget'
import { CompanyBranchInfo } from './CompanyBranchInfo'
import { ChangeCompanyBranchModal } from './ChangeCompanyBranchModal'

// Owner Navigation
const OWNER_NAV_GROUPS = [
  {
    label: 'Menu',
    items: [
      { to: '/dashboard-unified', icon: Calendar, label: 'Dashboard' },
      { to: '/owner/company', icon: Building2, label: 'Company' },
      { to: '/owner/clients', icon: UserCheck, label: 'Client' },
      { to: '/branches', icon: Building, label: 'Branches' },
    ],
  },
  {
    label: 'Employee',
    items: [
      { to: '/owner/reporting', icon: BarChart3, label: 'Reporting' },
      { to: '/owner/employees', icon: Users, label: 'Employees' },
    ],
  },
  {
    label: 'Task',
    items: [
      { to: '/tasks', icon: ClipboardList, label: 'Tasks' },
      { to: '/enquiries', icon: Mail, label: 'Enquiries' },
      { to: '/owner/document-requests', icon: FileText, label: 'Document Requests' },
    ],
  },
  {
    label: 'Admin',
    items: [
      { to: '/owner/leave', icon: Clock, label: 'Leave' },
      { to: '/owner/subscription', icon: CreditCard, label: 'Subscription' },
      { to: '/profile', icon: User, label: 'Profile' },
    ],
  },
]

// Manager Navigation
const MANAGER_NAV_GROUPS = [
  {
    label: 'Menu',
    items: [
      { to: '/dashboard-unified', icon: Calendar, label: 'Dashboard' },
      { to: '/manager/clients', icon: UserCheck, label: 'Client' },
    ],
  },
  {
    label: 'Employee',
    items: [
      { to: '/manager/reporting', icon: BarChart3, label: 'Reporting' },
      { to: '/manager/employees', icon: Users, label: 'Employees' },
    ],
  },
  {
    label: 'Task',
    items: [
      { to: '/manager/tasks', icon: ClipboardList, label: 'Tasks' },
      { to: '/manager/enquiries', icon: Mail, label: 'Enquiries' },
      { to: '/manager/document-requests', icon: FileText, label: 'Document Requests' },
    ],
  },
  {
    label: 'Admin',
    items: [
      { to: '/manager/leave', icon: Clock, label: 'Leave' },
      { to: '/manager/subscription', icon: CreditCard, label: 'Subscription' },
      { to: '/profile', icon: User, label: 'Profile' },
    ],
  },
]

// Employee Navigation
const EMPLOYEE_NAV_GROUPS = [
  {
    label: 'Menu',
    items: [
      { to: '/dashboard-unified', icon: Calendar, label: 'Dashboard' },
    ],
  },
  {
    label: 'Employee',
    items: [
      { to: '/employee/reporting', icon: BarChart3, label: 'Reporting' },
    ],
  },
  {
    label: 'Task',
    items: [
      { to: '/employee/tasks', icon: ClipboardList, label: 'Tasks' },
      { to: '/employee/enquiries', icon: Mail, label: 'Enquiries' },
      { to: '/employee/document-requests', icon: FileText, label: 'Document Requests' },
    ],
  },
]

// Client Navigation
const CLIENT_NAV_GROUPS = [
  {
    label: 'Menu',
    items: [
      { to: '/dashboard-unified', icon: Calendar, label: 'Dashboard' },
    ],
  },
  {
    label: 'Task',
    items: [
      { to: '/client/tasks', icon: ClipboardList, label: 'Tasks' },
      { to: '/client/enquiries', icon: Mail, label: 'Enquiries' },
      { to: '/client/document-requests', icon: FileText, label: 'Document Requests' },
    ],
  },
]

function Avatar({ user }: { user: any }) {
  const initials = `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
  if (user.avatar_url) {
    return <img src={user.avatar_url} alt={user.display_name || ''} className="w-8 h-8 rounded-full object-cover" />
  }
  return (
    <div className="w-8 h-8 rounded-full bg-brand-700 flex items-center justify-center text-white text-xs font-bold">
      {initials}
    </div>
  )
}

function SidebarContent({ onClose }: { onClose?: () => void }) {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { user, company, logout } = useAuthStoreV2()
  const [profileOpen, setProfileOpen] = useState(false)

  // Get navigation based on role
  const getNavGroups = () => {
    switch (company?.role) {
      case 'OWNER':
        return OWNER_NAV_GROUPS
      case 'MANAGER':
        return MANAGER_NAV_GROUPS
      case 'EMPLOYEE':
        return EMPLOYEE_NAV_GROUPS
      case 'CLIENT':
        return CLIENT_NAV_GROUPS
      default:
        return OWNER_NAV_GROUPS
    }
  }

  const navGroups = getNavGroups()

  const handleLogout = async () => {
    try { await authV2Api.logout() } catch {}
    logout()
    navigate('/login')
    toast.success('Signed out.')
  }

  return (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-6 border-b border-slate-100">
        <div className="flex items-start gap-3 flex-1">
          <div className="w-10 h-10 bg-brand-800 rounded-lg flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold text-base">CA</span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-base font-bold text-slate-900">CA Assists</div>
            <div className="text-sm text-slate-600 truncate font-medium">
              {company?.company_name || user?.email}
            </div>
            {company?.branch_name && (
              <div className="text-xs text-slate-500 truncate mt-1">
                Branch: {company.branch_name}
              </div>
            )}
          </div>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 lg:hidden flex-shrink-0">
            <X size={18} />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {navGroups.map(group => (
          <div key={group.label}>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5 px-3">
              {group.label}
            </p>
            <div className="space-y-0.5">
              {group.items.map(item => {
                const active = pathname.startsWith(item.to)
                
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    onClick={onClose}
                    className={clsx('sidebar-link', active && 'sidebar-link-active')}
                  >
                    {active && <ChevronRight size={14} className="mr-auto flex-shrink-0" />}
                    <item.icon size={16} className="flex-shrink-0" />
                    {item.label}
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* User profile footer */}
      <div className="border-t border-slate-100 p-3">
        <button
          onClick={() => setProfileOpen(!profileOpen)}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-50 transition-colors"
        >
          {user && <Avatar user={user} />}
          <div className="flex-1 text-left min-w-0">
            <div className="text-sm font-medium text-slate-900 truncate">
              {user?.display_name || `${user?.first_name} ${user?.last_name}`}
            </div>
            <div className="text-xs text-slate-500 truncate">{company?.role}</div>
          </div>
          <ChevronDown size={14} className={clsx('text-slate-400 transition-transform', profileOpen && 'rotate-180')} />
        </button>

        {profileOpen && (
          <div className="mt-1 space-y-0.5">
            <Link to="/profile" onClick={onClose}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-600 hover:bg-slate-50">
              <User size={14} /> My Profile
            </Link>
            <Link to="/security" onClick={onClose}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-600 hover:bg-slate-50">
              <Shield size={14} /> Security
            </Link>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-red-600 hover:bg-red-50"
            >
              <LogOut size={14} /> Sign Out
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [changeCompanyModalOpen, setChangeCompanyModalOpen] = useState(false)
  const { pathname } = useLocation()
  const { company } = useAuthStoreV2()

  // Get navigation based on role
  const getNavGroups = () => {
    switch (company?.role) {
      case 'OWNER':
        return OWNER_NAV_GROUPS
      case 'MANAGER':
        return MANAGER_NAV_GROUPS
      case 'EMPLOYEE':
        return EMPLOYEE_NAV_GROUPS
      case 'CLIENT':
        return CLIENT_NAV_GROUPS
      default:
        return OWNER_NAV_GROUPS
    }
  }

  const navGroups = getNavGroups()

  // Get page title from path
  const pageTitle = navGroups.flatMap(g => g.items).find(i => pathname.startsWith(i.to))?.label || 'Dashboard'

  // Check if user is owner
  const isOwner = company?.role === 'OWNER'

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex lg:flex-col w-60 bg-white border-r border-slate-200 flex-shrink-0">
        <SidebarContent />
      </aside>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-black/40" onClick={() => setSidebarOpen(false)} />
          <aside className="relative z-10 flex flex-col w-64 bg-white shadow-xl">
            <SidebarContent onClose={() => setSidebarOpen(false)} />
          </aside>
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Company/Branch Info Bar */}
        <CompanyBranchInfo />

        {/* Top bar */}
        <header className="bg-white border-b border-slate-200 px-4 lg:px-6 py-3 flex items-center gap-4 flex-shrink-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-1.5 rounded-lg text-slate-500 hover:bg-slate-100"
          >
            <Menu size={20} />
          </button>
          <h1 className="text-base font-semibold text-slate-900 flex-1">{pageTitle}</h1>
          <div className="flex items-center gap-2">
            {/* Change Company/Branch Icon - Only for Owners */}
            {isOwner && (
              <button
                onClick={() => setChangeCompanyModalOpen(true)}
                className="relative p-2 rounded-lg text-slate-500 hover:bg-slate-100 hover:text-brand-600 transition-colors"
                title="Change Company & Branch"
              >
                <Edit3 size={18} />
              </button>
            )}
            
            {/* Notification Bell */}
            <button className="relative p-2 rounded-lg text-slate-500 hover:bg-slate-100">
              <Bell size={18} />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-red-500 rounded-full" />
            </button>
          </div>
        </header>

        {/* Trial banner */}
        <TrialBanner />
        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>

      {/* Change Company/Branch Modal */}
      <ChangeCompanyBranchModal 
        isOpen={changeCompanyModalOpen} 
        onClose={() => setChangeCompanyModalOpen(false)} 
      />
    </div>
  )
}
