export interface User {
  user_id: number
  tenant_id: number
  role_id: number
  branch_id: number | null
  first_name: string
  last_name: string
  display_name: string | null
  email: string
  phone: string | null
  avatar_url: string | null
  designation: string | null
  membership_number: string | null
  is_owner: boolean
  is_two_factor_enabled: boolean
  status: 'ACTIVE' | 'INACTIVE' | 'INVITED' | 'SUSPENDED'
  last_login_at: string | null
  created_at: string
  role?: Role | null
}

export interface Role {
  role_id: number
  role_name: string
  role_code: string
  description: string | null
  permissions_json: Record<string, Record<string, boolean>>
  is_system_role: boolean
  can_manage_users: boolean
  can_view_billing: boolean
  can_approve_task: boolean
  is_active: boolean
}

export interface Branch {
  branch_id: number
  branch_name: string
  branch_code: string
  email: string | null
  phone: string | null
  city: string | null
  state: string | null
  is_head_office: boolean
  is_active: boolean
}

export interface Tenant {
  tenant_id: number
  tenant_code: string
  firm_name: string
  owner_name: string
  email: string
  phone: string
  membership_number: string | null
  gstin: string | null
  pan: string | null
  address_line1: string | null
  city: string | null
  state: string | null
  pincode: string | null
  country: string
  logo_url: string | null
  timezone: string
  currency_code: string
  status: string
  trial_end_date: string | null
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface LoginForm {
  email: string
  password: string
  totp_code?: string
  remember_me: boolean
}

export interface RegisterForm {
  firm_name: string
  owner_name: string
  tenant_code: string
  membership_number?: string
  email: string
  phone: string
  password: string
  confirm_password: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ApiError {
  detail: string
  errors?: { field: string; message: string }[]
}

export interface UserCreateForm {
  first_name: string
  last_name: string
  email: string
  phone?: string
  role_id: number
  branch_id?: number
  designation?: string
  membership_number?: string
  is_owner?: boolean
}

export interface RoleCreateForm {
  role_name: string
  role_code: string
  description?: string
  permissions_json: Record<string, Record<string, boolean>>
  can_manage_users: boolean
  can_view_billing: boolean
  can_approve_task: boolean
}

export interface BranchCreateForm {
  branch_name: string
  branch_code: string
  email?: string
  phone?: string
  address_line1?: string
  address_line2?: string
  city?: string
  state?: string
  pincode?: string
  gstin?: string
  manager_user_id?: number
  is_head_office: boolean
}
