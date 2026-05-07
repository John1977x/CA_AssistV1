import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { CompanyRoleEnum } from '@/types/auth'
import { setTokens, clearTokens } from '@/api/client'

export interface UserProfile {
  user_id: number
  email: string
  first_name: string
  last_name: string
  display_name?: string
  phone?: string
  avatar_url?: string
  is_owner: boolean
  is_two_factor_enabled: boolean
  status: string
}

export interface CompanyInfo {
  company_id: string
  company_name: string
  company_code: string
  role: CompanyRoleEnum
  branch_id?: string
  branch_name?: string
  client_id?: string  // For clients, the actual client_id from CompanyClient table
}

interface AuthState {
  user: UserProfile | null
  company: CompanyInfo | null
  isAuthenticated: boolean
  isLoading: boolean

  setUser: (user: UserProfile) => void
  setCompany: (company: CompanyInfo) => void
  setAuth: (user: UserProfile, company: CompanyInfo, access: string, refresh: string) => void
  logout: () => void
  setLoading: (v: boolean) => void
  updateUser: (updates: Partial<UserProfile>) => void
}

export const useAuthStoreV2 = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      company: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => set({ user, isAuthenticated: true }),

      setCompany: (company) => set({ company }),

      setAuth: (user, company, access, refresh) => {
        setTokens(access, refresh)
        set({ user, company, isAuthenticated: true })
      },

      logout: () => {
        clearTokens()
        set({ user: null, company: null, isAuthenticated: false })
      },

      setLoading: (v) => set({ isLoading: v }),

      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),
    }),
    {
      name: 'ca-auth-v2',
      partialize: (state) => ({
        user: state.user,
        company: state.company,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
