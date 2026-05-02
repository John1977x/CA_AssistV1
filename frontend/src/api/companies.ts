import { apiClient } from './client'

export interface TenantCompany {
  company_id: string
  company_code: string
  tenant_id: number
  company_name: string
  phone?: string
  address1?: string
  address2?: string
  city?: string
  state?: string
  pincode?: string
  country?: string
  status: string
  created_at: string
}

export interface CustomerCompany {
  company_id: string
  company_code: string
  customer_id: number
  tenant_id: number
  company_name: string
  company_type?: string
  cin?: string
  pan?: string
  tan?: string
  gstin?: string
  incorporation_date?: string
  registered_address?: string
  city?: string
  state?: string
  pincode?: string
  country?: string
  phone?: string
  email?: string
  is_primary: boolean
  status: string
  created_at: string
}

export interface ClientDocument {
  client_doc_id: string
  customer_id: number
  company_id?: string
  tenant_id: number
  document_type: string
  document_number?: string
  document_name: string
  url: string
  size_kb?: number
  issue_date?: string
  expiry_date?: string
  verified_by?: number
  verified_at?: string
  status: string
  remarks?: string
  created_at: string
}

export interface TenantCompanyCreate {
  company_code: string
  tenant_id: number
  company_name: string
  phone?: string
  address1?: string
  address2?: string
  city?: string
  state?: string
  pincode?: string
  country?: string
  status?: string
}

export interface CustomerCompanyCreate {
  company_code: string
  customer_id: number
  tenant_id: number
  company_name: string
  company_type?: string
  cin?: string
  pan?: string
  tan?: string
  gstin?: string
  incorporation_date?: string
  registered_address?: string
  city?: string
  state?: string
  pincode?: string
  country?: string
  phone?: string
  email?: string
  is_primary?: boolean
  status?: string
}

export interface ClientDocumentCreate {
  customer_id: number
  company_id?: string
  tenant_id: number
  document_type: string
  document_number?: string
  document_name: string
  url: string
  size_kb?: number
  issue_date?: string
  expiry_date?: string
  status?: string
  remarks?: string
}

// Tenant Companies API
export const tenantCompaniesApi = {
  list: async (params?: { skip?: number; limit?: number }) => {
    const response = await apiClient.get<TenantCompany[]>('/companies/tenant-companies', { params })
    return response.data
  },

  create: async (data: TenantCompanyCreate) => {
    const response = await apiClient.post<TenantCompany>('/companies/tenant-companies', data)
    return response.data
  },

  get: async (id: string) => {
    const response = await apiClient.get<TenantCompany>(`/companies/tenant-companies/${id}`)
    return response.data
  },

  update: async (id: string, data: Partial<TenantCompanyCreate>) => {
    const response = await apiClient.put<TenantCompany>(`/companies/tenant-companies/${id}`, data)
    return response.data
  },

  delete: async (id: string) => {
    await apiClient.delete(`/companies/tenant-companies/${id}`)
  },
}

// Customer Companies API
export const customerCompaniesApi = {
  list: async (params?: { customer_id?: number; skip?: number; limit?: number }) => {
    const response = await apiClient.get<CustomerCompany[]>('/companies/customer-companies', { params })
    return response.data
  },

  create: async (data: CustomerCompanyCreate) => {
    const response = await apiClient.post<CustomerCompany>('/companies/customer-companies', data)
    return response.data
  },

  get: async (id: string) => {
    const response = await apiClient.get<CustomerCompany>(`/companies/customer-companies/${id}`)
    return response.data
  },

  update: async (id: string, data: Partial<CustomerCompanyCreate>) => {
    const response = await apiClient.put<CustomerCompany>(`/companies/customer-companies/${id}`, data)
    return response.data
  },

  delete: async (id: string) => {
    await apiClient.delete(`/companies/customer-companies/${id}`)
  },
}

// Client Documents API
export const clientDocumentsApi = {
  list: async (params?: { customer_id?: number; company_id?: string; document_type?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<ClientDocument[]>('/companies/documents', { params })
    return response.data
  },

  create: async (data: ClientDocumentCreate) => {
    const response = await apiClient.post<ClientDocument>('/companies/documents', data)
    return response.data
  },

  get: async (id: string) => {
    const response = await apiClient.get<ClientDocument>(`/companies/documents/${id}`)
    return response.data
  },

  update: async (id: string, data: Partial<ClientDocumentCreate>) => {
    const response = await apiClient.put<ClientDocument>(`/companies/documents/${id}`, data)
    return response.data
  },

  delete: async (id: string) => {
    await apiClient.delete(`/companies/documents/${id}`)
  },
}
