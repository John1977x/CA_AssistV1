import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { assignmentsApi, type AssignmentTemplate } from '@/api/assignments'
import { Search, Plus, ChevronRight, Loader, AlertCircle } from 'lucide-react'

export default function ManagerAssignTemplatesPage() {
  const navigate = useNavigate()
  const [templates, setTemplates] = useState<AssignmentTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setLoading(true)
        const response = await assignmentsApi.templates({ page: 1, page_size: 100 })
        setTemplates(response.items || [])
      } catch (err) {
        console.error('Failed to fetch templates:', err)
        setError('Failed to load assignment templates')
      } finally {
        setLoading(false)
      }
    }

    fetchTemplates()
  }, [])

  const getDifficultyColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'EASY':
        return 'bg-green-100 text-green-800'
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800'
      case 'HARD':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-slate-100 text-slate-800'
    }
  }

  const getDifficultyIcon = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'EASY':
        return '⭐'
      case 'MEDIUM':
        return '⭐⭐'
      case 'HARD':
        return '⭐⭐⭐'
      default:
        return '⭐'
    }
  }

  const categories = ['all', ...new Set(templates.map(t => t.category))]

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = categoryFilter === 'all' || template.category === categoryFilter
    return matchesSearch && matchesCategory
  })

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Assignment Templates</h1>
        <p className="text-slate-500 mt-2">Select a template and assign it to your employees</p>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="md:col-span-2 relative">
            <Search className="absolute left-3 top-3 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Search templates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Category Filter */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>
                {cat === 'all' ? 'All Categories' : cat}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader size={32} className="text-brand-600 animate-spin" />
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start gap-3">
            <AlertCircle size={20} className="text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-900">{error}</p>
              <p className="text-sm text-red-800 mt-1">Please try again later</p>
            </div>
          </div>
        ) : filteredTemplates.length === 0 ? (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-12 text-center">
            <p className="text-slate-500 text-lg">
              {templates.length === 0 ? 'No templates available' : 'No templates match your search'}
            </p>
          </div>
        ) : (
          filteredTemplates.map(template => (
            <div
              key={template.template_id}
              className="bg-white rounded-lg border border-slate-200 hover:border-blue-300 hover:shadow-lg transition-all overflow-hidden"
            >
              <div className="p-6">
                <div className="flex items-start justify-between gap-4">
                  {/* Left Content */}
                  <div className="flex-1">
                    {/* Title and Category */}
                    <div className="flex items-start gap-3 mb-3">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-slate-900">{template.title}</h3>
                        <div className="flex items-center gap-2 mt-2">
                          <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {template.category}
                          </span>
                          <span className={`inline-block px-2.5 py-1 rounded-full text-xs font-medium ${getDifficultyColor(template.difficulty_level)}`}>
                            {getDifficultyIcon(template.difficulty_level)} {template.difficulty_level}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Description */}
                    {template.description && (
                      <p className="text-slate-600 text-sm mb-4 line-clamp-2">
                        {template.description}
                      </p>
                    )}

                    {/* Steps and Details */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-sm font-semibold text-blue-600">{template.total_steps}</span>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500">Steps</p>
                          <p className="text-sm font-medium text-slate-900">Total {template.total_steps}</p>
                        </div>
                      </div>

                      {template.estimated_hours && (
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                            <span className="text-sm font-semibold text-green-600">⏱</span>
                          </div>
                          <div>
                            <p className="text-xs text-slate-500">Est. Time</p>
                            <p className="text-sm font-medium text-slate-900">{template.estimated_hours}h</p>
                          </div>
                        </div>
                      )}

                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                          <span className="text-sm font-semibold text-purple-600">📋</span>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500">Status</p>
                          <p className="text-sm font-medium text-slate-900">
                            {template.is_active ? 'Active' : 'Inactive'}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Steps Preview */}
                    {template.steps && template.steps.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-slate-200">
                        <p className="text-xs font-semibold text-slate-600 uppercase mb-3">Steps Overview</p>
                        <div className="space-y-2">
                          {template.steps.slice(0, 3).map((step, idx) => (
                            <div key={step.step_id} className="flex items-start gap-2">
                              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center">
                                <span className="text-xs font-semibold text-slate-600">{step.step_number}</span>
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-slate-900">{step.title}</p>
                                {step.description && (
                                  <p className="text-xs text-slate-500 line-clamp-1">{step.description}</p>
                                )}
                              </div>
                            </div>
                          ))}
                          {template.steps.length > 3 && (
                            <p className="text-xs text-slate-500 italic">+{template.steps.length - 3} more steps</p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Right Action */}
                  <div className="flex-shrink-0">
                    <button
                      onClick={() => navigate(`/manager/assign-template/${template.template_id}`)}
                      className="flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium whitespace-nowrap"
                    >
                      <Plus size={18} />
                      Assign
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
