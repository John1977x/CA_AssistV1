import { useState, useEffect } from 'react'
import { AlertCircle, Clock, CheckCircle, Filter } from 'lucide-react'
import toast from 'react-hot-toast'
import { ticketsApi, Ticket, TicketStats } from '@/api/tickets'
import { TicketDetailModal } from '@/components/tickets/TicketDetailModal'

const PRIORITY_COLORS = {
  LOW: 'bg-blue-100 text-blue-800',
  MEDIUM: 'bg-yellow-100 text-yellow-800',
  HIGH: 'bg-orange-100 text-orange-800',
  URGENT: 'bg-red-100 text-red-800',
}

const STATUS_COLORS = {
  OPEN: 'bg-red-100 text-red-800',
  IN_PROGRESS: 'bg-blue-100 text-blue-800',
  RESOLVED: 'bg-green-100 text-green-800',
  CLOSED: 'bg-gray-100 text-gray-800',
  REOPENED: 'bg-orange-100 text-orange-800',
}

export default function OwnerTicketsPage() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [stats, setStats] = useState<TicketStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [priorityFilter, setPriorityFilter] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null)
  const [detailModalOpen, setDetailModalOpen] = useState(false)

  const fetchTickets = async () => {
    try {
      setLoading(true)
      const data = await ticketsApi.listTickets(page, 20, {
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
        search: searchQuery || undefined,
      })
      setTickets(data.items)
      setTotalPages(data.total_pages)
    } catch (error) {
      toast.error('Failed to load tickets')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const data = await ticketsApi.getStats()
      setStats(data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  useEffect(() => {
    fetchTickets()
  }, [page, statusFilter, priorityFilter, searchQuery])

  useEffect(() => {
    fetchStats()
  }, [])

  const handleTicketClick = (ticket: Ticket) => {
    setSelectedTicket(ticket)
    setDetailModalOpen(true)
  }

  const handleTicketUpdated = async () => {
    await fetchTickets()
    await fetchStats()
    setDetailModalOpen(false)
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">All Support Tickets</h1>
        <p className="text-slate-600 mt-1">Monitor all client support requests</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <div className="text-sm text-slate-600">Total Tickets</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{stats.total}</div>
          </div>
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <div className="flex items-center gap-2">
              <AlertCircle size={16} className="text-red-600" />
              <div className="text-sm text-slate-600">Open</div>
            </div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{stats.open}</div>
          </div>
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <div className="flex items-center gap-2">
              <Clock size={16} className="text-blue-600" />
              <div className="text-sm text-slate-600">In Progress</div>
            </div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{stats.in_progress}</div>
          </div>
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <div className="flex items-center gap-2">
              <CheckCircle size={16} className="text-green-600" />
              <div className="text-sm text-slate-600">Resolved</div>
            </div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{stats.resolved}</div>
          </div>
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <div className="flex items-center gap-2">
              <AlertCircle size={16} className="text-orange-600" />
              <div className="text-sm text-slate-600">Urgent</div>
            </div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{stats.urgent}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg border border-slate-200 p-4 space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter size={18} className="text-slate-600" />
          <h3 className="font-semibold text-slate-900">Filters</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Search tickets..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value)
              setPage(1)
            }}
            className="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setPage(1)
            }}
            className="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">All Status</option>
            <option value="OPEN">Open</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="RESOLVED">Resolved</option>
            <option value="CLOSED">Closed</option>
          </select>
          <select
            value={priorityFilter}
            onChange={(e) => {
              setPriorityFilter(e.target.value)
              setPage(1)
            }}
            className="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">All Priority</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="URGENT">Urgent</option>
          </select>
        </div>
      </div>

      {/* Tickets List */}
      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-600">Loading tickets...</div>
        ) : tickets.length === 0 ? (
          <div className="p-8 text-center text-slate-600">No tickets found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Ticket #</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Title</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Category</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Priority</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {tickets.map((ticket) => (
                  <tr
                    key={ticket.ticket_id}
                    onClick={() => handleTicketClick(ticket)}
                    className="hover:bg-slate-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 text-sm font-medium text-brand-600">{ticket.ticket_number}</td>
                    <td className="px-6 py-4 text-sm text-slate-900">{ticket.title}</td>
                    <td className="px-6 py-4 text-sm text-slate-600">{ticket.category}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${PRIORITY_COLORS[ticket.priority as keyof typeof PRIORITY_COLORS]}`}>
                        {ticket.priority}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${STATUS_COLORS[ticket.status as keyof typeof STATUS_COLORS]}`}>
                        {ticket.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-600">
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="px-3 py-2 border border-slate-300 rounded-lg disabled:opacity-50 hover:bg-slate-50"
          >
            Previous
          </button>
          <span className="text-sm text-slate-600">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            className="px-3 py-2 border border-slate-300 rounded-lg disabled:opacity-50 hover:bg-slate-50"
          >
            Next
          </button>
        </div>
      )}

      {/* Detail Modal */}
      {selectedTicket && (
        <TicketDetailModal
          isOpen={detailModalOpen}
          onClose={() => setDetailModalOpen(false)}
          ticket={selectedTicket}
          onUpdated={handleTicketUpdated}
          isManager={true}
        />
      )}
    </div>
  )
}
