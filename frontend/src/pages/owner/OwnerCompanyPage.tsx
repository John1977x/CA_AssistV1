import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, Building2, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { companiesApi } from '@/api/companies'
import { useAuthStoreV2 } from '@/store/authStoreV2'
import { CompanyFormModal } from './CompanyFormModal'

interface Company {
  company_id: string
  company_name: string
  company_code: string
  email?: string
  phone?: string
  city?: string
  state?: string
  status: string
  created_at: string
}

export default function OwnerCompanyPage() {
  const { company: currentCompany } = useAuthStoreV2()
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingCompany, setEditingCompany] = useState<Company | null>(null)

  useEffect(() => {
    loadCompanies()
  }, [])

  const loadCompanies = async () => {
    try {
      setLoading(true)
      const data = await companiesApi.listCompanies()
      setCompanies(data)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load companies')
    } finally {
      setLoading(false)
    }
  }

  const handleAddCompany = () => {
    setEditingCompany(null)
    setModalOpen(true)
  }

  const handleEditCompany = (company: Company) => {
    setEditingCompany(company)
    setModalOpen(true)
  }

  const handleDeleteCompany = async (companyId: string) => {
    if (!window.confirm('Are you sure you want to delete this company?')) return

    try {
      await companiesApi.deleteCompany(companyId)
      setCompanies(companies.filter(c => c.company_id !== companyId))
      toast.success('Company deleted successfully')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete company')
    }
  }

  const handleSaveCompany = async () => {
    await loadCompanies()
    setModalOpen(false)
    setEditingCompany(null)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-600">Loading companies...</p>
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
            <Building2 size={28} className="text-brand-600" />
            Companies
          </h1>
          <p className="text-slate-600 mt-1">Manage your companies and their details</p>
        </div>
        <button
          onClick={handleAddCompany}
          className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors"
        >
          <Plus size={20} />
          Add Company
        </button>
      </div>

      {/* Current Company Info */}
      {currentCompany && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle size={20} className="text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-blue-900">Current Company</p>
            <p className="text-sm text-blue-800">
              You are currently working with <strong>{currentCompany.company_name}</strong>
            </p>
          </div>
        </div>
      )}

      {/* Companies List */}
      {companies.length === 0 ? (
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-12 text-center">
          <Building2 size={48} className="mx-auto text-slate-400 mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">No companies yet</h3>
          <p className="text-slate-600 mb-6">Create your first company to get started</p>
          <button
            onClick={handleAddCompany}
            className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors"
          >
            <Plus size={20} />
            Create Company
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {companies.map(company => (
            <div
              key={company.company_id}
              className="bg-white border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-slate-900">{company.company_name}</h3>
                    <span className="px-2 py-1 bg-slate-100 text-slate-700 text-xs font-medium rounded">
                      {company.company_code}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      company.status === 'ACTIVE'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {company.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm text-slate-600 mt-3">
                    {company.email && (
                      <div>
                        <span className="font-medium">Email:</span> {company.email}
                      </div>
                    )}
                    {company.phone && (
                      <div>
                        <span className="font-medium">Phone:</span> {company.phone}
                      </div>
                    )}
                    {company.city && (
                      <div>
                        <span className="font-medium">City:</span> {company.city}
                      </div>
                    )}
                    {company.state && (
                      <div>
                        <span className="font-medium">State:</span> {company.state}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => handleEditCompany(company)}
                    className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                    title="Edit company"
                  >
                    <Edit2 size={18} />
                  </button>
                  <button
                    onClick={() => handleDeleteCompany(company.company_id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete company"
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
      <CompanyFormModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false)
          setEditingCompany(null)
        }}
        company={editingCompany}
        onSave={handleSaveCompany}
      />
    </div>
  )
}
