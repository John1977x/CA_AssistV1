import { apiClient } from './client'

export interface Company {
  company_id: string
  owner_id: number
  company_name: string
  company_code: string
  email?: string
  phone?: string
  address_line1?: string
  address_line2?: string
  city?: string
  state?: string
  pincode?: string
  country?: string
  pan?: string
  gstin?: string
  cin?: string
  status: string
  description?: string
  logo_url?: string
  website?: string
  created_at: string
  updated_at: string
}

export interface CompanyUser {
  company_user_id: string
  user_id: number
  role: string
  status: string
  joined_at?: string
}

export interface CompanyClient {
  client_id: string
  client_name: string
  client_code: string
  email?: string
  phone?: string
  status: string
}

export interface CompanyBranch {
  branch_id: string
  branch_name: string
  branch_code: string
  city?: string
  state?: string
  is_head_office: boolean
  status: string
}

export const companiesApi = {
  // List all companies for the current owner
  listCompanies: async (): Promise<Company[]> => {
    const response = await apiClient.get('/api/v1/companies')
    return response.data
  },

  // Get a specific company
  getCompany: async (companyId: string): Promise<Company> => {
    const response = await apiClient.get(`/api/v1/companies/${companyId}`)
    return response.data
  },

  // Create a new company
  createCompany: async (data: Partial<Company>): Promise<Company> => {
    const response = await apiClient.post('/api/v1/companies', data)
    return response.data
  },

  // Update a company
  updateCompany: async (companyId: string, data: Partial<Company>): Promise<Company> => {
    const response = await apiClient.put(`/api/v1/companies/${companyId}`, data)
    return response.data
  },

  // Delete a company
  deleteCompany: async (companyId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/companies/${companyId}`)
  },

  // List team members (employees/managers) in a company
  listTeamMembers: async (companyId: string): Promise<CompanyUser[]> => {
    const response = await apiClient.get(`/api/v1/companies/${companyId}/team-members`)
    return response.data
  },

  // Add an employee to a company
  addEmployee: async (companyId: string, data: { user_id: number; role: string }): Promise<CompanyUser> => {
    const response = await apiClient.post(`/api/v1/companies/${companyId}/employees`, data)
    return response.data
  },

  // Add a manager to a company
  addManager: async (companyId: string, data: { user_id: number }): Promise<CompanyUser> => {
    const response = await apiClient.post(`/api/v1/companies/${companyId}/managers`, data)
    return response.data
  },

  // Remove a team member from a company
  removeTeamMember: async (companyId: string, userId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/companies/${companyId}/team-members/${userId}`)
  },

  // List clients of a company
  listClients: async (companyId: string): Promise<CompanyClient[]> => {
    const response = await apiClient.get(`/api/v1/companies/${companyId}/clients`)
    return response.data
  },

  // Add a client to a company
  addClient: async (companyId: string, data: Partial<CompanyClient>): Promise<CompanyClient> => {
    const response = await apiClient.post(`/api/v1/companies/${companyId}/clients`, data)
    return response.data
  },

  // Delete a client from a company
  deleteClient: async (companyId: string, clientId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/companies/${companyId}/clients/${clientId}`)
  },

  // List branches of a company
  listBranches: async (companyId: string): Promise<CompanyBranch[]> => {
    const response = await apiClient.get(`/api/v1/companies/${companyId}/branches`)
    return response.data
  },

  // Create a branch for a company
  createBranch: async (companyId: string, data: Partial<CompanyBranch>): Promise<CompanyBranch> => {
    const response = await apiClient.post(`/api/v1/companies/${companyId}/branches`, data)
    return response.data
  },

  // Delete a branch
  deleteBranch: async (companyId: string, branchId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/companies/${companyId}/branches/${branchId}`)
  },
}
