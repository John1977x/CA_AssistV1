import api from './client'
import type { Task, TaskStep, TaskStats } from '@/types/task'
import type { PaginatedResponse } from '@/types/auth'

export const tasksApi = {
  stats: () =>
    api.get<TaskStats>('/tasks/stats').then(r => r.data),

  list: (params?: {
    page?: number; page_size?: number; search?: string
    status?: string; priority?: string; task_type_code?: string
    customer_id?: number; assigned_to_user_id?: number
    financial_year?: string; overdue_only?: boolean; due_today?: boolean
  }) =>
    api.get<PaginatedResponse<Task>>('/tasks', { params }).then(r => r.data),

  clientTasks: (params?: { page?: number; page_size?: number }) =>
    api.get<PaginatedResponse<Task>>('/companies/client/tasks', { params }).then(r => r.data),

  employeeTasks: (params?: { page?: number; page_size?: number }) =>
    api.get<PaginatedResponse<Task>>('/tasks/employee/assigned', { params }).then(r => r.data),

  get: (id: number) =>
    api.get<Task>(`/tasks/${id}`).then(r => r.data),

  create: (data: {
    customer_id: number; task_type_code: string; task_title: string
    due_date: string; financial_year?: string; return_period?: string
    priority?: string; assigned_to_user_id?: number; reviewer_user_id?: number
    description?: string; estimated_hours?: number; tags?: string[]
    internal_due_date?: string
  }) =>
    api.post<Task>('/tasks', data).then(r => r.data),

  update: (id: number, data: Partial<Task> & {
    status?: string; completion_percentage?: number
    acknowledgement_number?: string; actual_hours?: number
    billing_status?: string; billed_amount?: number
  }) =>
    api.patch<Task>(`/tasks/${id}`, data).then(r => r.data),

  delete: (id: number) =>
    api.delete(`/tasks/${id}`).then(r => r.data),

  // Steps
  addStep: (taskId: number, data: { step_title: string; step_description?: string; is_required?: boolean; is_client_action?: boolean }) =>
    api.post<TaskStep>(`/tasks/${taskId}/steps`, data).then(r => r.data),

  updateStep: (taskId: number, stepId: number, data: {
    status?: string; notes_json?: any[]; form_data_json?: any
    step_title?: string; step_description?: string
  }) =>
    api.patch<TaskStep>(`/tasks/${taskId}/steps/${stepId}`, data).then(r => r.data),

  deleteStep: (taskId: number, stepId: number) =>
    api.delete(`/tasks/${taskId}/steps/${stepId}`).then(r => r.data),

  // Reminders
  getReminders: (taskId: number) =>
    api.get(`/tasks/${taskId}/reminders`).then(r => r.data),

  createReminder: (taskId: number, data: {
    reminder_type: string; channel: string; message_body: string
    scheduled_at: string; target_user_id?: number; subject?: string
  }) =>
    api.post(`/tasks/${taskId}/reminders`, data).then(r => r.data),
}
