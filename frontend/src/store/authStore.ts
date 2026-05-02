import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types/auth'
import { setTokens, clearTokens } from '@/api/client'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean

  setUser: (user: User) => void
  setAuth: (user: User, access: string, refresh: string) => void
  logout: () => void
  setLoading: (v: boolean) => void
  updateUser: (updates: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => set({ user, isAuthenticated: true }),

      setAuth: (user, access, refresh) => {
        setTokens(access, refresh)
        set({ user, isAuthenticated: true })
      },

      logout: () => {
        clearTokens()
        set({ user: null, isAuthenticated: false })
      },

      setLoading: (v) => set({ isLoading: v }),

      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),
    }),
    {
      name: 'ca-auth',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)
