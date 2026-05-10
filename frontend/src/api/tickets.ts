import api from './client'

export interface TicketComment {
  comment_id: number
  ticket_id: number
  user_id: number
  comment_text: string
  is_internal: boolean
  created_at: string
  updated_at: string
}

export interface Ticket {
  ticket_id: number
  ticket_number: string
  title: string
  description: string
  category: string
  priority: string
  status: string
  resolution?: string
  created_at: string
  updated_at: string
  resolved_at?: string
  closed_at?: string
  assigned_to_user_id?: number
  raised_by_user_id: number
  resolved_by_user_id?: number
}

export interface TicketDetail extends Ticket {
  comments: TicketComment[]
}

export interface TicketCreatePayload {
  title: string
  description: string
  category: string
  priority?: string
  tags?: string[]
}

export interface TicketUpdatePayload {
  title?: string
  description?: string
  category?: string
  priority?: string
  status?: string
  assigned_to_user_id?: number
  resolution?: string
  tags?: string[]
}

export interface TicketCommentPayload {
  comment_text: string
  is_internal?: boolean
}

export interface PaginatedTickets {
  items: Ticket[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface TicketStats {
  total: number
  open: number
  in_progress: number
  resolved: number
  urgent: number
}

export const ticketsApi = {
  // Create ticket
  createTicket: async (payload: TicketCreatePayload): Promise<Ticket> => {
    const response = await api.post('/tickets', payload)
    return response.data
  },

  // List tickets
  listTickets: async (
    page: number = 1,
    pageSize: number = 20,
    filters?: {
      status?: string
      priority?: string
      category?: string
      search?: string
    }
  ): Promise<PaginatedTickets> => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      ...(filters?.status && { status: filters.status }),
      ...(filters?.priority && { priority: filters.priority }),
      ...(filters?.category && { category: filters.category }),
      ...(filters?.search && { search: filters.search }),
    })
    const response = await api.get(`/tickets?${params}`)
    return response.data
  },

  // Get ticket stats
  getStats: async (): Promise<TicketStats> => {
    const response = await api.get('/tickets/stats')
    return response.data
  },

  // Get ticket detail
  getTicket: async (ticketId: number): Promise<TicketDetail> => {
    const response = await api.get(`/tickets/${ticketId}`)
    return response.data
  },

  // Update ticket
  updateTicket: async (ticketId: number, payload: TicketUpdatePayload): Promise<Ticket> => {
    const response = await api.patch(`/tickets/${ticketId}`, payload)
    return response.data
  },

  // Close ticket
  closeTicket: async (ticketId: number, resolution: string): Promise<Ticket> => {
    const response = await api.post(`/tickets/${ticketId}/close`, { resolution })
    return response.data
  },

  // Add comment
  addComment: async (ticketId: number, payload: TicketCommentPayload): Promise<TicketComment> => {
    const response = await api.post(`/tickets/${ticketId}/comments`, payload)
    return response.data
  },

  // Get comments
  getComments: async (ticketId: number): Promise<TicketComment[]> => {
    const response = await api.get(`/tickets/${ticketId}/comments`)
    return response.data
  },
}
