import api from './client'

export interface LeaveMaster {
  leave_master_id: number
  tenant_id:       number
  leave_type:      string
  entitled:        number
  calendar_year:   number
  calculation:     string
  created_at:      string
  updated_at:      string
}

export interface LeaveMasterPayload {
  leave_type:    string
  entitled:      number
  calendar_year: number
  calculation:   string
}

export interface PaginatedLeaveMasters {
  items:       LeaveMaster[]
  total:       number
  page:        number
  page_size:   number
  total_pages: number
}

export const LEAVE_TYPES = [
  'Annual', 'Sick', 'Casual', 'Maternity', 'Paternity',
  'Emergency', 'Unpaid', 'Compensatory', 'Other',
]

export const CALCULATIONS = ['MONTHLY', 'YEARLY', 'QUARTERLY']

export const leaveMasterApi = {
  list: (params?: { page?: number; page_size?: number; calendar_year?: number }) =>
    api.get<PaginatedLeaveMasters>('/leave-master', { params }).then(r => r.data),

  create: (data: LeaveMasterPayload) =>
    api.post<LeaveMaster>('/leave-master', data).then(r => r.data),

  update: (id: number, data: Partial<LeaveMasterPayload>) =>
    api.patch<LeaveMaster>(`/leave-master/${id}`, data).then(r => r.data),

  delete: (id: number) =>
    api.delete(`/leave-master/${id}`).then(r => r.data),
}
