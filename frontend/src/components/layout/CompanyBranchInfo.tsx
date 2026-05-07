import { Building2, GitBranch } from 'lucide-react'
import { useAuthStoreV2 } from '@/store/authStoreV2'

export function CompanyBranchInfo() {
  const { company } = useAuthStoreV2()

  if (!company) return null

  return (
    <div className="flex items-center gap-4 px-4 py-2 bg-slate-50 border-b border-slate-200 text-sm">
      {/* Company Info */}
      <div className="flex items-center gap-2 text-slate-700">
        <Building2 size={16} className="text-brand-600 flex-shrink-0" />
        <div className="flex flex-col">
          <span className="text-xs text-slate-500 font-medium">Company</span>
          <span className="font-medium text-slate-900">{company.company_name}</span>
        </div>
      </div>

      {/* Divider */}
      <div className="h-6 w-px bg-slate-300" />

      {/* Branch Info */}
      <div className="flex items-center gap-2 text-slate-700">
        <GitBranch size={16} className="text-brand-600 flex-shrink-0" />
        <div className="flex flex-col">
          <span className="text-xs text-slate-500 font-medium">Branch</span>
          <span className="font-medium text-slate-900">
            {company.branch_name || 'Head Branch'}
          </span>
        </div>
      </div>

      {/* Role Badge */}
      <div className="ml-auto">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-brand-100 text-brand-800">
          {company.role}
        </span>
      </div>
    </div>
  )
}
