import api from './client'

export interface LeaveApplication {
  leave_application_id: number
  tenant_id:            number
  employee_id:          number
  leave_type:           string
  leave_date:           string
  from_date:            string
  to_date:              string
  reason:               string | null
  attachment_url:       string | null
  approver_id:          number | null
  status:               string
  approval_notes:       string | null
  employee_name:        string | null
  approver_name:        string | null
  created_at:           string
  updated_at:           string
}

export interface LeaveApplicationPayload {
  leave_type:     string
  leave_date:     string
  from_date:      string
  to_date:        string
  reason?:        string
  attachment_url?: string
  approver_id?:   number | null
}

export interface LeaveApplicationUpdatePayload extends Partial<LeaveApplicationPayload> {
  status?:         string
  approval_notes?: string
}

export interface PaginatedLeaveApplications {
  items:       LeaveApplication[]
  total:       number
  page:        number
  page_size:   number
  total_pages: number
}

export interface Approver {
  user_id: number
  name:    string
}

export const LEAVE_STATUSES = ['PENDING', 'APPROVED', 'REJECTED'] as const

export const STATUS_COLORS: Record<string, string> = {
  PENDING:  'bg-yellow-100 text-yellow-700',
  APPROVED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
}

export const leaveApplicationApi = {
  list: (params?: { page?: number; page_size?: number; status?: string }) =>
    api.get<PaginatedLeaveApplications>('/leave-application', { params }).then(r => r.data),

  create: (data: LeaveApplicationPayload) =>
    api.post<LeaveApplication>('/leave-application', data).then(r => r.data),

  update: (id: number, data: LeaveApplicationUpdatePayload) =>
    api.patch<LeaveApplication>(`/leave-application/${id}`, data).then(r => r.data),

  delete: (id: number) =>
    api.delete(`/leave-application/${id}`).then(r => r.data),

  approvers: () =>
    api.get<Approver[]>('/leave-application/approvers').then(r => r.data),
}
