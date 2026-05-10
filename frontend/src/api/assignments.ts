import api from './client'
import type { PaginatedResponse } from '@/types/auth'

export interface AssignmentTemplate {
  template_id: number
  title: string
  description?: string
  category: string
  total_steps: number
  estimated_hours?: number
  difficulty_level: string
  is_active: boolean
  steps: AssignmentTemplateStep[]
  created_at: string
}

export interface AssignmentTemplateStep {
  step_id: number
  step_number: number
  title: string
  description?: string
  instructions?: string
  estimated_hours?: number
  is_required: boolean
}

export interface Assignment {
  assignment_id: number
  template_id: number
  title: string
  description?: string
  assigned_to_user_id: number
  assigned_by_user_id: number
  due_date: string
  status: string
  completion_percentage: number
  total_score?: number
  feedback?: string
  created_at: string
  submitted_at?: string
  approved_at?: string
}

export interface AssignmentDetail extends Assignment {
  template: AssignmentTemplate
  step_submissions: AssignmentStepSubmission[]
}

export interface AssignmentStepSubmission {
  submission_id: number
  assignment_id: number
  step_id: number
  status: string
  submission_text?: string
  file_url?: string
  file_name?: string
  score?: number
  feedback?: string
  submitted_at: string
  reviewed_at?: string
}

export const assignmentsApi = {
  // Templates
  templates: (params?: { page?: number; page_size?: number; category?: string }) =>
    api.get<PaginatedResponse<AssignmentTemplate>>('/assignments/templates', { params }).then(r => r.data),

  getTemplate: (templateId: number) =>
    api.get<AssignmentTemplate>(`/assignments/templates/${templateId}`).then(r => r.data),

  createTemplate: (data: any) =>
    api.post<AssignmentTemplate>('/assignments/templates', data).then(r => r.data),

  // Assignments
  list: (params?: { page?: number; page_size?: number; assigned_to_user_id?: number; status?: string }) =>
    api.get<PaginatedResponse<Assignment>>('/assignments', { params }).then(r => r.data),

  get: (assignmentId: number) =>
    api.get<AssignmentDetail>(`/assignments/${assignmentId}`).then(r => r.data),

  create: (data: { template_id: number; assigned_to_user_id: number; due_date: string; title?: string; description?: string }) =>
    api.post<Assignment>('/assignments', data).then(r => r.data),

  update: (assignmentId: number, data: { status?: string; feedback?: string; total_score?: number }) =>
    api.patch<Assignment>(`/assignments/${assignmentId}`, data).then(r => r.data),

  // Step Submissions
  submitStep: (assignmentId: number, stepId: number, data: FormData) =>
    api.post<AssignmentStepSubmission>(
      `/assignments/${assignmentId}/steps/${stepId}/submit`,
      data,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    ).then(r => r.data),

  reviewSubmission: (assignmentId: number, submissionId: number, data: { status: string; score: number; feedback?: string }) =>
    api.patch<AssignmentStepSubmission>(
      `/assignments/${assignmentId}/submissions/${submissionId}/review`,
      data
    ).then(r => r.data),

  getSubmissions: (assignmentId: number) =>
    api.get<AssignmentStepSubmission[]>(`/assignments/${assignmentId}/submissions`).then(r => r.data),
}
