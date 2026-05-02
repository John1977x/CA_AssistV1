import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Plus, Search, Trash2, Edit2, Mail, Shield, MoreVertical,
  Loader2, UserPlus, ChevronLeft, ChevronRight, RefreshCw,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { usersApi, rolesApi, branchesApi } from '@/api/users'
import { useAuthStore } from '@/store/authStore'
import type { User, UserCreateForm } from '@/types/auth'
import clsx from 'clsx'

const STATUS_BADGE: Record<string, string> = {
  ACTIVE:   'badge-green',
  INACTIVE: 'badge-gray',
  INVITED:  'badge-yellow',
  SUSPENDED:'badge-red',
}

const inviteSchema = z.object({
  first_name: z.string().min(1, 'Required'),
  last_name:  z.string().min(1, 'Required'),
  email:      z.string().email('Valid email required'),
  phone:      z.string().optional(),
  role_id:    z.number().optional(),
  branch_id:  z.number().optional(),
  designation: z.string().optional(),
  membership_number: z.string().optional(),
  is_owner:   z.boolean().optional(),
})

function InviteModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const { data: roles = [] } = useQuery({ queryKey: ['roles'], queryFn: rolesApi.list })
  const { data: branches = [] } = useQuery({ queryKey: ['branches'], queryFn: branchesApi.list })

  const { register, handleSubmit, watch, formState: { errors } } = useForm<UserCreateForm & { is_owner?: boolean }>({
    resolver: zodResolver(inviteSchema),
  })

  const isOwner = watch('is_owner')

  const invite = useMutation({
    mutationFn: (data: UserCreateForm & { is_owner?: boolean }) => usersApi.invite(data as any),
    onSuccess: () => {
      toast.success('Employee added successfully!')
      qc.invalidateQueries({ queryKey: ['users'] })
      onClose()
    },
  })

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-slate-100 px-6 py-4 flex items-center justify-between rounded-t-2xl">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Add New Employee</h2>
            <p className="text-sm text-slate-500">Add a team member to your firm</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl font-medium">✕</button>
        </div>

        <form onSubmit={handleSubmit(d => invite.mutate(d))} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">First Name *</label>
              <input {...register('first_name')} className={`input ${errors.first_name ? 'input-error' : ''}`} placeholder="Rahul" />
              {errors.first_name && <p className="mt-1 text-xs text-red-600">{errors.first_name.message}</p>}
            </div>
            <div>
              <label className="label">Last Name *</label>
              <input {...register('last_name')} className={`input ${errors.last_name ? 'input-error' : ''}`} placeholder="Verma" />
              {errors.last_name && <p className="mt-1 text-xs text-red-600">{errors.last_name.message}</p>}
            </div>
          </div>

          <div>
            <label className="label">Email Address *</label>
            <input {...register('email')} type="email" className={`input ${errors.email ? 'input-error' : ''}`} placeholder="rahul@yourfirm.com" />
            {errors.email && <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>}
          </div>

          <div>
            <label className="label">Mobile Number</label>
            <input {...register('phone')} type="tel" className="input" placeholder="9876543210" />
          </div>

          <div>
            <label className="label">Employee Type *</label>
            <div className="space-y-2">
              <label className="flex items-center gap-3 p-3 border border-slate-200 rounded-lg cursor-pointer hover:bg-slate-50 transition-colors">
                <input
                  type="radio"
                  value="false"
                  {...register('is_owner')}
                  className="w-4 h-4 rounded-full border-slate-300 text-brand-600"
                />
                <div>
                  <p className="font-medium text-slate-900 text-sm">Employee</p>
                  <p className="text-xs text-slate-500">Regular team member with limited access</p>
                </div>
              </label>
              <label className="flex items-center gap-3 p-3 border border-slate-200 rounded-lg cursor-pointer hover:bg-slate-50 transition-colors">
                <input
                  type="radio"
                  value="true"
                  {...register('is_owner')}
                  className="w-4 h-4 rounded-full border-slate-300 text-brand-600"
                />
                <div>
                  <p className="font-medium text-slate-900 text-sm">Owner</p>
                  <p className="text-xs text-slate-500">Full access to firm settings and all features</p>
                </div>
              </label>
            </div>
          </div>

          {branches.length > 0 && (
            <div>
              <label className="label">Branch</label>
              <select {...register('branch_id', { valueAsNumber: true })} className="input">
                <option value="">All branches</option>
                {branches.map(b => (
                  <option key={b.branch_id} value={b.branch_id}>{b.branch_name}</option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="label">Designation</label>
            <input {...register('designation')} className="input" placeholder="e.g. Article Assistant, Manager" />
          </div>

          <div>
            <label className="label">ICAI Membership Number</label>
            <input {...register('membership_number')} className="input" placeholder="Optional" />
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={invite.isPending} className="btn-primary flex-1">
              {invite.isPending ? <><Loader2 size={14} className="animate-spin" /> Adding...</> : <><UserPlus size={14} /> Add Employee</>}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function UserRow({ user, onDelete }: { user: User; onDelete: (id: number) => void }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const currentUser = useAuthStore(s => s.user)

  const initials = `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
  const isSelf = currentUser?.user_id === user.user_id

  return (
    <tr className="hover:bg-slate-50 transition-colors">
      <td className="table-td">
        <div className="flex items-center gap-3">
          {user.avatar_url
            ? <img src={user.avatar_url} alt="" className="w-8 h-8 rounded-full object-cover" />
            : <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center text-brand-800 text-xs font-bold">
                {initials}
              </div>
          }
          <div>
            <div className="font-medium text-slate-900 text-sm flex items-center gap-2">
              {user.display_name || `${user.first_name} ${user.last_name}`}
              {isSelf && <span className="text-xs text-slate-400">(you)</span>}
              {user.is_owner && <span className="badge-purple text-xs">Co-Owner</span>}
            </div>
            <div className="text-xs text-slate-500">{user.email}</div>
          </div>
        </div>
      </td>
      <td className="table-td text-slate-600">
        {user.designation || <span className="text-slate-300">—</span>}
      </td>
      <td className="table-td">
        <div className="flex items-center gap-1.5">
          <Shield size={12} className="text-brand-600" />
          <span className="text-sm text-slate-600">{user.role?.role_name || '—'}</span>
        </div>
      </td>
      <td className="table-td">
        <span className={STATUS_BADGE[user.status] || 'badge-gray'}>
          {user.status.charAt(0) + user.status.slice(1).toLowerCase()}
        </span>
      </td>
      <td className="table-td text-slate-500 text-xs">
        {user.last_login_at
          ? new Date(user.last_login_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
          : 'Never'
        }
      </td>
      <td className="table-td">
        <div className="relative">
          <button onClick={() => setMenuOpen(!menuOpen)}
            className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600">
            <MoreVertical size={15} />
          </button>
          {menuOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 top-8 z-20 bg-white border border-slate-200 rounded-xl shadow-lg w-44 py-1">
                <button className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50">
                  <Edit2 size={13} /> Edit User
                </button>
                <button className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50">
                  <Mail size={13} /> Resend Invite
                </button>
                {!user.is_owner && !isSelf && (
                  <button
                    onClick={() => { onDelete(user.user_id); setMenuOpen(false) }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50">
                    <Trash2 size={13} /> Remove User
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </td>
    </tr>
  )
}

export default function UsersPage() {
  const qc = useQueryClient()
  const [showInvite, setShowInvite] = useState(false)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState('')

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['users', page, search, statusFilter],
    queryFn: () => usersApi.list({ page, page_size: 15, search: search || undefined, status: statusFilter || undefined }),
    placeholderData: prev => prev,
  })

  const deleteUser = useMutation({
    mutationFn: usersApi.delete,
    onSuccess: () => {
      toast.success('User removed.')
      qc.invalidateQueries({ queryKey: ['users'] })
    },
  })

  const users = data?.items || []
  const total = data?.total || 0
  const totalPages = data?.total_pages || 1

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Team Members</h1>
          <p className="text-sm text-slate-500 mt-0.5">{total} user{total !== 1 ? 's' : ''} in your firm</p>
        </div>
        <button onClick={() => setShowInvite(true)} className="btn-primary">
          <UserPlus size={15} /> Add New Employee
        </button>
      </div>

      {/* Filters */}
      <div className="card p-4 mb-5">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1) }}
              placeholder="Search by name or email..."
              className="input pl-9"
            />
          </div>
          <select
            value={statusFilter}
            onChange={e => { setStatusFilter(e.target.value); setPage(1) }}
            className="input w-full sm:w-40"
          >
            <option value="">All Status</option>
            <option value="ACTIVE">Active</option>
            <option value="INVITED">Invited</option>
            <option value="INACTIVE">Inactive</option>
          </select>
          <button onClick={() => qc.invalidateQueries({ queryKey: ['users'] })}
            className={clsx('btn-ghost', isFetching && 'opacity-50')}>
            <RefreshCw size={15} className={isFetching ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="table-th">Name</th>
                <th className="table-th">Designation</th>
                <th className="table-th">Role</th>
                <th className="table-th">Status</th>
                <th className="table-th">Last Login</th>
                <th className="table-th w-12"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="py-16 text-center">
                    <Loader2 size={24} className="animate-spin text-slate-400 mx-auto" />
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-16 text-center">
                    <div className="text-slate-400">
                      <UserPlus size={32} className="mx-auto mb-3 opacity-40" />
                      <p className="text-sm font-medium">No users found</p>
                      <p className="text-xs mt-1">Invite your first team member to get started</p>
                    </div>
                  </td>
                </tr>
              ) : (
                users.map(u => (
                  <UserRow key={u.user_id} user={u}
                    onDelete={id => {
                      if (confirm('Remove this user from your firm?')) deleteUser.mutate(id)
                    }} />
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="border-t border-slate-100 px-4 py-3 flex items-center justify-between">
            <p className="text-sm text-slate-500">
              Showing {((page - 1) * 15) + 1}–{Math.min(page * 15, total)} of {total}
            </p>
            <div className="flex items-center gap-1">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                className="btn-ghost btn-sm">
                <ChevronLeft size={14} />
              </button>
              <span className="text-sm text-slate-600 px-2">{page} / {totalPages}</span>
              <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}
                className="btn-ghost btn-sm">
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      {showInvite && <InviteModal onClose={() => setShowInvite(false)} />}
    </div>
  )
}
