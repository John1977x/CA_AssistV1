/**
 * Notification API Client
 * Handles all notification-related API calls
 */

import api from './client'

export interface Notification {
  notification_id: number
  user_id: number
  title: string
  message: string
  notification_type: 'info' | 'success' | 'warning' | 'error' | 'task_assigned' | 'task_completed' | 'document_request' | 'assignment_submitted' | 'ticket_created' | 'ticket_updated' | 'user_invited' | 'company_created' | 'subscription_updated'
  status: 'unread' | 'read' | 'archived'
  related_entity_type?: string
  related_entity_id?: number
  action_url?: string
  metadata?: Record<string, any>
  created_at: string
  read_at?: string
  archived_at?: string
}

export interface NotificationListResponse {
  notifications: Notification[]
  total: number
  unread_count: number
  page: number
  page_size: number
}

export interface NotificationPreference {
  preference_id: number
  user_id: number
  task_assigned: boolean
  task_completed: boolean
  document_request: boolean
  assignment_submitted: boolean
  ticket_created: boolean
  ticket_updated: boolean
  user_invited: boolean
  company_created: boolean
  subscription_updated: boolean
  email_notifications: boolean
  in_app_notifications: boolean
  quiet_hours_enabled: boolean
  quiet_hours_start?: string
  quiet_hours_end?: string
  created_at: string
  updated_at: string
}

export const notificationApi = {
  // Get notifications
  getNotifications: async (page: number = 1, pageSize: number = 20, status?: string): Promise<NotificationListResponse> => {
    const params = new URLSearchParams()
    params.append('page', page.toString())
    params.append('page_size', pageSize.toString())
    if (status) params.append('status', status)
    
    const response = await api.get(`/notifications?${params.toString()}`)
    return response.data
  },

  // Get unread count
  getUnreadCount: async (): Promise<{ unread_count: number }> => {
    const response = await api.get('/notifications/unread-count')
    return response.data
  },

  // Get single notification
  getNotification: async (notificationId: number): Promise<Notification> => {
    const response = await api.get(`/notifications/${notificationId}`)
    return response.data
  },

  // Mark as read
  markAsRead: async (notificationId: number): Promise<Notification> => {
    const response = await api.post(`/notifications/${notificationId}/read`)
    return response.data
  },

  // Mark all as read
  markAllAsRead: async (): Promise<{ message: string }> => {
    const response = await api.post('/notifications/read-all')
    return response.data
  },

  // Archive notification
  archiveNotification: async (notificationId: number): Promise<Notification> => {
    const response = await api.post(`/notifications/${notificationId}/archive`)
    return response.data
  },

  // Delete notification
  deleteNotification: async (notificationId: number): Promise<void> => {
    await api.delete(`/notifications/${notificationId}`)
  },

  // Get preferences
  getPreferences: async (): Promise<NotificationPreference> => {
    const response = await api.get('/notifications/preferences/me')
    return response.data
  },

  // Update preferences
  updatePreferences: async (data: Partial<NotificationPreference>): Promise<NotificationPreference> => {
    const response = await api.put('/notifications/preferences/me', data)
    return response.data
  },
}
