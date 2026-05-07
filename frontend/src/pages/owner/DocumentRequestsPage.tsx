import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Plus, Search, CheckCircle, Clock, AlertCircle, Loader2, RefreshCw,
  MoreVertical, User, FileText, Calendar, MessageSquare,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { companiesApi } from '@/api/companies'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import clsx from 'clsx'

const STATUS_COLORS: Record<string, string> = {
  OPEN: 'badge-yellow',
  IN_PROGRESS: 'badge-blue',
  COMPLETED: 'badge-green',
  REJECTED: 'badge-red',
}

const PRIORITY_COLORS: Record<string, string> = {
  URGENT: 'text-red-600 bg-red-50',
  NORMAL: 'text-slate-600 bg-slate-50',
  LOW: 'text-slate-400 bg-slate-50',
}

const DOCUMENT_TYPES: Record<string, string> = {
  PAN: 'PAN Certificate',
  TAN: 'TAN Certificate',
  COMPANY_ESTABLISHED_DATE: 'Company Established Date',
  GST: 'GST Certificate',
  CIN: 'CIN Certificate',
  UDYAM: 'Udyam Registration',
  IEC: 'IEC Code',
  OTHER: 'Other Document',
}

function TicketRow({
  ticket,
  onStatusChange,
}: {
  ticket: any
  onStatusChange: (ticketId: string, status: string) => void
}) {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <tr className="hover:bg-slate-50 transition-colors">
      <td className="table-td">
        <div>
          <div className="font-medium text-slate-900 text-sm">Ticket #{ticket.ticket_id.slice(0, 8)}</div>
          <div className="text-xs text-slate-500 mt-1">
            {new Date(ticket.created_at).toLocaleDateString('en-IN', {
              day: '2-digit',
              month: 'short',
              year: 'numeric',
            })}
          </div>
        </div>
      </td>
      <td className="table-td">
        <div className="space-y-1">
          {ticket.document_types.map((doc: string) => (
            <div key={doc} className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded w-fit">
              {DOCUMENT_TYPES[doc] || doc}
            </div>
          ))}
        </div>
      </td>
      <td className="table-td">
        <span className={clsx('text-xs font-medium px-2 py-1 rounded', PRIORITY_COLORS[ticket.priority])}>
          {ticket.priority}
        </span>
      </td>
      <td className="table-td">
        <span className={STATUS_COLORS[ticket.status] || 'badge-gray'}>
          {ticket.status.charAt(0) + ticket.status.slice(1).toLowerCase()}
        </span>
      </td>
      <td className="table-td">
        {ticket.description && (
          <div className="text-xs text-slate-600 line-clamp-2">{ticket.description}</div>
        )}
      </td>
      <td className="table-td">
        <div className="relative">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            <MoreVertical size={15} />
          </button>
          {menuOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 top-8 z-20 bg-white border border-slate-200 rounded-xl shadow-lg w-48 py-1">
                {ticket.status === 'OPEN' && (
                  <button
                    onClick={() => {
                      onStatusChange(ticket.ticket_id, 'IN_PROGRESS')
                      setMenuOpen(false)
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50"
                  >
                    <Clock size={13} /> Mark In Progress
                  </button>
                )}
                {ticket.status !== 'COMPLETED' && ticket.status !== 'REJECTED' && (
                  <button
                    onClick={() => {
                      onStatusChange(ticket.ticket_id, 'COMPLETED')
                      setMenuOpen(false)
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-green-600 hover:bg-green-50"
                  >
                    <CheckCircle size={13} /> Mark Completed
                  </button>
                )}
                {ticket.status !== 'REJECTED' && (
                  <button
                    onClick={() => {
                      onStatusChange(ticket.ticket_id, 'REJECTED')
                      setMenuOpen(false)
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <AlertCircle size={13} /> Reject
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </td>
    </tr>
  )
}

export default function DocumentRequestsPage() {
  const qc = useQueryClient()
  const { company } = useAuthStoreV2()
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [search, setSearch] = useState('')

  if (!company) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="card p-8 text-center">
          <p className="text-slate-600">Please select a company first</p>
        </div>
      </div>
    )
  }

  const { data: tickets = [], isLoading, isFetching } = useQuery({
    queryKey: ['documentRequests', company.company_id, statusFilter],
    queryFn: () => companiesApi.listDocumentRequests(company.company_id, statusFilter || undefined),
    enabled: !!company.company_id,
  })

  const updateTicket = useMutation({
    mutationFn: (data: { ticketId: string; status: string }) =>
      companiesApi.updateDocumentRequest(company.company_id, data.ticketId, { status: data.status }),
    onSuccess: () => {
      toast.success('Ticket updated successfully!')
      qc.invalidateQueries({ queryKey: ['documentRequests', company.company_id, statusFilter] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update ticket')
    },
  })

  const filteredTickets = tickets.filter(
    (t) =>
      search === '' ||
      t.ticket_id.toLowerCase().includes(search.toLowerCase()) ||
      t.document_types.some((d: string) => d.toLowerCase().includes(search.toLowerCase()))
  )

  const stats = {
    total: tickets.length,
    open: tickets.filter((t) => t.status === 'OPEN').length,
    inProgress: tickets.filter((t) => t.status === 'IN_PROGRESS').length,
    completed: tickets.filter((t) => t.status === 'COMPLETED').length,
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900">Document Requests</h1>
        <p className="text-sm text-slate-500 mt-0.5">Manage client document requests for {company.company_name}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div className="card p-4">
          <div className="text-2xl font-bold text-slate-900">{stats.total}</div>
          <div className="text-xs text-slate-500 mt-1">Total Requests</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-bold text-yellow-600">{stats.open}</div>
          <div className="text-xs text-slate-500 mt-1">Open</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-bold text-blue-600">{stats.inProgress}</div>
          <div className="text-xs text-slate-500 mt-1">In Progress</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
          <div className="text-xs text-slate-500 mt-1">Completed</div>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4 mb-5">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by ticket ID or document type..."
              className="input pl-9"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input"
          >
            <option value="">All Status</option>
            <option value="OPEN">Open</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
            <option value="REJECTED">Rejected</option>
          </select>
          <button
            onClick={() => qc.invalidateQueries({ queryKey: ['documentRequests', company.company_id, statusFilter] })}
            className={clsx('btn-ghost', isFetching && 'opacity-50')}
          >
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
                <th className="table-th">Ticket</th>
                <th className="table-th">Documents Requested</th>
                <th className="table-th">Priority</th>
                <th className="table-th">Status</th>
                <th className="table-th">Description</th>
                <th className="table-th w-12"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="py-16 text-center">
                    <Loader2 size={24} className="animate-spin text-slate-400 mx-auto" />
                  </td>
                </tr>
              ) : filteredTickets.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-16 text-center">
                    <div className="text-slate-400">
                      <FileText size={32} className="mx-auto mb-3 opacity-40" />
                      <p className="text-sm font-medium">No document requests found</p>
                      <p className="text-xs mt-1">Clients will see a form to request documents</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredTickets.map((ticket) => (
                  <TicketRow
                    key={ticket.ticket_id}
                    ticket={ticket}
                    onStatusChange={(ticketId, status) => updateTicket.mutate({ ticketId, status })}
                  />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
