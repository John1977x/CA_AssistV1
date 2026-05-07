import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, GitBranch, AlertCircle, ChevronDown } from 'lucide-react'
import toast from 'react-hot-toast'
import { companiesApi } from '@/api/companies'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import { BranchFormModal } from './BranchFormModal'

interface Branch {
  branch_id: string
  branch_name: string
  branch_code: string
  email?: string
  phone?: string
  city?: string
  state?: string
  is_head_office: boolean
  status: string
  created_at: string
}

interface Company {
  company_id: string
  company_name: string
}

export default function OwnerBranchPage() {
  const { company: currentCompany } = useAuthStoreV2()
  const [companies, setCompanies] = useState<Company[]>([])
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>('')
  const [branches, setBranches] = useState<Branch[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingBranch, setEditingBranch] = useState<Branch | null>(null)

  useEffect(() => {
    loadCompanies()
  }, [])

  useEffect(() => {
    if (selectedCompanyId) {
      loadBranches()
    }
  }, [selectedCompanyId])

  const loadCompanies = async () => {
    try {
      setLoading(true)
      const data = await companiesApi.listCompanies()
      setCompanies(data)
      // Set default to current company or first company
      if (currentCompany?.company_id) {
        setSelectedCompanyId(currentCompany.company_id)
      } else if (data.length > 0) {
        setSelectedCompanyId(data[0].company_id)
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load companies')
    } finally {
      setLoading(false)
    }
  }

  const loadBranches = async () => {
    if (!selectedCompanyId) return

    try {
      setLoading(true)
      const data = await companiesApi.listBranches(selectedCompanyId)
      setBranches(data)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load branches')
    } finally {
      setLoading(false)
    }
  }

  const handleAddBranch = () => {
    setEditingBranch(null)
    setModalOpen(true)
  }

  const handleEditBranch = (branch: Branch) => {
    setEditingBranch(branch)
    setModalOpen(true)
  }

  const handleDeleteBranch = async (branchId: string) => {
    if (!window.confirm('Are you sure you want to delete this branch?')) return

    try {
      await companiesApi.deleteBranch(selectedCompanyId, branchId)
      setBranches(branches.filter(b => b.branch_id !== branchId))
      toast.success('Branch deleted successfully')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete branch')
    }
  }

  const handleSaveBranch = async () => {
    await loadBranches()
    setModalOpen(false)
    setEditingBranch(null)
  }

  const selectedCompany = companies.find(c => c.company_id === selectedCompanyId)

  if (loading && companies.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-600">Loading branches...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <GitBranch size={28} className="text-brand-600" />
            Branches
          </h1>
          <p className="text-slate-600 mt-1">Manage branches for your companies</p>
        </div>
        {selectedCompanyId && (
          <button
            onClick={handleAddBranch}
            className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors"
          >
            <Plus size={20} />
            Add Branch
          </button>
        )}
      </div>

      {/* Company Selector */}
      {companies.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Select Company
          </label>
          <div className="relative">
            <select
              value={selectedCompanyId}
              onChange={(e) => setSelectedCompanyId(e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 appearance-none bg-white"
            >
              {companies.map(company => (
                <option key={company.company_id} value={company.company_id}>
                  {company.company_name}
                </option>
              ))}
            </select>
            <ChevronDown size={20} className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 pointer-events-none" />
          </div>
        </div>
      )}

      {/* Current Company Info */}
      {selectedCompany && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle size={20} className="text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-blue-900">Selected Company</p>
            <p className="text-sm text-blue-800">
              Viewing branches for <strong>{selectedCompany.company_name}</strong>
            </p>
          </div>
        </div>
      )}

      {/* Branches List */}
      {!selectedCompanyId ? (
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-12 text-center">
          <GitBranch size={48} className="mx-auto text-slate-400 mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">No companies available</h3>
          <p className="text-slate-600">Create a company first to add branches</p>
        </div>
      ) : branches.length === 0 ? (
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-12 text-center">
          <GitBranch size={48} className="mx-auto text-slate-400 mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">No branches yet</h3>
          <p className="text-slate-600 mb-6">Create your first branch for this company</p>
          <button
            onClick={handleAddBranch}
            className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors"
          >
            <Plus size={20} />
            Create Branch
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {branches.map(branch => (
            <div
              key={branch.branch_id}
              className="bg-white border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-slate-900">{branch.branch_name}</h3>
                    <span className="px-2 py-1 bg-slate-100 text-slate-700 text-xs font-medium rounded">
                      {branch.branch_code}
                    </span>
                    {branch.is_head_office && (
                      <span className="px-2 py-1 bg-brand-100 text-brand-700 text-xs font-medium rounded">
                        Head Office
                      </span>
                    )}
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      branch.status === 'ACTIVE'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {branch.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm text-slate-600 mt-3">
                    {branch.email && (
                      <div>
                        <span className="font-medium">Email:</span> {branch.email}
                      </div>
                    )}
                    {branch.phone && (
                      <div>
                        <span className="font-medium">Phone:</span> {branch.phone}
                      </div>
                    )}
                    {branch.city && (
                      <div>
                        <span className="font-medium">City:</span> {branch.city}
                      </div>
                    )}
                    {branch.state && (
                      <div>
                        <span className="font-medium">State:</span> {branch.state}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => handleEditBranch(branch)}
                    className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                    title="Edit branch"
                  >
                    <Edit2 size={18} />
                  </button>
                  <button
                    onClick={() => handleDeleteBranch(branch.branch_id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete branch"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {selectedCompanyId && (
        <BranchFormModal
          isOpen={modalOpen}
          onClose={() => {
            setModalOpen(false)
            setEditingBranch(null)
          }}
          branch={editingBranch}
          companyId={selectedCompanyId}
          onSave={handleSaveBranch}
        />
      )}
    </div>
  )
}
