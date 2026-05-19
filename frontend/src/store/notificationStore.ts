/**
 * Notification Store - Zustand store for managing notifications
 */

import { create } from 'zustand'
import { notificationApi, Notification, NotificationListResponse } from '@/api/notificationApi'

interface NotificationState {
  // State
  notifications: Notification[]
  unreadCount: number
  isLoading: boolean
  error: string | null
  currentPage: number
  totalNotifications: number
  pageSize: number

  // Actions
  fetchNotifications: (page?: number, status?: string) => Promise<void>
  fetchUnreadCount: () => Promise<void>
  markAsRead: (notificationId: number) => Promise<void>
  markAllAsRead: () => Promise<void>
  archiveNotification: (notificationId: number) => Promise<void>
  deleteNotification: (notificationId: number) => Promise<void>
  addNotification: (notification: Notification) => void
  clearError: () => void
  reset: () => void
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  // Initial state
  notifications: [],
  unreadCount: 0,
  isLoading: false,
  error: null,
  currentPage: 1,
  totalNotifications: 0,
  pageSize: 20,

  // Fetch notifications
  fetchNotifications: async (page = 1, status?: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await notificationApi.getNotifications(page, 20, status)
      set({
        notifications: response.notifications,
        unreadCount: response.unread_count,
        totalNotifications: response.total,
        currentPage: page,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.message || 'Failed to fetch notifications',
        isLoading: false,
      })
    }
  },

  // Fetch unread count
  fetchUnreadCount: async () => {
    try {
      const response = await notificationApi.getUnreadCount()
      set({ unreadCount: response.unread_count })
    } catch (error: any) {
      console.error('Failed to fetch unread count:', error)
    }
  },

  // Mark as read
  markAsRead: async (notificationId: number) => {
    try {
      await notificationApi.markAsRead(notificationId)
      // Update local state
      set((state) => ({
        notifications: state.notifications.map((n) =>
          n.notification_id === notificationId
            ? { ...n, status: 'read' as const }
            : n
        ),
        unreadCount: Math.max(0, state.unreadCount - 1),
      }))
    } catch (error: any) {
      set({ error: error.message || 'Failed to mark as read' })
    }
  },

  // Mark all as read
  markAllAsRead: async () => {
    try {
      await notificationApi.markAllAsRead()
      // Update local state
      set((state) => ({
        notifications: state.notifications.map((n) => ({
          ...n,
          status: 'read' as const,
        })),
        unreadCount: 0,
      }))
    } catch (error: any) {
      set({ error: error.message || 'Failed to mark all as read' })
    }
  },

  // Archive notification
  archiveNotification: async (notificationId: number) => {
    try {
      await notificationApi.archiveNotification(notificationId)
      // Update local state
      set((state) => ({
        notifications: state.notifications.filter(
          (n) => n.notification_id !== notificationId
        ),
      }))
    } catch (error: any) {
      set({ error: error.message || 'Failed to archive notification' })
    }
  },

  // Delete notification
  deleteNotification: async (notificationId: number) => {
    try {
      await notificationApi.deleteNotification(notificationId)
      // Update local state
      set((state) => ({
        notifications: state.notifications.filter(
          (n) => n.notification_id !== notificationId
        ),
      }))
    } catch (error: any) {
      set({ error: error.message || 'Failed to delete notification' })
    }
  },

  // Add notification (for real-time updates)
  addNotification: (notification: Notification) => {
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: state.unreadCount + 1,
    }))
  },

  // Clear error
  clearError: () => set({ error: null }),

  // Reset store
  reset: () => set({
    notifications: [],
    unreadCount: 0,
    isLoading: false,
    error: null,
    currentPage: 1,
    totalNotifications: 0,
  }),
}))
