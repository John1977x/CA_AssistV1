import api from './client'

export type InOutWard = 'INWARD' | 'OUTWARD'

export const DOC_TYPES = [
  'LETTER', 'NOTICE', 'CERTIFICATE', 'FORM',
  'APPLICATION', 'CONTRACT', 'REPORT', 'INVOICE', 'OTHER',
] as const

export interface RegisterEntry {
  register_id: number
  tenant_id: number
  in_out_ward: InOutWard
  doc_date: string
  doc_type: string
  doc_description: string
  client_id: number | null
  owner_id: number | null
  employee_id: number | null
  sent_date: string | null
  acknowledgement: string | null
  created_at: string
  updated_at: string
}

export interface RegisterStats {
  total: number
  inward: number
  outward: number
  pending_ack: number
}

export interface PaginatedRegisters {
  items: RegisterEntry[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface RegisterCreatePayload {
  in_out_ward: InOutWard
  doc_date: string
  doc_type: string
  doc_description: string
  client_id?: number | null
  owner_id?: number | null
  employee_id?: number | null
  sent_date?: string | null
  acknowledgement?: string | null
}

export const registerApi = {
  getStats: async (): Promise<RegisterStats> => {
    const res = await api.get('/register/stats')
    return res.data
  },

  list: async (params?: {
    page?: number
    page_size?: number
    in_out_ward?: InOutWard | ''
    doc_type?: string
    search?: string
  }): Promise<PaginatedRegisters> => {
    const p = new URLSearchParams()
    if (params?.page)         p.set('page',         String(params.page))
    if (params?.page_size)    p.set('page_size',     String(params.page_size))
    if (params?.in_out_ward)  p.set('in_out_ward',   params.in_out_ward)
    if (params?.doc_type)     p.set('doc_type',      params.doc_type)
    if (params?.search)       p.set('search',        params.search)
    const res = await api.get(`/register?${p}`)
    return res.data
  },

  create: async (payload: RegisterCreatePayload): Promise<RegisterEntry> => {
    const res = await api.post('/register', payload)
    return res.data
  },

  update: async (id: number, payload: Partial<RegisterCreatePayload>): Promise<RegisterEntry> => {
    const res = await api.patch(`/register/${id}`, payload)
    return res.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/register/${id}`)
  },
}
