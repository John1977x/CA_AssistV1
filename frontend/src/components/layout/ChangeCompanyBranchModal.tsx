import { useState } from 'react'
import { X, Building2, GitBranch } from 'lucide-react'
import { useAuthStoreV2 } from '@/store/authStoreV2'

interface ChangeCompanyBranchModalProps {
  isOpen: boolean
  onClose: () => void
}

export function ChangeCompanyBranchModal({ isOpen, onClose }: ChangeCompanyBranchModalProps) {
  const { company } = useAuthStoreV2()
  const [selectedCompany, setSelectedCompany] = useState(company?.company_id || '')
  const [selectedBranch, setSelectedBranch] = useState(company?.branch_id || '')

  // Mock data - replace with actual API calls
  const companies = [
    { id: company?.company_id, name: company?.company_name, code: company?.company_code }
  ]

  const branches = [
    { id: company?.branch_id, name: company?.branch_name || 'Head Office' }
  ]

  const handleSave = () => {
    // TODO: Implement API call to change company and branch
    console.log('Changing to company:', selectedCompany, 'branch:', selectedBranch)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />

      {/* Modal */}
      <div className="relative z-10 bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">Change Company & Branch</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-4">
          {/* Company Selection */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-2">
              <Building2 size={16} className="text-brand-600" />
              Company
            </label>
            <select
              value={selectedCompany}
              onChange={(e) => setSelectedCompany(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            >
              <option value="">Select Company</option>
              {companies.map(comp => (
                <option key={comp.id} value={comp.id}>
                  {comp.name} ({comp.code})
                </option>
              ))}
            </select>
          </div>

          {/* Branch Selection */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-2">
              <GitBranch size={16} className="text-brand-600" />
              Branch
            </label>
            <select
              value={selectedBranch}
              onChange={(e) => setSelectedBranch(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            >
              <option value="">Select Branch</option>
              {branches.map(branch => (
                <option key={branch.id} value={branch.id}>
                  {branch.name}
                </option>
              ))}
            </select>
          </div>

          {/* Info Message */}
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs text-blue-800">
              <strong>Note:</strong> Changing company or branch will update your workspace context and may affect your access to certain resources.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-200 bg-slate-50 rounded-b-lg">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 transition-colors"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  )
}
