import { useQuery } from '@tanstack/react-query'
import { FileText, AlertCircle, Clock, CheckCircle, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { companiesApi } from '@/api/companies'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import clsx from 'clsx'

const STATUS_COLORS: Record<string, string> = {
  OPEN: 'bg-yellow-50 border-yellow-200',
  IN_PROGRESS: 'bg-blue-50 border-blue-200',
  COMPLETED: 'bg-green-50 border-green-200',
  REJECTED: 'bg-red-50 border-red-200',
}

const STATUS_ICONS: Record<string, any> = {
  OPEN: AlertCircle,
  IN_PROGRESS: Clock,
  COMPLETED: CheckCircle,
  REJECTED: AlertCircle,
}

const STATUS_TEXT_COLORS: Record<string, string> = {
  OPEN: 'text-yellow-700',
  IN_PROGRESS: 'text-blue-700',
  COMPLETED: 'text-green-700',
  REJECTED: 'text-red-700',
}

export default function DocumentRequestsWidget() {
  const { company } = useAuthStoreV2()

  const { data: tickets = [], isLoading } = useQuery({
    queryKey: ['documentRequests', company?.company_id, 'widget'],
    queryFn: () => companiesApi.listDocumentRequests(company!.company_id),
    enabled: !!company?.company_id,
  })

  const openTickets = tickets.filter((t) => t.status === 'OPEN')
  const inProgressTickets = tickets.filter((t) => t.status === 'IN_PROGRESS')

  if (!company) return null

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FileText className="text-brand-600" size={24} />
          <h3 className="text-lg font-bold text-slate-900">Document Requests</h3>
        </div>
        <Link
          to="/owner/document-requests"
          className="text-brand-600 hover:text-brand-700 text-sm font-medium flex items-center gap-1"
        >
          View All <ArrowRight size={14} />
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 bg-slate-100 rounded animate-pulse" />
          ))}
        </div>
      ) : tickets.length === 0 ? (
        <div className="text-center py-8">
          <FileText className="mx-auto text-slate-300 mb-2" size={32} />
          <p className="text-slate-500 text-sm">No document requests yet</p>
        </div>
      ) : (
        <div className="space-y-2">
          {/* Open Tickets */}
          {openTickets.length > 0 && (
            <div className="mb-4">
              <p className="text-xs font-semibold text-slate-600 uppercase mb-2">
                Open ({openTickets.length})
              </p>
              <div className="space-y-2">
                {openTickets.slice(0, 3).map((ticket) => (
                  <div
                    key={ticket.ticket_id}
                    className={clsx(
                      'p-3 rounded-lg border-2 flex items-start gap-3',
                      STATUS_COLORS[ticket.status]
                    )}
                  >
                    <AlertCircle className={clsx('text-yellow-600 flex-shrink-0 mt-0.5')} size={16} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900">
                        Ticket #{ticket.ticket_id.slice(0, 8)}
                      </p>
                      <p className="text-xs text-slate-600 mt-1">
                        {ticket.document_types.length} document{ticket.document_types.length !== 1 ? 's' : ''} requested
                      </p>
                    </div>
                    <span
                      className={clsx(
                        'text-xs font-semibold px-2 py-1 rounded whitespace-nowrap',
                        ticket.priority === 'URGENT'
                          ? 'bg-red-100 text-red-700'
                          : ticket.priority === 'NORMAL'
                            ? 'bg-slate-100 text-slate-700'
                            : 'bg-slate-50 text-slate-600'
                      )}
                    >
                      {ticket.priority}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* In Progress Tickets */}
          {inProgressTickets.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-600 uppercase mb-2">
                In Progress ({inProgressTickets.length})
              </p>
              <div className="space-y-2">
                {inProgressTickets.slice(0, 2).map((ticket) => (
                  <div
                    key={ticket.ticket_id}
                    className={clsx(
                      'p-3 rounded-lg border-2 flex items-start gap-3',
                      STATUS_COLORS[ticket.status]
                    )}
                  >
                    <Clock className="text-blue-600 flex-shrink-0 mt-0.5" size={16} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900">
                        Ticket #{ticket.ticket_id.slice(0, 8)}
                      </p>
                      <p className="text-xs text-slate-600 mt-1">
                        {ticket.document_types.length} document{ticket.document_types.length !== 1 ? 's' : ''} being processed
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Summary Stats */}
          {tickets.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-200 grid grid-cols-3 gap-2">
              <div className="text-center">
                <p className="text-lg font-bold text-yellow-600">{openTickets.length}</p>
                <p className="text-xs text-slate-600">Open</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-bold text-blue-600">{inProgressTickets.length}</p>
                <p className="text-xs text-slate-600">In Progress</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-bold text-green-600">
                  {tickets.filter((t) => t.status === 'COMPLETED').length}
                </p>
                <p className="text-xs text-slate-600">Completed</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
