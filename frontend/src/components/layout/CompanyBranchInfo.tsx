import { Building2, GitBranch, MapPin, Briefcase } from 'lucide-react'
import { useAuthStoreV2 } from '@/store/authStoreV2'

export function CompanyBranchInfo() {
  const { company } = useAuthStoreV2()

  if (!company) return null

  const getRoleColor = (role: string) => {
    switch (role?.toUpperCase()) {
      case 'OWNER':
        return 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
      case 'MANAGER':
        return 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
      case 'EMPLOYEE':
        return 'bg-gradient-to-r from-green-500 to-emerald-500 text-white'
      case 'CLIENT':
        return 'bg-gradient-to-r from-orange-500 to-red-500 text-white'
      default:
        return 'bg-gradient-to-r from-slate-500 to-slate-600 text-white'
    }
  }

  return (
    <div className="bg-gradient-to-r from-slate-50 to-slate-100 border-b border-slate-200 px-4 lg:px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-6">
        {/* Company Section */}
        <div className="flex items-center gap-3 flex-1">
          <div className="p-2.5 bg-white rounded-lg shadow-sm border border-slate-200">
            <Building2 size={20} className="text-brand-600" />
          </div>
          <div className="flex-1">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Company</p>
            <p className="text-lg font-bold text-slate-900 truncate">{company.company_name}</p>
          </div>
        </div>

        {/* Divider */}
        <div className="hidden md:block h-12 w-px bg-gradient-to-b from-transparent via-slate-300 to-transparent" />

        {/* Branch Section */}
        <div className="flex items-center gap-3 flex-1">
          <div className="p-2.5 bg-white rounded-lg shadow-sm border border-slate-200">
            <MapPin size={20} className="text-brand-600" />
          </div>
          <div className="flex-1">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Branch</p>
            <p className="text-lg font-bold text-slate-900 truncate">
              {company.branch_name || 'Head Branch'}
            </p>
          </div>
        </div>

        {/* Role Badge */}
        <div className="flex items-center gap-2">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full font-semibold text-sm shadow-md ${getRoleColor(company.role)}`}>
            <Briefcase size={16} />
            <span>{company.role}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
