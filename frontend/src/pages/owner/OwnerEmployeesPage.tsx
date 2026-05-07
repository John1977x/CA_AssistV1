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
import { companiesApi } from '@/api/companies'
import { useAuthStoreV2 } from '@/store/authStoreV2'
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
  role:       z.string().default('EMPLOYEE'),
  branch_id:  z.string().optional(),
})

function InviteModal({ companyId, onClose }: { companyId: string; onClose: () => void }) {
  const qc = useQueryClient()
  const { data: branches = [] } = useQuery({
    queryKey: ['branches', companyId],
    queryFn: () => companiesApi.listBranches(companyId),
  })

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(inviteSchema),
    defaultValues: {
      role: 'EMPLOYEE',
    },
  })

  const invite = useMutation({
    mutationFn: (data: any) => companiesApi.addTeamMember(companyId, data),
    onSuccess: () => {
      toast.success('Employee added successfully!')
      qc.invalidateQueries({ queryKey: ['teamMembers', companyId] })
      onClose()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to add employee')
    },
  })

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-slate-100 px-6 py-4 flex items-center justify-between rounded-t-2xl">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Add New Employee</h2>
            <p className="text-sm text-slate-500">Add a team member to your company</p>
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
            <label className="label">Role *</label>
            <select {...register('role')} className="input">
              <option value="EMPLOYEE">Employee</option>
              <option value="MANAGER">Manager</option>
            </select>
          </div>

          {branches.length > 0 && (
            <div>
              <label className="label">Branch</label>
              <select {...register('branch_id')} className="input">
                <option value="">All branches</option>
                {branches.map(b => (
                  <option key={b.branch_id} value={b.branch_id}>{b.branch_name}</option>
                ))}
              </select>
            </div>
          )}

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

function UserRow({ member, companyId, onDelete }: { member: any; companyId: string; onDelete: (userId: number) => void }) {
  const [menuOpen, setMenuOpen] = useState(false)

  const initials = `${member.first_name[0]}${member.last_name[0]}`.toUpperCase()

  return (
    <tr className="hover:bg-slate-50 transition-colors">
      <td className="table-td">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center text-brand-800 text-xs font-bold">
            {initials}
          </div>
          <div>
            <div className="font-medium text-slate-900 text-sm flex items-center gap-2">
              {member.first_name} {member.last_name}
              {member.role === 'MANAGER' && <span className="badge-purple text-xs">Manager</span>}
            </div>
            <div className="text-xs text-slate-500">{member.email}</div>
          </div>
        </div>
      </td>
      <td className="table-td">
        <div className="flex items-center gap-1.5">
          <Shield size={12} className="text-brand-600" />
          <span className="text-sm text-slate-600">{member.role || '—'}</span>
        </div>
      </td>
      <td className="table-td">
        <span className={STATUS_BADGE[member.status] || 'badge-gray'}>
          {member.status.charAt(0) + member.status.slice(1).toLowerCase()}
        </span>
      </td>
      <td className="table-td text-slate-500 text-xs">
        {member.joined_at
          ? new Date(member.joined_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
          : 'Recently'
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
                <button
                  onClick={() => { onDelete(member.user_id); setMenuOpen(false) }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50">
                  <Trash2 size={13} /> Remove User
                </button>
              </div>
            </>
          )}
        </div>
      </td>
    </tr>
  )
}

export default function OwnerEmployeesPage() {
  const qc = useQueryClient()
  const { company } = useAuthStoreV2()
  const [showInvite, setShowInvite] = useState(false)
  const [search, setSearch] = useState('')

  // Redirect if no company selected
  if (!company) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="card p-8 text-center">
          <p className="text-slate-600">Please select a company first</p>
        </div>
      </div>
    )
  }

  const { data: members = [], isLoading, isFetching } = useQuery({
    queryKey: ['teamMembers', company.company_id],
    queryFn: () => companiesApi.listTeamMembers(company.company_id),
    enabled: !!company.company_id,
  })

  const deleteUser = useMutation({
    mutationFn: (userId: number) => companiesApi.removeTeamMember(company.company_id, userId),
    onSuccess: () => {
      toast.success('Employee removed.')
      qc.invalidateQueries({ queryKey: ['teamMembers', company.company_id] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to remove employee')
    },
  })

  const filteredMembers = members.filter(m =>
    search === '' || 
    m.first_name.toLowerCase().includes(search.toLowerCase()) ||
    m.last_name.toLowerCase().includes(search.toLowerCase()) ||
    m.email.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Employees</h1>
          <p className="text-sm text-slate-500 mt-0.5">{filteredMembers.length} employee{filteredMembers.length !== 1 ? 's' : ''} in {company.company_name}</p>
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
              onChange={e => setSearch(e.target.value)}
              placeholder="Search by name or email..."
              className="input pl-9"
            />
          </div>
          <button onClick={() => qc.invalidateQueries({ queryKey: ['teamMembers', company.company_id] })}
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
                <th className="table-th">Role</th>
                <th className="table-th">Status</th>
                <th className="table-th">Joined</th>
                <th className="table-th w-12"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="py-16 text-center">
                    <Loader2 size={24} className="animate-spin text-slate-400 mx-auto" />
                  </td>
                </tr>
              ) : filteredMembers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-16 text-center">
                    <div className="text-slate-400">
                      <UserPlus size={32} className="mx-auto mb-3 opacity-40" />
                      <p className="text-sm font-medium">No employees found</p>
                      <p className="text-xs mt-1">Add your first employee to get started</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredMembers.map(m => (
                  <UserRow key={m.user_id} member={m} companyId={company.company_id}
                    onDelete={id => {
                      if (confirm('Remove this employee from the company?')) deleteUser.mutate(id)
                    }} />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showInvite && <InviteModal companyId={company.company_id} onClose={() => setShowInvite(false)} />}
    </div>
  )
}
