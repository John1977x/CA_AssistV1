import axios from 'axios'
import type { LoginResponse, UserProfile, CompanyInfo } from '@/store/authStoreV2'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface OwnerRegisterRequest {
  first_name: string
  last_name: string
  email: string
  phone: string
  password: string
  company_name: string
  company_code: string
}

export interface OwnerRegisterResponse {
  user_id: number
  email: string
  first_name: string
  last_name: string
  company_id: string
  company_name: string
  message: string
}

export interface LoginRequest {
  email: string
  password: string
  totp_code?: string
}

export const authV2Api = {
  // Owner Registration
  registerOwner: async (data: OwnerRegisterRequest): Promise<OwnerRegisterResponse> => {
    const response = await axios.post(`${API_URL}/api/v1/auth/register-owner`, data)
    return response.data
  },

  // Login
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await axios.post(`${API_URL}/api/v1/auth/login`, data)
    return response.data
  },

  // Refresh Token
  refreshToken: async (refreshToken: string) => {
    const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
      refresh_token: refreshToken,
    })
    return response.data
  },

  // Get Current User
  getCurrentUser: async (): Promise<UserProfile> => {
    const response = await axios.get(`${API_URL}/api/v1/auth/me`)
    return response.data
  },

  // Logout
  logout: async () => {
    const response = await axios.post(`${API_URL}/api/v1/auth/logout`)
    return response.data
  },

  // Change Password
  changePassword: async (data: {
    current_password: string
    new_password: string
    confirm_password: string
  }) => {
    const response = await axios.post(`${API_URL}/api/v1/auth/change-password`, data)
    return response.data
  },

  // Forgot Password
  forgotPassword: async (email: string) => {
    const response = await axios.post(`${API_URL}/api/v1/auth/forgot-password`, {
      email,
    })
    return response.data
  },

  // Reset Password
  resetPassword: async (data: {
    token: string
    new_password: string
    confirm_password: string
  }) => {
    const response = await axios.post(`${API_URL}/api/v1/auth/reset-password`, data)
    return response.data
  },

  // Change Company & Branch
  changeCompanyBranch: async (data: {
    company_id: string
    branch_id?: string | null
  }): Promise<{ message: string; company: CompanyInfo }> => {
    const response = await axios.post(`${API_URL}/api/v1/auth/change-company-branch`, data)
    return response.data
  },
}
