import api from './client'
import type { User, Role, Branch, PaginatedResponse, UserCreateForm, RoleCreateForm, BranchCreateForm } from '@/types/auth'

// ── Users ─────────────────────────────────────────────────────────────────────
export const usersApi = {
  list: (params?: {
    page?: number; page_size?: number; search?: string
    status?: string; role_id?: number; branch_id?: number
  }) => api.get<PaginatedResponse<User>>('/users', { params }).then(r => r.data),

  get: (id: number) => api.get<User>(`/users/${id}`).then(r => r.data),

  invite: (data: UserCreateForm) =>
    api.post<User>('/users', data).then(r => r.data),

  update: (id: number, data: Partial<UserCreateForm> & { status?: string; avatar_url?: string }) =>
    api.patch<User>(`/users/${id}`, data).then(r => r.data),

  delete: (id: number) => api.delete(`/users/${id}`).then(r => r.data),

  acceptInvite: (token: string, password: string) =>
    api.post('/users/accept-invite', null, { params: { token, password } }).then(r => r.data),
}

// ── Roles ─────────────────────────────────────────────────────────────────────
export const rolesApi = {
  list: () => api.get<Role[]>('/roles').then(r => r.data),

  create: (data: RoleCreateForm) =>
    api.post<Role>('/roles', data).then(r => r.data),

  update: (id: number, data: Partial<RoleCreateForm> & { is_active?: boolean }) =>
    api.patch<Role>(`/roles/${id}`, data).then(r => r.data),

  delete: (id: number) => api.delete(`/roles/${id}`).then(r => r.data),
}

// ── Branches ──────────────────────────────────────────────────────────────────
export const branchesApi = {
  list: () => api.get<Branch[]>('/branches').then(r => r.data),

  create: (data: BranchCreateForm) =>
    api.post<Branch>('/branches', data).then(r => r.data),

  update: (id: number, data: Partial<BranchCreateForm> & { is_active?: boolean }) =>
    api.patch<Branch>(`/branches/${id}`, data).then(r => r.data),
}
