import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Plus, Search, Users, UserCheck, ShieldAlert, Filter,
  ChevronLeft, ChevronRight, RefreshCw, Download,
} from 'lucide-react'
import { customersApi } from '@/api/customers'
import { StatCard, StatusBadge, EmptyState, Tabs } from '@/components/ui'
import CustomerFormModal from '@/pages/customers/CustomerFormModal'
import CustomerDrawer from '@/pages/customers/CustomerDrawer'
import type { Customer } from '@/types/customer'
import clsx from 'clsx'

const TYPE_COLORS: Record<string, string> = {
  INDIVIDUAL: 'bg-blue-100 text-blue-700',
  COMPANY:    'bg-purple-100 text-purple-700',
  HUF:        'bg-orange-100 text-orange-700',
  TRUST:      'bg-green-100 text-green-700',
  LLP:        'bg-indigo-100 text-indigo-700',
  PARTNERSHIP:'bg-pink-100 text-pink-700',
  AOP:        'bg-teal-100 text-teal-700',
  BOI:        'bg-cyan-100 text-cyan-700',
}

function CustomerAvatar({ customer }: { customer: Customer }) {
  const initials = customer.display_name.slice(0, 2).toUpperCase()
  const colors = ['bg-brand-100 text-brand-700', 'bg-purple-100 text-purple-700',
    'bg-green-100 text-green-700', 'bg-orange-100 text-orange-700']
  const color = colors[customer.customer_id % colors.length]
  return (
    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${color}`}>
      {initials}
    </div>
  )
}

export default function ManagerClientsPage() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editCustomer, setEditCustomer] = useState<Customer | null>(null)
  const [viewCustomerId, setViewCustomerId] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [kycFilter, setKycFilter] = useState('')
  const [page, setPage] = useState(1)

  const { data: stats } = useQuery({
    queryKey: ['customer-stats'],
    queryFn: customersApi.stats,
  })

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['customers', page, search, statusFilter, typeFilter, kycFilter],
    queryFn: () => customersApi.list({
      page, page_size: 15,
      search: search || undefined,
      status: statusFilter || undefined,
      customer_type: typeFilter || undefined,
      kyc_status: kycFilter || undefined,
    }),
    placeholderData: prev => prev,
  })

  const customers = data?.items || []
  const total = data?.total || 0
  const totalPages = data?.total_pages || 1

  const openEdit = (c: Customer) => {
    setEditCustomer(c)
    setShowForm(true)
    setViewCustomerId(null)
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Clients</h1>
          <p className="text-sm text-slate-500 mt-0.5">{total} client{total !== 1 ? 's' : ''} total</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary btn-sm">
            <Download size={14} /> Export
          </button>
          <button onClick={() => { setEditCustomer(null); setShowForm(true) }} className="btn-primary">
            <Plus size={15} /> Add Client
          </button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total Clients"   value={stats.total}       icon={<Users size={18} />}       color="text-blue-600"   bg="bg-blue-50" />
          <StatCard label="Active"          value={stats.active}      icon={<UserCheck size={18} />}   color="text-green-600"  bg="bg-green-50" />
          <StatCard label="KYC Pending"     value={stats.kyc_pending} icon={<ShieldAlert size={18} />} color="text-orange-600" bg="bg-orange-50" />
          <StatCard label="Companies"       value={stats.by_type?.COMPANY || 0} icon={<Filter size={18} />} color="text-purple-600" bg="bg-purple-50" />
        </div>
      )}

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-wrap gap-3">
          <div className="relative flex-1 min-w-48">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1) }}
              placeholder="Search by name, PAN, GSTIN, phone..."
              className="input pl-9"
            />
          </div>
          <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1) }} className="input w-36">
            <option value="">All Status</option>
            {['ACTIVE', 'INACTIVE', 'PROSPECT', 'CHURNED'].map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <select value={typeFilter} onChange={e => { setTypeFilter(e.target.value); setPage(1) }} className="input w-36">
            <option value="">All Types</option>
            {['INDIVIDUAL', 'COMPANY', 'HUF', 'LLP', 'PARTNERSHIP', 'TRUST'].map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <select value={kycFilter} onChange={e => { setKycFilter(e.target.value); setPage(1) }} className="input w-36">
            <option value="">KYC Status</option>
            {['PENDING', 'VERIFIED', 'EXPIRED', 'REJECTED'].map(k => (
              <option key={k} value={k}>{k}</option>
            ))}
          </select>
          <button onClick={() => qc.invalidateQueries({ queryKey: ['customers'] })}
            className={clsx('btn-ghost', isFetching && 'opacity-50')}>
            <RefreshCw size={15} className={isFetching ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="table-th">Client</th>
                <th className="table-th">Type</th>
                <th className="table-th">PAN / GSTIN</th>
                <th className="table-th">Contact</th>
                <th className="table-th">KYC</th>
                <th className="table-th">Status</th>
                <th className="table-th">Since</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr><td colSpan={7} className="py-16 text-center">
                  <div className="animate-spin w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full mx-auto" />
                </td></tr>
              ) : customers.length === 0 ? (
                <tr><td colSpan={7}>
                  <EmptyState
                    icon={<Users size={24} />}
                    title="No clients found"
                    description="Add your first client to get started"
                    action={
                      <button onClick={() => { setEditCustomer(null); setShowForm(true) }} className="btn-primary btn-sm">
                        <Plus size={13} /> Add Client
                      </button>
                    }
                  />
                </td></tr>
              ) : (
                customers.map(c => (
                  <tr
                    key={c.customer_id}
                    onClick={() => setViewCustomerId(c.customer_id)}
                    className="hover:bg-blue-50/40 cursor-pointer transition-colors"
                  >
                    <td className="table-td">
                      <div className="flex items-center gap-3">
                        <CustomerAvatar customer={c} />
                        <div>
                          <p className="font-medium text-slate-900 text-sm">{c.display_name}</p>
                          <p className="text-xs text-slate-400">{c.customer_code}</p>
                        </div>
                      </div>
                    </td>
                    <td className="table-td">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${TYPE_COLORS[c.customer_type] || 'bg-slate-100 text-slate-600'}`}>
                        {c.customer_type}
                      </span>
                    </td>
                    <td className="table-td">
                      <div className="space-y-0.5">
                        {c.pan && <p className="text-xs font-mono text-slate-700">{c.pan}</p>}
                        {c.gstin && <p className="text-xs font-mono text-slate-500">{c.gstin}</p>}
                        {!c.pan && !c.gstin && <span className="text-slate-300 text-xs">—</span>}
                      </div>
                    </td>
                    <td className="table-td">
                      <p className="text-sm text-slate-700">{c.phone}</p>
                      {c.email && <p className="text-xs text-slate-400">{c.email}</p>}
                    </td>
                    <td className="table-td">
                      <StatusBadge status={c.kyc_status} />
                    </td>
                    <td className="table-td">
                      <StatusBadge status={c.status} />
                    </td>
                    <td className="table-td text-slate-500 text-xs">
                      {c.onboarded_at
                        ? new Date(c.onboarded_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
                        : new Date(c.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
                      }
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="border-t border-slate-100 px-4 py-3 flex items-center justify-between">
            <p className="text-sm text-slate-500">
              Showing {((page - 1) * 15) + 1}–{Math.min(page * 15, total)} of {total}
            </p>
            <div className="flex items-center gap-1">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="btn-ghost btn-sm">
                <ChevronLeft size={14} />
              </button>
              <span className="text-sm text-slate-600 px-2">{page} / {totalPages}</span>
              <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="btn-ghost btn-sm">
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modals & Drawers */}
      <CustomerFormModal
        open={showForm}
        onClose={() => { setShowForm(false); setEditCustomer(null) }}
        customer={editCustomer}
      />
      <CustomerDrawer
        customerId={viewCustomerId}
        onClose={() => setViewCustomerId(null)}
        onEdit={openEdit}
      />
    </div>
  )
}
