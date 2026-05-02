import api from './client'
import type { AuthTokens, LoginForm, RegisterForm, User } from '@/types/auth'

export const authApi = {
  login: (data: LoginForm) =>
    api.post<AuthTokens>('/auth/login', data).then(r => r.data),

  register: (data: RegisterForm) =>
    api.post<{ message: string }>('/auth/register', data).then(r => r.data),

  logout: () => api.post('/auth/logout'),

  me: () => api.get<User>('/auth/me').then(r => r.data),

  refresh: (refresh_token: string) =>
    api.post<{ access_token: string; refresh_token: string }>('/auth/refresh', { refresh_token })
      .then(r => r.data),

  changePassword: (data: { current_password: string; new_password: string; confirm_password: string }) =>
    api.post('/auth/change-password', data).then(r => r.data),

  forgotPassword: (email: string) =>
    api.post('/auth/forgot-password', { email }).then(r => r.data),

  resetPassword: (data: { token: string; new_password: string; confirm_password: string }) =>
    api.post('/auth/reset-password', data).then(r => r.data),

  enable2fa: () =>
    api.post<{ qr_code: string; secret: string }>('/auth/2fa/enable').then(r => r.data),

  confirm2fa: (totp_code: string) =>
    api.post('/auth/2fa/confirm', { totp_code }).then(r => r.data),

  disable2fa: (totp_code: string) =>
    api.post('/auth/2fa/disable', { totp_code }).then(r => r.data),
}
