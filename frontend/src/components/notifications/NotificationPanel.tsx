/**
 * Notification Panel - Dropdown panel showing notifications
 */

import { useEffect, useRef } from 'react'
import { useNotificationStore } from '@/store/notificationStore'
import { Bell, X, Check, Archive, Trash2, Loader } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import clsx from 'clsx'

interface NotificationPanelProps {
  isOpen: boolean
  onClose: () => void
}

export default function NotificationPanel({ isOpen, onClose }: NotificationPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null)
  const {
    notifications,
    unreadCount,
    isLoading,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    archiveNotification,
    deleteNotification,
  } = useNotificationStore()

  // Fetch notifications when panel opens
  useEffect(() => {
    if (isOpen) {
      fetchNotifications()
    }
  }, [isOpen, fetchNotifications])

  // Close panel when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen, onClose])

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return '✅'
      case 'warning':
        return '⚠️'
      case 'error':
        return '❌'
      case 'task_assigned':
        return '📋'
      case 'task_completed':
        return '✔️'
      case 'document_request':
        return '📄'
      case 'assignment_submitted':
        return '📤'
      case 'ticket_created':
        return '🎫'
      case 'ticket_updated':
        return '🔄'
      case 'user_invited':
        return '👤'
      case 'company_created':
        return '🏢'
      case 'subscription_updated':
        return '💳'
      default:
        return 'ℹ️'
    }
  }

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200'
      case 'error':
        return 'bg-red-50 border-red-200'
      default:
        return 'bg-blue-50 border-blue-200'
    }
  }

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-40 bg-black/20" onClick={onClose} />
      )}

      {/* Panel */}
      <div
        ref={panelRef}
        className={clsx(
          'fixed right-0 top-0 h-screen w-96 bg-white shadow-2xl z-50 flex flex-col transition-transform duration-300',
          isOpen ? 'translate-x-0' : 'translate-x-full'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div className="flex items-center gap-3">
            <Bell size={20} className="text-brand-600" />
            <h2 className="text-lg font-bold text-slate-900">Notifications</h2>
            {unreadCount > 0 && (
              <span className="inline-flex items-center justify-center w-6 h-6 text-xs font-bold text-white bg-red-500 rounded-full">
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-500 hover:bg-slate-100"
          >
            <X size={20} />
          </button>
        </div>

        {/* Actions */}
        {unreadCount > 0 && (
          <div className="border-b border-slate-200 px-6 py-3">
            <button
              onClick={() => markAllAsRead()}
              className="text-sm text-brand-600 hover:text-brand-700 font-medium flex items-center gap-2"
            >
              <Check size={16} />
              Mark all as read
            </button>
          </div>
        )}

        {/* Notifications List */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <Loader size={24} className="text-brand-600 animate-spin" />
            </div>
          ) : notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <Bell size={48} className="mb-4 opacity-20" />
              <p className="text-center">No notifications yet</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-200">
              {notifications.map((notification) => (
                <div
                  key={notification.notification_id}
                  className={clsx(
                    'p-4 hover:bg-slate-50 transition-colors border-l-4',
                    notification.status === 'unread'
                      ? 'border-l-brand-600 bg-brand-50'
                      : 'border-l-transparent'
                  )}
                >
                  {/* Notification Content */}
                  <div className="flex gap-3">
                    {/* Icon */}
                    <div className="text-2xl flex-shrink-0">
                      {getNotificationIcon(notification.notification_type)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <h3 className="font-semibold text-slate-900 text-sm">
                          {notification.title}
                        </h3>
                        {notification.status === 'unread' && (
                          <div className="w-2 h-2 bg-brand-600 rounded-full flex-shrink-0 mt-1" />
                        )}
                      </div>
                      <p className="text-sm text-slate-600 mt-1 line-clamp-2">
                        {notification.message}
                      </p>
                      <p className="text-xs text-slate-500 mt-2">
                        {formatDistanceToNow(new Date(notification.created_at), {
                          addSuffix: true,
                        })}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 mt-3 ml-11">
                    {notification.status === 'unread' && (
                      <button
                        onClick={() => markAsRead(notification.notification_id)}
                        className="p-1 rounded text-slate-500 hover:bg-slate-200 transition-colors"
                        title="Mark as read"
                      >
                        <Check size={16} />
                      </button>
                    )}
                    <button
                      onClick={() => archiveNotification(notification.notification_id)}
                      className="p-1 rounded text-slate-500 hover:bg-slate-200 transition-colors"
                      title="Archive"
                    >
                      <Archive size={16} />
                    </button>
                    <button
                      onClick={() => deleteNotification(notification.notification_id)}
                      className="p-1 rounded text-slate-500 hover:bg-red-100 hover:text-red-600 transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {notifications.length > 0 && (
          <div className="border-t border-slate-200 px-6 py-3 text-center">
            <button className="text-sm text-brand-600 hover:text-brand-700 font-medium">
              View all notifications
            </button>
          </div>
        )}
      </div>
    </>
  )
}
