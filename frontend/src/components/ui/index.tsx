import { ReactNode } from 'react'
import { X, TrendingUp, TrendingDown } from 'lucide-react'
import clsx from 'clsx'

// ── StatusBadge ───────────────────────────────────────────────────────────────
const STATUS_COLORS: Record<string, string> = {
  // Customer
  ACTIVE:    'badge-green',
  INACTIVE:  'badge-gray',
  PROSPECT:  'badge-blue',
  CHURNED:   'badge-red',
  // KYC
  VERIFIED:  'badge-green',
  PENDING:   'badge-yellow',
  EXPIRED:   'badge-red',
  REJECTED:  'badge-red',
  // Enquiry
  NEW:           'badge-blue',
  IN_PROGRESS:   'badge-yellow',
  PROPOSAL_SENT: 'badge-blue',
  WON:           'badge-green',
  LOST:          'badge-red',
  DEFERRED:      'badge-gray',
  // Risk
  LOW:    'badge-green',
  MEDIUM: 'badge-yellow',
  HIGH:   'badge-red',
  // User
  INVITED:   'badge-yellow',
  SUSPENDED: 'badge-red',
}

export function StatusBadge({ status, label }: { status: string; label?: string }) {
  return (
    <span className={STATUS_COLORS[status] || 'badge-gray'}>
      {label || status.charAt(0) + status.slice(1).toLowerCase().replace('_', ' ')}
    </span>
  )
}

// ── StatCard ──────────────────────────────────────────────────────────────────
interface StatCardProps {
  label:   string
  value:   number | string
  icon:    ReactNode
  color:   string
  bg:      string
  trend?:  number   // percentage change
}

export function StatCard({ label, value, icon, color, bg, trend }: StatCardProps) {
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-500 mb-1">{label}</p>
          <p className="text-2xl font-bold text-slate-900">{value}</p>
        </div>
        <div className={`w-10 h-10 ${bg} rounded-xl flex items-center justify-center flex-shrink-0`}>
          <span className={color}>{icon}</span>
        </div>
      </div>
      {trend !== undefined && (
        <div className={clsx('flex items-center gap-1 mt-2 text-xs font-medium',
          trend >= 0 ? 'text-green-600' : 'text-red-600')}>
          {trend >= 0
            ? <TrendingUp size={12} />
            : <TrendingDown size={12} />
          }
          {Math.abs(trend)}% this month
        </div>
      )}
    </div>
  )
}

// ── Drawer ────────────────────────────────────────────────────────────────────
interface DrawerProps {
  open:     boolean
  onClose:  () => void
  title:    string
  subtitle?: string
  children: ReactNode
  width?:   'sm' | 'md' | 'lg' | 'xl'
}

const DRAWER_WIDTHS = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
}

export function Drawer({ open, onClose, title, subtitle, children, width = 'lg' }: DrawerProps) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <div className={clsx(
        'relative bg-white shadow-2xl flex flex-col w-full h-full',
        DRAWER_WIDTHS[width]
      )}>
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 flex-shrink-0">
          <div>
            <h2 className="text-lg font-bold text-slate-900">{title}</h2>
            {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
          </div>
          <button onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
            <X size={18} />
          </button>
        </div>
        {/* Body */}
        <div className="flex-1 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  )
}

// ── Modal ─────────────────────────────────────────────────────────────────────
interface ModalProps {
  open:     boolean
  onClose:  () => void
  title:    string
  subtitle?: string
  children: ReactNode
  size?:    'sm' | 'md' | 'lg'
}

const MODAL_SIZES = { sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl' }

export function Modal({ open, onClose, title, subtitle, children, size = 'md' }: ModalProps) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className={clsx(
        'relative bg-white rounded-2xl shadow-2xl w-full max-h-[90vh] flex flex-col',
        MODAL_SIZES[size]
      )}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 flex-shrink-0">
          <div>
            <h2 className="text-lg font-bold text-slate-900">{title}</h2>
            {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
          </div>
          <button onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100">
            <X size={16} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">{children}</div>
      </div>
    </div>
  )
}

// ── EmptyState ────────────────────────────────────────────────────────────────
export function EmptyState({
  icon, title, description, action
}: {
  icon: ReactNode; title: string; description?: string; action?: ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center px-4">
      <div className="w-14 h-14 bg-slate-100 rounded-2xl flex items-center justify-center mb-4 text-slate-400">
        {icon}
      </div>
      <h3 className="text-base font-semibold text-slate-700 mb-1">{title}</h3>
      {description && <p className="text-sm text-slate-500 max-w-xs mb-4">{description}</p>}
      {action}
    </div>
  )
}

// ── FormField ─────────────────────────────────────────────────────────────────
export function FormField({
  label, error, required, children, hint
}: {
  label: string; error?: string; required?: boolean; children: ReactNode; hint?: string
}) {
  return (
    <div>
      <label className="label">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      {children}
      {hint && !error && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  )
}

// ── SectionHeader ─────────────────────────────────────────────────────────────
export function SectionHeader({ title, action }: { title: string; action?: ReactNode }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider">{title}</h3>
      {action}
    </div>
  )
}

// ── Tabs ──────────────────────────────────────────────────────────────────────
export function Tabs({
  tabs, active, onChange
}: {
  tabs: { key: string; label: string; count?: number }[]
  active: string
  onChange: (key: string) => void
}) {
  return (
    <div className="flex gap-1 bg-slate-100 p-1 rounded-xl">
      {tabs.map(tab => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={clsx(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
            active === tab.key
              ? 'bg-white text-slate-900 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
          )}
        >
          {tab.label}
          {tab.count !== undefined && (
            <span className={clsx(
              'text-xs px-1.5 py-0.5 rounded-full',
              active === tab.key ? 'bg-brand-100 text-brand-700' : 'bg-slate-200 text-slate-500'
            )}>
              {tab.count}
            </span>
          )}
        </button>
      ))}
    </div>
  )
}
