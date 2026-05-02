import { apiClient } from './client'

export interface EmailTemplate {
  template_id: string
  tenant_id: number
  template_name: string
  template_code: string
  subject: string
  body_html: string
  variables_json?: Record<string, any>
  category?: string
  is_active: boolean
  created_at: string
}

export interface EmailQueue {
  queue_id: string
  tenant_id: number
  template_id?: string
  from_email: string
  to_email: string
  cc?: string
  bcc?: string
  subject: string
  body_html: string
  priority: string
  scheduled_at?: string
  sent_at?: string
  status: string
  retry_count: number
  error_message?: string
  created_at: string
}

export interface WATemplate {
  wa_template_id: string
  tenant_id: number
  template_name: string
  template_code: string
  language: string
  category: string
  header_type?: string
  header_content?: string
  body_text: string
  footer_text?: string
  buttons_json?: Record<string, any>
  provider_template_id?: string
  status: string
  created_at: string
}

export interface WAQueue {
  wa_queue_id: string
  tenant_id: number
  wa_template_id: string
  to_phone: string
  variables_json?: Record<string, any>
  media_url?: string
  priority: string
  scheduled_at?: string
  sent_at?: string
  status: string
  wa_message_id?: string
  error_code?: string
  error_message?: string
  created_at: string
}

export interface EmailScheduler {
  scheduler_id: string
  tenant_id: number
  template_id: string
  trigger_type: string
  trigger_event?: string
  cron_expression?: string
  recipient_type: string
  recipient_filter?: Record<string, any>
  is_active: boolean
  last_run_at?: string
  next_run_at?: string
  created_at: string
}

export interface WAScheduler {
  scheduler_id: string
  tenant_id: number
  wa_template_id: string
  trigger_type: string
  trigger_event?: string
  cron_expression?: string
  recipient_type: string
  recipient_filter?: Record<string, any>
  is_active: boolean
  last_run_at?: string
  next_run_at?: string
  created_at: string
}

// Email Templates API
export const emailTemplatesApi = {
  list: async (params?: { category?: string; is_active?: boolean; skip?: number; limit?: number }) => {
    const response = await apiClient.get<EmailTemplate[]>('/communications/email-templates', { params })
    return response.data
  },

  create: async (data: Omit<EmailTemplate, 'template_id' | 'created_at'>) => {
    const response = await apiClient.post<EmailTemplate>('/communications/email-templates', data)
    return response.data
  },

  get: async (id: string) => {
    const response = await apiClient.get<EmailTemplate>(`/communications/email-templates/${id}`)
    return response.data
  },

  update: async (id: string, data: Partial<EmailTemplate>) => {
    const response = await apiClient.put<EmailTemplate>(`/communications/email-templates/${id}`, data)
    return response.data
  },

  delete: async (id: string) => {
    await apiClient.delete(`/communications/email-templates/${id}`)
  },
}

// Email Queue API
export const emailQueueApi = {
  list: async (params?: { status?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<EmailQueue[]>('/communications/email-queue', { params })
    return response.data
  },

  create: async (data: Omit<EmailQueue, 'queue_id' | 'sent_at' | 'retry_count' | 'created_at'>) => {
    const response = await apiClient.post<EmailQueue>('/communications/email-queue', data)
    return response.data
  },

  get: async (id: string) => {
    const response = await apiClient.get<EmailQueue>(`/communications/email-queue/${id}`)
    return response.data
  },

  update: async (id: string, data: Partial<EmailQueue>) => {
    const response = await apiClient.put<EmailQueue>(`/communications/email-queue/${id}`, data)
    return response.data
  },
}

// WhatsApp Templates API
export const whatsappTemplatesApi = {
  list: async (params?: { category?: string; status?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<WATemplate[]>('/communications/whatsapp-templates', { params })
    return response.data
  },

  create: async (data: Omit<WATemplate, 'wa_template_id' | 'created_at'>) => {
    const response = await apiClient.post<WATemplate>('/communications/whatsapp-templates', data)
    return response.data
  },

  get: async (id: string) => {
    const response = await apiClient.get<WATemplate>(`/communications/whatsapp-templates/${id}`)
    return response.data
  },

  update: async (id: string, data: Partial<WATemplate>) => {
    const response = await apiClient.put<WATemplate>(`/communications/whatsapp-templates/${id}`, data)
    return response.data
  },
}

// WhatsApp Queue API
export const whatsappQueueApi = {
  list: async (params?: { status?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<WAQueue[]>('/communications/whatsapp-queue', { params })
    return response.data
  },

  create: async (data: Omit<WAQueue, 'wa_queue_id' | 'sent_at' | 'wa_message_id' | 'error_code' | 'error_message' | 'created_at'>) => {
    const response = await apiClient.post<WAQueue>('/communications/whatsapp-queue', data)
    return response.data
  },

  get: async (id: string) => {
    const response = await apiClient.get<WAQueue>(`/communications/whatsapp-queue/${id}`)
    return response.data
  },

  update: async (id: string, data: Partial<WAQueue>) => {
    const response = await apiClient.put<WAQueue>(`/communications/whatsapp-queue/${id}`, data)
    return response.data
  },
}

// Email Schedulers API
export const emailSchedulersApi = {
  list: async (params?: { is_active?: boolean }) => {
    const response = await apiClient.get<EmailScheduler[]>('/communications/email-schedulers', { params })
    return response.data
  },

  create: async (data: Omit<EmailScheduler, 'scheduler_id' | 'last_run_at' | 'next_run_at' | 'created_at'>) => {
    const response = await apiClient.post<EmailScheduler>('/communications/email-schedulers', data)
    return response.data
  },

  update: async (id: string, data: Partial<EmailScheduler>) => {
    const response = await apiClient.put<EmailScheduler>(`/communications/email-schedulers/${id}`, data)
    return response.data
  },
}

// WhatsApp Schedulers API
export const whatsappSchedulersApi = {
  list: async (params?: { is_active?: boolean }) => {
    const response = await apiClient.get<WAScheduler[]>('/communications/whatsapp-schedulers', { params })
    return response.data
  },

  create: async (data: Omit<WAScheduler, 'scheduler_id' | 'last_run_at' | 'next_run_at' | 'created_at'>) => {
    const response = await apiClient.post<WAScheduler>('/communications/whatsapp-schedulers', data)
    return response.data
  },

  update: async (id: string, data: Partial<WAScheduler>) => {
    const response = await apiClient.put<WAScheduler>(`/communications/whatsapp-schedulers/${id}`, data)
    return response.data
  },
}
