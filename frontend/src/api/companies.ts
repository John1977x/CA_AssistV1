import api from './client'

export interface CreateCompanyRequest {
  company_name: string
  company_code: string
  email?: string
  phone?: string
  address_line1?: string
  address_line2?: string
  city?: string
  state?: string
  pincode?: string
  pan?: string
  gstin?: string
  cin?: string
}

export interface CompanyResponse {
  company_id: string
  company_name: string
  company_code: string
  email?: string
  phone?: string
  city?: string
  state?: string
  status: string
  created_at: string
}

export interface CreateBranchRequest {
  branch_name: string
  branch_code: string
  email?: string
  phone?: string
  address_line1?: string
  address_line2?: string
  city?: string
  state?: string
  pincode?: string
  is_head_office?: boolean
  manager_id?: number
}

export interface BranchResponse {
  branch_id: string
  branch_name: string
  branch_code: string
  email?: string
  phone?: string
  city?: string
  state?: string
  is_head_office: boolean
  status: string
  created_at: string
}

export interface TeamMemberResponse {
  company_user_id: string
  user_id: number
  first_name: string
  last_name: string
  email: string
  phone?: string
  role: string
  status: string
  joined_at?: string
}

export interface AddTeamMemberRequest {
  email: string
  first_name: string
  last_name: string
  phone?: string
  role: string
  branch_id?: string
}

export interface AddClientRequest {
  client_name: string
  client_code: string
  email?: string
  phone?: string
  client_type?: string
  pan?: string
  gstin?: string
}

export interface ClientResponse {
  client_id: string
  client_name: string
  client_code: string
  email?: string
  phone?: string
  client_type?: string
  status: string
  user_id?: number
  created_at: string
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Document Request Tickets
export interface DocumentRequestTicketResponse {
  ticket_id: string
  company_id: string
  client_id: string
  requested_by_user_id: number
  document_types: string[]
  description?: string
  priority: string
  status: string
  assigned_to_user_id?: number
  completed_at?: string
  completed_by_user_id?: number
  completion_notes?: string
  created_at: string
  updated_at: string
}

export interface CreateDocumentRequestRequest {
  document_types: string[]
  description?: string
  priority?: string
}

export interface UpdateDocumentRequestRequest {
  status?: string
  assigned_to_user_id?: number
  completion_notes?: string
}

export const companiesApi = {
  // Companies
  listCompanies: async (): Promise<CompanyResponse[]> => {
    const response = await api.get(`${API_URL}/api/v1/companies`)
    return response.data
  },

  createCompany: async (data: CreateCompanyRequest): Promise<CompanyResponse> => {
    const response = await api.post(`${API_URL}/api/v1/companies`, data)
    return response.data
  },

  getCompany: async (companyId: string): Promise<CompanyResponse> => {
    const response = await api.get(`${API_URL}/api/v1/companies/${companyId}`)
    return response.data
  },

  updateCompany: async (companyId: string, data: CreateCompanyRequest): Promise<CompanyResponse> => {
    const response = await api.patch(`${API_URL}/api/v1/companies/${companyId}`, data)
    return response.data
  },

  deleteCompany: async (companyId: string): Promise<void> => {
    await api.delete(`${API_URL}/api/v1/companies/${companyId}`)
  },

  // Branches
  listBranches: async (companyId: string): Promise<BranchResponse[]> => {
    const response = await api.get(`${API_URL}/api/v1/companies/${companyId}/branches`)
    return response.data
  },

  createBranch: async (companyId: string, data: CreateBranchRequest): Promise<BranchResponse> => {
    const response = await api.post(`${API_URL}/api/v1/companies/${companyId}/branches`, data)
    return response.data
  },

  getBranch: async (companyId: string, branchId: string): Promise<BranchResponse> => {
    const response = await api.get(`${API_URL}/api/v1/companies/${companyId}/branches/${branchId}`)
    return response.data
  },

  deleteBranch: async (companyId: string, branchId: string): Promise<void> => {
    await api.delete(`${API_URL}/api/v1/companies/${companyId}/branches/${branchId}`)
  },

  // Team Members
  listTeamMembers: async (companyId: string): Promise<TeamMemberResponse[]> => {
    const response = await api.get(`${API_URL}/api/v1/companies/${companyId}/team`)
    return response.data
  },

  addTeamMember: async (companyId: string, data: AddTeamMemberRequest): Promise<TeamMemberResponse> => {
    const response = await api.post(`${API_URL}/api/v1/companies/${companyId}/team/employees`, data)
    return response.data
  },

  removeTeamMember: async (companyId: string, userId: number): Promise<void> => {
    await api.delete(`${API_URL}/api/v1/companies/${companyId}/team/${userId}`)
  },

  // Clients
  listClients: async (companyId: string): Promise<ClientResponse[]> => {
    const response = await api.get(`${API_URL}/api/v1/companies/${companyId}/clients`)
    return response.data
  },

  createClient: async (companyId: string, data: AddClientRequest): Promise<ClientResponse> => {
    const response = await api.post(`${API_URL}/api/v1/companies/${companyId}/clients`, data)
    return response.data
  },

  getClient: async (companyId: string, clientId: string): Promise<ClientResponse> => {
    const response = await api.get(`${API_URL}/api/v1/companies/${companyId}/clients/${clientId}`)
    return response.data
  },

  updateClient: async (companyId: string, clientId: string, data: Partial<AddClientRequest>): Promise<ClientResponse> => {
    const response = await api.patch(`${API_URL}/api/v1/companies/${companyId}/clients/${clientId}`, data)
    return response.data
  },

  deleteClient: async (companyId: string, clientId: string): Promise<void> => {
    await api.delete(`${API_URL}/api/v1/companies/${companyId}/clients/${clientId}`)
  },

  // Document Request Tickets
  createDocumentRequest: async (
    companyId: string,
    clientId: string,
    data: CreateDocumentRequestRequest
  ): Promise<DocumentRequestTicketResponse> => {
    const response = await api.post(
      `${API_URL}/api/v1/companies/${companyId}/clients/${clientId}/document-request`,
      data
    )
    return response.data
  },

  listDocumentRequests: async (companyId: string, statusFilter?: string): Promise<DocumentRequestTicketResponse[]> => {
    const params = statusFilter ? `?status_filter=${statusFilter}` : ''
    const response = await api.get(`${API_URL}/api/v1/companies/${companyId}/document-requests${params}`)
    return response.data
  },

  updateDocumentRequest: async (
    companyId: string,
    ticketId: string,
    data: UpdateDocumentRequestRequest
  ): Promise<DocumentRequestTicketResponse> => {
    const response = await api.patch(
      `${API_URL}/api/v1/companies/${companyId}/document-requests/${ticketId}`,
      data
    )
    return response.data
  },
}
