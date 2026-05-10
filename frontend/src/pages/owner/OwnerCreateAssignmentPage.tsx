import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { assignmentsApi, type AssignmentTemplate } from '@/api/assignments'
import { Loader, AlertCircle, ChevronLeft, Calendar, Users } from 'lucide-react'
import toast from 'react-hot-toast'

export default function OwnerCreateAssignmentPage() {
  const { templateId } = useParams<{ templateId: string }>()
  const navigate = useNavigate()
  const [template, setTemplate] = useState<AssignmentTemplate | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [employees, setEmployees] = useState<any[]>([])
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>('')
  const [dueDate, setDueDate] = useState<string>('')
  const [title, setTitle] = useState<string>('')
  const [description, setDescription] = useState<string>('')

  useEffect(() => {
    const fetchTemplate = async () => {
      if (!templateId) return
      try {
        setLoading(true)
        const data = await assignmentsApi.getTemplate(parseInt(templateId))
        setTemplate(data)
        setTitle(data.title)
        setDescription(data.description || '')
        setError(null)
      } catch (err) {
        console.error('Failed to fetch template:', err)
        setError('Failed to load template')
      } finally {
        setLoading(false)
      }
    }

    fetchTemplate()
    // TODO: Fetch employees from API
    // For now, using mock data
    setEmployees([
      { id: 1, name: 'John Doe', email: 'john@example.com' },
      { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
      { id: 3, name: 'Mike Johnson', email: 'mike@example.com' },
      { id: 4, name: 'Sarah Williams', email: 'sarah@example.com' },
      { id: 5, name: 'Robert Brown', email: 'robert@example.com' },
    ])
  }, [templateId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedEmployeeId || !dueDate) {
      toast.error('Please select an employee and due date')
      return
    }

    try {
      setSubmitting(true)
      await assignmentsApi.create({
        template_id: parseInt(templateId!),
        assigned_to_user_id: parseInt(selectedEmployeeId),
        due_date: dueDate,
        title: title || template?.title,
        description: description || template?.description,
      })

      toast.success('Assignment created successfully!')
      navigate('/owner/assignments')
    } catch (err) {
      console.error('Failed to create assignment:', err)
      toast.error('Failed to create assignment')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <Loader size={32} className="text-brand-600 animate-spin" />
        </div>
      </div>
    )
  }

  if (error || !template) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start gap-3">
          <AlertCircle size={20} className="text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-900">{error || 'Template not found'}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <button
        onClick={() => navigate('/owner/assign-templates')}
        className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium mb-6"
      >
        <ChevronLeft size={18} />
        Back to Templates
      </button>

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Assign: {template.title}</h1>
        <p className="text-slate-500 mt-2">Select an employee and set the due date</p>
      </div>

      {/* Template Preview Card */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm text-slate-600 mb-1">Category</p>
            <p className="text-lg font-semibold text-slate-900">{template.category}</p>
          </div>
          <div>
            <p className="text-sm text-slate-600 mb-1">Difficulty</p>
            <p className="text-lg font-semibold text-slate-900">{template.difficulty_level}</p>
          </div>
          <div>
            <p className="text-sm text-slate-600 mb-1">Total Steps</p>
            <p className="text-lg font-semibold text-slate-900">{template.total_steps}</p>
          </div>
        </div>

        {template.description && (
          <div className="mt-4 pt-4 border-t border-blue-200">
            <p className="text-sm text-slate-600 mb-2">Description</p>
            <p className="text-slate-700">{template.description}</p>
          </div>
        )}

        {/* Steps */}
        {template.steps && template.steps.length > 0 && (
          <div className="mt-4 pt-4 border-t border-blue-200">
            <p className="text-sm font-semibold text-slate-700 mb-3">Steps</p>
            <div className="space-y-2">
              {template.steps.map((step) => (
                <div key={step.step_id} className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-white border-2 border-blue-400 flex items-center justify-center">
                    <span className="text-xs font-bold text-blue-600">{step.step_number}</span>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-slate-900">{step.title}</p>
                    {step.description && (
                      <p className="text-sm text-slate-600 mt-1">{step.description}</p>
                    )}
                    {step.instructions && (
                      <p className="text-xs text-slate-500 mt-1 italic">Instructions: {step.instructions}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Assignment Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-slate-200 p-8">
        <h2 className="text-xl font-bold text-slate-900 mb-6">Assignment Details</h2>

        <div className="space-y-6">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Assignment Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter assignment title"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter assignment description"
              rows={4}
            />
          </div>

          {/* Employee Selection */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
              <Users size={16} />
              Select Employee
            </label>
            <select
              value={selectedEmployeeId}
              onChange={(e) => setSelectedEmployeeId(e.target.value)}
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Choose an employee...</option>
              {employees.map(emp => (
                <option key={emp.id} value={emp.id}>
                  {emp.name} ({emp.email})
                </option>
              ))}
            </select>
          </div>

          {/* Due Date */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
              <Calendar size={16} />
              Due Date
            </label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        {/* Buttons */}
        <div className="flex gap-4 mt-8">
          <button
            type="button"
            onClick={() => navigate('/owner/assign-templates')}
            className="flex-1 px-4 py-2 border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors font-medium"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-slate-400 transition-colors font-medium"
          >
            {submitting ? 'Creating...' : 'Create Assignment'}
          </button>
        </div>
      </form>
    </div>
  )
}
