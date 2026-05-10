import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { assignmentsApi, type AssignmentDetail, type AssignmentStepSubmission } from '@/api/assignments'
import { CheckCircle, Clock, AlertCircle, Upload, Loader, ChevronDown, ChevronUp } from 'lucide-react'
import toast from 'react-hot-toast'

export default function EmployeeAssignmentDetailPage() {
  const { assignmentId } = useParams<{ assignmentId: string }>()
  const navigate = useNavigate()
  const [assignment, setAssignment] = useState<AssignmentDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set())
  const [submittingStepId, setSubmittingStepId] = useState<number | null>(null)
  const [submissionText, setSubmissionText] = useState<{ [key: number]: string }>({})
  const [selectedFiles, setSelectedFiles] = useState<{ [key: number]: File | null }>({})

  useEffect(() => {
    const fetchAssignment = async () => {
      if (!assignmentId) return
      try {
        setLoading(true)
        const data = await assignmentsApi.get(parseInt(assignmentId))
        setAssignment(data)
        setError(null)
      } catch (err) {
        console.error('Failed to fetch assignment:', err)
        setError('Failed to load assignment')
      } finally {
        setLoading(false)
      }
    }

    fetchAssignment()
  }, [assignmentId])

  const toggleStep = (stepId: number) => {
    const newExpanded = new Set(expandedSteps)
    if (newExpanded.has(stepId)) {
      newExpanded.delete(stepId)
    } else {
      newExpanded.add(stepId)
    }
    setExpandedSteps(newExpanded)
  }

  const getSubmissionStatus = (stepId: number): AssignmentStepSubmission | undefined => {
    return assignment?.step_submissions.find(s => s.step_id === stepId)
  }

  const getStatusColor = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'APPROVED':
        return 'bg-green-100 text-green-800'
      case 'REJECTED':
        return 'bg-red-100 text-red-800'
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'APPROVED':
        return <CheckCircle size={18} className="text-green-600" />
      case 'REJECTED':
        return <AlertCircle size={18} className="text-red-600" />
      case 'PENDING':
        return <Clock size={18} className="text-yellow-600" />
      default:
        return null
    }
  }

  const handleSubmitStep = async (stepId: number) => {
    if (!assignmentId) return

    try {
      setSubmittingStepId(stepId)
      const formData = new FormData()
      
      if (submissionText[stepId]) {
        formData.append('submission_text', submissionText[stepId])
      }
      
      if (selectedFiles[stepId]) {
        formData.append('file', selectedFiles[stepId]!)
      }

      await assignmentsApi.submitStep(parseInt(assignmentId), stepId, formData)
      
      toast.success('Step submitted successfully!')
      
      // Refresh assignment data
      const updatedAssignment = await assignmentsApi.get(parseInt(assignmentId))
      setAssignment(updatedAssignment)
      
      // Clear form
      setSubmissionText({ ...submissionText, [stepId]: '' })
      setSelectedFiles({ ...selectedFiles, [stepId]: null })
    } catch (err) {
      console.error('Failed to submit step:', err)
      toast.error('Failed to submit step')
    } finally {
      setSubmittingStepId(null)
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

  if (error || !assignment) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="bg-red-50 text-red-700 p-4 rounded-lg">
          {error || 'Assignment not found'}
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/employee/assignments')}
          className="text-blue-600 hover:text-blue-700 text-sm font-medium mb-4"
        >
          ← Back to Assignments
        </button>
        <h1 className="text-3xl font-bold text-slate-900">{assignment.title}</h1>
        <p className="text-slate-500 mt-2">{assignment.description}</p>
      </div>

      {/* Assignment Info */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-slate-500 text-sm">Due Date</p>
          <p className="text-lg font-semibold text-slate-900 mt-1">
            {new Date(assignment.due_date).toLocaleDateString('en-IN')}
          </p>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-slate-500 text-sm">Progress</p>
          <p className="text-lg font-semibold text-slate-900 mt-1">{assignment.completion_percentage}%</p>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-slate-500 text-sm">Score</p>
          <p className="text-lg font-semibold text-slate-900 mt-1">
            {assignment.total_score ? `${assignment.total_score}/100` : '-'}
          </p>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <p className="text-slate-500 text-sm">Status</p>
          <p className={`text-lg font-semibold mt-1 ${
            assignment.status?.toUpperCase() === 'APPROVED' ? 'text-green-600' :
            assignment.status?.toUpperCase() === 'REJECTED' ? 'text-red-600' :
            'text-yellow-600'
          }`}>
            {assignment.status?.replace(/_/g, ' ')}
          </p>
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Assignment Steps</h2>
        
        {assignment.template.steps.map((step) => {
          const submission = getSubmissionStatus(step.step_id)
          const isExpanded = expandedSteps.has(step.step_id)
          
          return (
            <div key={step.step_id} className="bg-white rounded-lg border border-slate-200 overflow-hidden">
              {/* Step Header */}
              <button
                onClick={() => toggleStep(step.step_id)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-4 flex-1">
                  <div className="flex items-center gap-3">
                    {submission ? getStatusIcon(submission.status) : <AlertCircle size={18} className="text-slate-400" />}
                    <div className="text-left">
                      <p className="font-semibold text-slate-900">Step {step.step_number}: {step.title}</p>
                      {submission && (
                        <p className="text-sm text-slate-500">
                          Submitted: {new Date(submission.submitted_at).toLocaleDateString('en-IN')}
                        </p>
                      )}
                    </div>
                  </div>
                  {submission && (
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(submission.status)}`}>
                      {submission.status}
                    </span>
                  )}
                </div>
                {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
              </button>

              {/* Step Content */}
              {isExpanded && (
                <div className="px-6 py-4 border-t border-slate-200 bg-slate-50">
                  {step.description && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-slate-900 mb-2">Description</p>
                      <p className="text-sm text-slate-600">{step.description}</p>
                    </div>
                  )}

                  {step.instructions && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-slate-900 mb-2">Instructions</p>
                      <p className="text-sm text-slate-600 whitespace-pre-wrap">{step.instructions}</p>
                    </div>
                  )}

                  {submission && submission.status === 'APPROVED' ? (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <p className="text-sm font-medium text-green-900 mb-2">✓ Approved</p>
                      {submission.score && (
                        <p className="text-sm text-green-800">Score: {submission.score}/100</p>
                      )}
                      {submission.feedback && (
                        <p className="text-sm text-green-800 mt-2">Feedback: {submission.feedback}</p>
                      )}
                    </div>
                  ) : submission && submission.status === 'REJECTED' ? (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                      <p className="text-sm font-medium text-red-900 mb-2">✗ Rejected</p>
                      {submission.feedback && (
                        <p className="text-sm text-red-800">Feedback: {submission.feedback}</p>
                      )}
                    </div>
                  ) : null}

                  {(!submission || submission.status === 'REJECTED') && (
                    <div className="bg-white border border-slate-200 rounded-lg p-4">
                      <p className="text-sm font-medium text-slate-900 mb-4">Submit Your Work</p>
                      
                      {/* Text Input */}
                      <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                          Submission Text (Optional)
                        </label>
                        <textarea
                          value={submissionText[step.step_id] || ''}
                          onChange={(e) => setSubmissionText({ ...submissionText, [step.step_id]: e.target.value })}
                          placeholder="Enter your submission text here..."
                          className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          rows={4}
                        />
                      </div>

                      {/* File Upload */}
                      <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                          Upload File (Optional)
                        </label>
                        <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:border-slate-400 transition-colors">
                          <input
                            type="file"
                            onChange={(e) => setSelectedFiles({ ...selectedFiles, [step.step_id]: e.target.files?.[0] || null })}
                            className="hidden"
                            id={`file-${step.step_id}`}
                          />
                          <label htmlFor={`file-${step.step_id}`} className="cursor-pointer">
                            <Upload size={24} className="mx-auto text-slate-400 mb-2" />
                            <p className="text-sm text-slate-600">
                              {selectedFiles[step.step_id]?.name || 'Click to upload or drag and drop'}
                            </p>
                          </label>
                        </div>
                      </div>

                      {/* Submit Button */}
                      <button
                        onClick={() => handleSubmitStep(step.step_id)}
                        disabled={submittingStepId === step.step_id}
                        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-slate-400 transition-colors font-medium flex items-center justify-center gap-2"
                      >
                        {submittingStepId === step.step_id ? (
                          <>
                            <Loader size={16} className="animate-spin" />
                            Submitting...
                          </>
                        ) : (
                          <>
                            <Upload size={16} />
                            Submit Step
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
