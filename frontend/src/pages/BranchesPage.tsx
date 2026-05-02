import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Plus, Search, Trash2, Edit2, MapPin, Phone, Mail, MoreVertical,
  Loader2, Building2, ChevronLeft, ChevronRight, RefreshCw, Check,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { branchesApi } from '@/api/users'
import type { Branch, BranchCreateForm } from '@/types/auth'
import clsx from 'clsx'

const branchSchema = z.object({
  branch_name: z.string().min(2, 'Branch name required'),
  branch_code: z.string().min(2, 'Branch code required'),
  email: z.string().email('Valid email').optional().or(z.literal('')),
  phone: z.string().optional(),
  address_line1: z.string().optional(),
  address_line2: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  pincode: z.string().optional(),
  gstin: z.string().optional(),
  is_head_office: z.boolean().optional(),
})

type BranchFormData = z.infer<typeof branchSchema>

function CreateBranchModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const { register, handleSubmit, watch, formState: { errors } } = useForm<BranchFormData>({
    resolver: zodResolver(branchSchema),
  })

  const isHeadOffice = watch('is_head_office')

  const create = useMutation({
    mutationFn: (data: BranchCreateForm) => branchesApi.create(data),
    onSuccess: () => {
      toast.success('Branch created successfully!')
      qc.invalidateQueries({ queryKey: ['branches'] })
      onClose()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create branch')
    },
  })

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-slate-100 px-6 py-4 flex items-center justify-between rounded-t-2xl">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Create New Branch</h2>
            <p className="text-sm text-slate-500">Add a new office location</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl font-medium">✕</button>
        </div>

        <form onSubmit={handleSubmit(d => create.mutate(d as BranchCreateForm))} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Branch Name *</label>
              <input
                {...register('branch_name')}
                className={`input ${errors.branch_name ? 'input-error' : ''}`}
                placeholder="Main Office"
              />
              {errors.branch_name && <p className="mt-1 text-xs text-red-600">{errors.branch_name.message}</p>}
            </div>
            <div>
              <label className="label">Branch Code *</label>
              <input
                {...register('branch_code')}
                className={`input ${errors.branch_code ? 'input-error' : ''}`}
                placeholder="HO"
              />
              {errors.branch_code && <p className="mt-1 text-xs text-red-600">{errors.branch_code.message}</p>}
            </div>
          </div>

          <div>
            <label className="label">Email Address</label>
            <input
              {...register('email')}
              type="email"
              className="input"
              placeholder="branch@firm.com"
            />
          </div>

          <div>
            <label className="label">Phone Number</label>
            <input
              {...register('phone')}
              type="tel"
              className="input"
              placeholder="9876543210"
            />
          </div>

          <div>
            <label className="label">Address Line 1</label>
            <input
              {...register('address_line1')}
              className="input"
              placeholder="Street address"
            />
          </div>

          <div>
            <label className="label">Address Line 2</label>
            <input
              {...register('address_line2')}
              className="input"
              placeholder="Apartment, suite, etc."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">City</label>
              <input
                {...register('city')}
                className="input"
                placeholder="Mumbai"
              />
            </div>
            <div>
              <label className="label">State</label>
              <input
                {...register('state')}
                className="input"
                placeholder="Maharashtra"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Pincode</label>
              <input
                {...register('pincode')}
                className="input"
                placeholder="400001"
              />
            </div>
            <div>
              <label className="label">GSTIN</label>
              <input
                {...register('gstin')}
                className="input"
                placeholder="27AABCT1234H1Z0"
              />
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                {...register('is_head_office')}
                className="w-4 h-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
              />
              <div>
                <p className="font-medium text-slate-900 text-sm">Set as Head Office</p>
                <p className="text-xs text-slate-600 mt-0.5">This will be your primary office location</p>
              </div>
            </label>
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={create.isPending} className="btn-primary flex-1">
              {create.isPending ? <><Loader2 size={14} className="animate-spin" /> Creating...</> : <><Plus size={14} /> Create Branch</>}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function BranchRow({ branch, onDelete }: { branch: Branch; onDelete: (id: number) => void }) {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <tr className="hover:bg-slate-50 transition-colors">
      <td className="table-td">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-brand-100 flex items-center justify-center text-brand-800">
            <Building2 size={18} />
          </div>
          <div>
            <div className="font-medium text-slate-900 text-sm flex items-center gap-2">
              {branch.branch_name}
              {branch.is_head_office && <span className="badge-blue text-xs">Head Office</span>}
            </div>
            <div className="text-xs text-slate-500">{branch.branch_code}</div>
          </div>
        </div>
      </td>
      <td className="table-td">
        <div className="space-y-1">
          {branch.city && <div className="text-sm text-slate-600">{branch.city}</div>}
          {branch.state && <div className="text-xs text-slate-500">{branch.state}</div>}
        </div>
      </td>
      <td className="table-td">
        {branch.email ? (
          <div className="flex items-center gap-2 text-slate-600">
            <Mail size={14} className="text-slate-400" />
            <span className="text-sm">{branch.email}</span>
          </div>
        ) : (
          <span className="text-slate-300">—</span>
        )}
      </td>
      <td className="table-td">
        {branch.phone ? (
          <div className="flex items-center gap-2 text-slate-600">
            <Phone size={14} className="text-slate-400" />
            <span className="text-sm">{branch.phone}</span>
          </div>
        ) : (
          <span className="text-slate-300">—</span>
        )}
      </td>
      <td className="table-td">
        <span className={branch.is_active ? 'badge-green' : 'badge-gray'}>
          {branch.is_active ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td className="table-td">
        <div className="relative">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            <MoreVertical size={15} />
          </button>
          {menuOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 top-8 z-20 bg-white border border-slate-200 rounded-xl shadow-lg w-44 py-1">
                <button className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50">
                  <Edit2 size={13} /> Edit Branch
                </button>
                {!branch.is_head_office && (
                  <button
                    onClick={() => { onDelete(branch.branch_id); setMenuOpen(false) }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <Trash2 size={13} /> Delete Branch
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

export default function BranchesPage() {
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [search, setSearch] = useState('')

  const { data: branches = [], isLoading, isFetching } = useQuery({
    queryKey: ['branches'],
    queryFn: () => branchesApi.list(),
  })

  const deleteBranch = useMutation({
    mutationFn: (id: number) => {
      // Note: branchesApi doesn't have delete method yet, this is for future implementation
      return Promise.reject(new Error('Delete not yet implemented'))
    },
    onSuccess: () => {
      toast.success('Branch deleted.')
      qc.invalidateQueries({ queryKey: ['branches'] })
    },
  })

  const filteredBranches = branches.filter(b =>
    b.branch_name.toLowerCase().includes(search.toLowerCase()) ||
    b.branch_code.toLowerCase().includes(search.toLowerCase()) ||
    b.city?.toLowerCase().includes(search.toLowerCase())
  )

  const headOffice = branches.find(b => b.is_head_office)
  const otherBranches = branches.filter(b => !b.is_head_office)

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Office Branches</h1>
          <p className="text-sm text-slate-500 mt-0.5">{branches.length} branch{branches.length !== 1 ? 'es' : ''} in your firm</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary">
          <Plus size={15} /> Create Branch
        </button>
      </div>

      {/* Head Office Card */}
      {headOffice && (
        <div className="mb-6 bg-gradient-to-br from-brand-50 to-brand-100 border border-brand-200 rounded-2xl p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-brand-600 flex items-center justify-center text-white">
                <Building2 size={24} />
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="text-lg font-bold text-slate-900">{headOffice.branch_name}</h2>
                  <span className="badge-blue text-xs">Head Office</span>
                </div>
                <p className="text-sm text-slate-600 mb-3">{headOffice.branch_code}</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  {headOffice.city && (
                    <div>
                      <p className="text-xs text-slate-500 mb-1">City</p>
                      <p className="text-sm font-medium text-slate-900">{headOffice.city}</p>
                    </div>
                  )}
                  {headOffice.state && (
                    <div>
                      <p className="text-xs text-slate-500 mb-1">State</p>
                      <p className="text-sm font-medium text-slate-900">{headOffice.state}</p>
                    </div>
                  )}
                  {headOffice.email && (
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Email</p>
                      <p className="text-sm font-medium text-slate-900">{headOffice.email}</p>
                    </div>
                  )}
                  {headOffice.phone && (
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Phone</p>
                      <p className="text-sm font-medium text-slate-900">{headOffice.phone}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
            <span className="badge-green text-xs">Active</span>
          </div>
        </div>
      )}

      {/* Search */}
      <div className="card p-4 mb-5">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search by branch name, code, or city..."
              className="input pl-9"
            />
          </div>
          <button
            onClick={() => qc.invalidateQueries({ queryKey: ['branches'] })}
            className={clsx('btn-ghost', isFetching && 'opacity-50')}
          >
            <RefreshCw size={15} className={isFetching ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Branches Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="table-th">Branch</th>
                <th className="table-th">Location</th>
                <th className="table-th">Email</th>
                <th className="table-th">Phone</th>
                <th className="table-th">Status</th>
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
              ) : filteredBranches.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-16 text-center">
                    <div className="text-slate-400">
                      <Building2 size={32} className="mx-auto mb-3 opacity-40" />
                      <p className="text-sm font-medium">No branches found</p>
                      <p className="text-xs mt-1">Create your first branch to get started</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredBranches.map(b => (
                  <BranchRow
                    key={b.branch_id}
                    branch={b}
                    onDelete={id => {
                      if (confirm('Delete this branch?')) deleteBranch.mutate(id)
                    }}
                  />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Stats */}
      {branches.length > 0 && (
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="card p-4">
            <p className="text-xs text-slate-500 mb-1">Total Branches</p>
            <p className="text-2xl font-bold text-slate-900">{branches.length}</p>
          </div>
          <div className="card p-4">
            <p className="text-xs text-slate-500 mb-1">Active Branches</p>
            <p className="text-2xl font-bold text-green-600">{branches.filter(b => b.is_active).length}</p>
          </div>
          <div className="card p-4">
            <p className="text-xs text-slate-500 mb-1">Head Office</p>
            <p className="text-2xl font-bold text-brand-600">{headOffice ? headOffice.branch_name : 'Not set'}</p>
          </div>
        </div>
      )}

      {showCreate && <CreateBranchModal onClose={() => setShowCreate(false)} />}
    </div>
  )
}
