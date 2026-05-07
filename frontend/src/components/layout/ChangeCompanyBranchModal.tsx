import { useState, useEffect } from 'react'
import { X, Building2, GitBranch, ChevronDown } from 'lucide-react'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import { authV2Api } from '@/api/authV2'
import { companiesApi } from '@/api/companies'
import toast from 'react-hot-toast'

interface Company {
  company_id: string
  company_name: string
  company_code: string
}

interface Branch {
  branch_id: string
  branch_name: string
  branch_code: string
  is_head_office: boolean
}

interface ChangeCompanyBranchModalProps {
  isOpen: boolean
  onClose: () => void
}

export function ChangeCompanyBranchModal({ isOpen, onClose }: ChangeCompanyBranchModalProps) {
  const { company: currentCompany, setCompany } = useAuthStoreV2()
  const [companies, setCompanies] = useState<Company[]>([])
  const [branches, setBranches] = useState<Branch[]>([])
  const [selectedCompany, setSelectedCompany] = useState(currentCompany?.company_id || '')
  const [selectedBranch, setSelectedBranch] = useState(currentCompany?.branch_id || '')
  const [loading, setLoading] = useState(false)
  const [loadingCompanies, setLoadingCompanies] = useState(false)
  const [loadingBranches, setLoadingBranches] = useState(false)

  // Load companies when modal opens
  useEffect(() => {
    if (isOpen) {
      loadCompanies()
    }
  }, [isOpen])

  // Load branches when company changes
  useEffect(() => {
    if (selectedCompany && selectedCompany !== 'default-company') {
      loadBranches()
    }
  }, [selectedCompany])

  const loadCompanies = async () => {
    try {
      setLoadingCompanies(true)
      const data = await companiesApi.listCompanies()
      setCompanies(data)
      // Set first company if current company is invalid (like 'default-company')
      if ((!selectedCompany || selectedCompany === 'default-company') && data.length > 0) {
        setSelectedCompany(data[0].company_id)
      }
    } catch (error: any) {
      toast.error('Failed to load companies')
      console.error(error)
    } finally {
      setLoadingCompanies(false)
    }
  }

  const loadBranches = async () => {
    if (!selectedCompany) return

    try {
      setLoadingBranches(true)
      const data = await companiesApi.listBranches(selectedCompany)
      setBranches(data)
      if (!selectedBranch && data.length > 0) {
        setSelectedBranch(data[0].branch_id)
      }
    } catch (error: any) {
      toast.error('Failed to load branches')
      console.error(error)
    } finally {
      setLoadingBranches(false)
    }
  }

  const handleCompanyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCompany(e.target.value)
    setSelectedBranch('') // Reset branch when company changes
  }

  const handleSave = async () => {
    if (!selectedCompany) {
      toast.error('Please select a company')
      return
    }

    setLoading(true)
    try {
      const response = await authV2Api.changeCompanyBranch({
        company_id: selectedCompany,
        branch_id: selectedBranch || null,
      })

      // Update auth store with new company info
      setCompany(response.company)
      
      toast.success('Company and branch changed successfully')
      onClose()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to change company/branch')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  const selectedCompanyData = companies.find(c => c.company_id === selectedCompany)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />

      {/* Modal */}
      <div className="relative z-10 bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 sticky top-0 bg-white">
          <h2 className="text-lg font-semibold text-slate-900">Switch Company & Branch</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-6">
          {/* Company Selection */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-3">
              <Building2 size={16} className="text-brand-600" />
              Select Company
            </label>
            <div className="relative">
              <select
                value={selectedCompany}
                onChange={handleCompanyChange}
                disabled={loadingCompanies || loading}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent disabled:bg-slate-100 disabled:cursor-not-allowed appearance-none bg-white"
              >
                <option value="">Select a company...</option>
                {companies.map(comp => (
                  <option key={comp.company_id} value={comp.company_id}>
                    {comp.company_name} ({comp.company_code})
                  </option>
                ))}
              </select>
              <ChevronDown size={20} className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 pointer-events-none" />
            </div>
            {loadingCompanies && (
              <p className="text-xs text-slate-500 mt-2">Loading companies...</p>
            )}
          </div>

          {/* Companies List */}
          {companies.length > 0 && (
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-slate-900 mb-3">Your Companies</h3>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {companies.map(comp => (
                  <div
                    key={comp.company_id}
                    onClick={() => setSelectedCompany(comp.company_id)}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedCompany === comp.company_id
                        ? 'bg-brand-100 border border-brand-300'
                        : 'bg-white border border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Building2 size={16} className="text-brand-600 flex-shrink-0" />
                      <div>
                        <p className="font-medium text-slate-900">{comp.company_name}</p>
                        <p className="text-xs text-slate-500">{comp.company_code}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Branch Selection */}
          {selectedCompanyData && (
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-3">
                <GitBranch size={16} className="text-brand-600" />
                Select Branch for {selectedCompanyData.company_name}
              </label>
              <div className="relative">
                <select
                  value={selectedBranch}
                  onChange={(e) => setSelectedBranch(e.target.value)}
                  disabled={loadingBranches || loading}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent disabled:bg-slate-100 disabled:cursor-not-allowed appearance-none bg-white"
                >
                  <option value="">Head Branch (No specific branch)</option>
                  {branches.map(branch => (
                    <option key={branch.branch_id} value={branch.branch_id}>
                      {branch.branch_name} ({branch.branch_code})
                      {branch.is_head_office ? ' - Head Office' : ''}
                    </option>
                  ))}
                </select>
                <ChevronDown size={20} className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 pointer-events-none" />
              </div>
              {loadingBranches && (
                <p className="text-xs text-slate-500 mt-2">Loading branches...</p>
              )}
            </div>
          )}

          {/* Branches List */}
          {selectedCompanyData && branches.length > 0 && (
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-slate-900 mb-3">Branches</h3>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {/* Head Branch Option */}
                <div
                  onClick={() => setSelectedBranch('')}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedBranch === ''
                      ? 'bg-brand-100 border border-brand-300'
                      : 'bg-white border border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <GitBranch size={16} className="text-brand-600 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="font-medium text-slate-900">Head Branch</p>
                      <p className="text-xs text-slate-500">No specific branch assigned</p>
                    </div>
                  </div>
                </div>

                {/* Other Branches */}
                {branches.map(branch => (
                  <div
                    key={branch.branch_id}
                    onClick={() => setSelectedBranch(branch.branch_id)}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedBranch === branch.branch_id
                        ? 'bg-brand-100 border border-brand-300'
                        : 'bg-white border border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <GitBranch size={16} className="text-brand-600 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="font-medium text-slate-900">{branch.branch_name}</p>
                        <p className="text-xs text-slate-500">{branch.branch_code}</p>
                      </div>
                      {branch.is_head_office && (
                        <span className="px-2 py-1 bg-brand-100 text-brand-700 text-xs font-medium rounded">
                          HO
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Info Message */}
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs text-blue-800">
              <strong>Note:</strong> Changing company or branch will update your workspace context and may affect your access to certain resources.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-200 bg-slate-50 rounded-b-lg sticky bottom-0">
          <button
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={loading || !selectedCompany}
            className="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Switching...
              </>
            ) : (
              'Switch Company'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
