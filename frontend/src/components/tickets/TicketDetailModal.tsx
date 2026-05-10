import { useState, useEffect } from 'react'
import { X, MessageSquare, Send } from 'lucide-react'
import toast from 'react-hot-toast'
import { ticketsApi, Ticket, TicketDetail, TicketComment } from '@/api/tickets'

interface TicketDetailModalProps {
  isOpen: boolean
  onClose: () => void
  ticket: Ticket
  onUpdated: () => void
  isManager?: boolean
}

const STATUS_COLORS = {
  OPEN: 'bg-red-100 text-red-800',
  IN_PROGRESS: 'bg-blue-100 text-blue-800',
  RESOLVED: 'bg-green-100 text-green-800',
  CLOSED: 'bg-gray-100 text-gray-800',
  REOPENED: 'bg-orange-100 text-orange-800',
}

const PRIORITY_COLORS = {
  LOW: 'bg-blue-100 text-blue-800',
  MEDIUM: 'bg-yellow-100 text-yellow-800',
  HIGH: 'bg-orange-100 text-orange-800',
  URGENT: 'bg-red-100 text-red-800',
}

export function TicketDetailModal({ isOpen, onClose, ticket, onUpdated, isManager }: TicketDetailModalProps) {
  const [ticketDetail, setTicketDetail] = useState<TicketDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [commentText, setCommentText] = useState('')
  const [submittingComment, setSubmittingComment] = useState(false)
  const [updatingStatus, setUpdatingStatus] = useState(false)
  const [newStatus, setNewStatus] = useState(ticket.status)

  useEffect(() => {
    if (isOpen) {
      fetchTicketDetail()
    }
  }, [isOpen, ticket.ticket_id])

  const fetchTicketDetail = async () => {
    try {
      setLoading(true)
      const detail = await ticketsApi.getTicket(ticket.ticket_id)
      setTicketDetail(detail)
      setNewStatus(detail.status)
    } catch (error) {
      toast.error('Failed to load ticket details')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!commentText.trim()) {
      toast.error('Please enter a comment')
      return
    }

    try {
      setSubmittingComment(true)
      await ticketsApi.addComment(ticket.ticket_id, {
        comment_text: commentText,
        is_internal: false,
      })
      toast.success('Comment added')
      setCommentText('')
      await fetchTicketDetail()
    } catch (error) {
      toast.error('Failed to add comment')
      console.error(error)
    } finally {
      setSubmittingComment(false)
    }
  }

  const handleStatusChange = async () => {
    if (newStatus === ticket.status) return

    try {
      setUpdatingStatus(true)
      await ticketsApi.updateTicket(ticket.ticket_id, { status: newStatus })
      toast.success('Ticket status updated')
      await fetchTicketDetail()
      onUpdated()
    } catch (error) {
      toast.error('Failed to update ticket status')
      setNewStatus(ticket.status)
      console.error(error)
    } finally {
      setUpdatingStatus(false)
    }
  }

  if (!isOpen || !ticketDetail) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200 sticky top-0 bg-white">
          <div>
            <h2 className="text-xl font-bold text-slate-900">{ticketDetail.ticket_number}</h2>
            <p className="text-sm text-slate-600 mt-1">{ticketDetail.title}</p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600"
          >
            <X size={24} />
          </button>
        </div>

        {loading ? (
          <div className="p-6 text-center text-slate-600">Loading...</div>
        ) : (
          <div className="p-6 space-y-6">
            {/* Ticket Info */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-xs text-slate-600 uppercase font-semibold">Priority</div>
                <span className={`inline-block px-2 py-1 rounded text-xs font-medium mt-1 ${PRIORITY_COLORS[ticketDetail.priority as keyof typeof PRIORITY_COLORS]}`}>
                  {ticketDetail.priority}
                </span>
              </div>
              <div>
                <div className="text-xs text-slate-600 uppercase font-semibold">Category</div>
                <div className="text-sm text-slate-900 mt-1">{ticketDetail.category}</div>
              </div>
              <div>
                <div className="text-xs text-slate-600 uppercase font-semibold">Created</div>
                <div className="text-sm text-slate-900 mt-1">
                  {new Date(ticketDetail.created_at).toLocaleDateString()}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-600 uppercase font-semibold">Status</div>
                {isManager ? (
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    onBlur={handleStatusChange}
                    disabled={updatingStatus}
                    className={`mt-1 px-2 py-1 rounded text-xs font-medium border-0 focus:outline-none focus:ring-2 focus:ring-brand-500 ${STATUS_COLORS[newStatus as keyof typeof STATUS_COLORS]}`}
                  >
                    <option value="OPEN">Open</option>
                    <option value="IN_PROGRESS">In Progress</option>
                    <option value="RESOLVED">Resolved</option>
                    <option value="CLOSED">Closed</option>
                  </select>
                ) : (
                  <span className={`inline-block px-2 py-1 rounded text-xs font-medium mt-1 ${STATUS_COLORS[ticketDetail.status as keyof typeof STATUS_COLORS]}`}>
                    {ticketDetail.status}
                  </span>
                )}
              </div>
            </div>

            {/* Description */}
            <div>
              <h3 className="font-semibold text-slate-900 mb-2">Description</h3>
              <p className="text-slate-700 whitespace-pre-wrap">{ticketDetail.description}</p>
            </div>

            {/* Resolution (if resolved) */}
            {ticketDetail.resolution && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-semibold text-green-900 mb-2">Resolution</h3>
                <p className="text-green-800 whitespace-pre-wrap">{ticketDetail.resolution}</p>
              </div>
            )}

            {/* Comments */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <MessageSquare size={18} className="text-slate-600" />
                <h3 className="font-semibold text-slate-900">Comments ({ticketDetail.comments.length})</h3>
              </div>

              {/* Comments List */}
              <div className="space-y-3 mb-4 max-h-64 overflow-y-auto">
                {ticketDetail.comments.length === 0 ? (
                  <p className="text-sm text-slate-600">No comments yet</p>
                ) : (
                  ticketDetail.comments.map((comment) => (
                    <div key={comment.comment_id} className="bg-slate-50 rounded-lg p-3">
                      <div className="flex items-start justify-between mb-1">
                        <div className="text-sm font-medium text-slate-900">User #{comment.user_id}</div>
                        <div className="text-xs text-slate-500">
                          {new Date(comment.created_at).toLocaleString()}
                        </div>
                      </div>
                      <p className="text-sm text-slate-700">{comment.comment_text}</p>
                      {comment.is_internal && (
                        <div className="text-xs text-orange-600 mt-1">Internal Note</div>
                      )}
                    </div>
                  ))
                )}
              </div>

              {/* Add Comment Form */}
              <form onSubmit={handleAddComment} className="space-y-2">
                <textarea
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  placeholder="Add a comment..."
                  rows={3}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
                />
                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={submittingComment}
                    className="flex items-center gap-2 px-3 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 text-sm"
                  >
                    <Send size={14} />
                    {submittingComment ? 'Sending...' : 'Send Comment'}
                  </button>
                </div>
              </form>
            </div>

            {/* Close Button */}
            <div className="flex justify-end pt-4 border-t border-slate-200">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
