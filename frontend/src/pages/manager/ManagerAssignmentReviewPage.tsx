import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { assignmentsApi, type AssignmentDetail } from '@/api/assignments'
import { CheckCircle, Clock, AlertCircle, Loader, ChevronDown, ChevronUp, Download } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ManagerAssignmentReviewPage() {
  const { assignmentId } = useParams<{ assignmentId: string }>()
  const navigate = useNavigate()
  const [assignment, setAssignment] = useState<AssignmentDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedSubmissions, setExpandedSubmissions] = useState<Set<number>>(new Set())
  const [reviewingSubmissionId, setReviewingSubmissionId] = useState<number | null>(null)
  const [reviewData, setReviewData] = useState<{ [key: number]: { status: string; score: string; feedback: string } }>({})

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

  const toggleSubmission = (submissionId: number) => {
    const newExpanded = new Set(expandedSubmissions)
    if (newExpanded.has(submissionId)) {
      newExpanded.delete(submissionId)
    } else {
      newExpanded.add(submissionId)
    }
    setExpandedSubmissions(newExpanded)
  }

  const handleReviewSubmission = async (submissionId: number) => {
    if (!assignmentId || !reviewData[submissionId]) return

    try {
      setReviewingSubmissionId(submissionId)
      const data = reviewData[submissionId]
      
      await assignmentsApi.reviewSubmission(parseInt(assignmentId), submissionId, {
        status: data.status,
        score: parseFloat(data.score),
        feedback: data.feedback,
      })

      toast.success('Submission reviewed successfully!')

      // Refresh assignment data
      const updatedAssignment = await assignmentsApi.get(parseInt(assignmentId))
      setAssignment(updatedAssignment)

      // Clear review form
      setReviewData({ ...reviewData, [submissionId]: { status: '', score: '', feedback: '' } })
      setExpandedSubmissions(new Set())
    } catch (err) {
      console.error('Failed to review submission:', err)
      toast.error('Failed to review submission')
    } finally {
      setReviewingSubmissionId(null)
    }
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
          onClick={() => navigate('/manager/assignments')}
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
          <p className="text-slate-500 text-sm">Total Score</p>
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

      {/* Submissions */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Step Submissions</h2>

        {assignment.step_submissions.length === 0 ? (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-8 text-center">
            <p className="text-slate-500">No submissions yet</p>
          </div>
        ) : (
          assignment.step_submissions.map((submission) => {
            const isExpanded = expandedSubmissions.has(submission.submission_id)
            const step = assignment.template.steps.find(s => s.step_id === submission.step_id)

            return (
              <div key={submission.submission_id} className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                {/* Submission Header */}
                <button
                  onClick={() => toggleSubmission(submission.submission_id)}
                  className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
                >
                  <div className="flex items-center gap-4 flex-1">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(submission.status)}
                      <div className="text-left">
                        <p className="font-semibold text-slate-900">
                          Step {step?.step_number}: {step?.title}
                        </p>
                        <p className="text-sm text-slate-500">
                          Submitted: {new Date(submission.submitted_at).toLocaleDateString('en-IN')}
                        </p>
                      </div>
                    </div>
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(submission.status)}`}>
                      {submission.status}
                    </span>
                  </div>
                  {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </button>

                {/* Submission Content */}
                {isExpanded && (
                  <div className="px-6 py-4 border-t border-slate-200 bg-slate-50 space-y-4">
                    {/* Step Instructions */}
                    {step?.instructions && (
                      <div>
                        <p className="text-sm font-medium text-slate-900 mb-2">Instructions</p>
                        <p className="text-sm text-slate-600 whitespace-pre-wrap bg-white p-3 rounded border border-slate-200">
                          {step.instructions}
                        </p>
                      </div>
                    )}

                    {/* Submission Content */}
                    {submission.submission_text && (
                      <div>
                        <p className="text-sm font-medium text-slate-900 mb-2">Submission Text</p>
                        <p className="text-sm text-slate-600 whitespace-pre-wrap bg-white p-3 rounded border border-slate-200">
                          {submission.submission_text}
                        </p>
                      </div>
                    )}

                    {/* File */}
                    {submission.file_url && (
                      <div>
                        <p className="text-sm font-medium text-slate-900 mb-2">Uploaded File</p>
                        <a
                          href={submission.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 px-3 py-2 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 text-sm text-blue-600"
                        >
                          <Download size={16} />
                          {submission.file_name}
                        </a>
                      </div>
                    )}

                    {/* Previous Review */}
                    {submission.reviewed_at && (
                      <div className={`p-4 rounded-lg ${
                        submission.status === 'APPROVED' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                      }`}>
                        <p className={`text-sm font-medium mb-2 ${
                          submission.status === 'APPROVED' ? 'text-green-900' : 'text-red-900'
                        }`}>
                          {submission.status === 'APPROVED' ? '✓ Approved' : '✗ Rejected'}
                        </p>
                        {submission.score && (
                          <p className={`text-sm ${submission.status === 'APPROVED' ? 'text-green-800' : 'text-red-800'}`}>
                            Score: {submission.score}/100
                          </p>
                        )}
                        {submission.feedback && (
                          <p className={`text-sm mt-2 ${submission.status === 'APPROVED' ? 'text-green-800' : 'text-red-800'}`}>
                            Feedback: {submission.feedback}
                          </p>
                        )}
                      </div>
                    )}

                    {/* Review Form */}
                    {submission.status === 'PENDING' && (
                      <div className="bg-white border border-slate-200 rounded-lg p-4 space-y-4">
                        <p className="text-sm font-medium text-slate-900">Review Submission</p>

                        {/* Status */}
                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-2">Decision</label>
                          <select
                            value={reviewData[submission.submission_id]?.status || ''}
                            onChange={(e) => setReviewData({
                              ...reviewData,
                              [submission.submission_id]: {
                                ...reviewData[submission.submission_id],
                                status: e.target.value,
                              },
                            })}
                            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="">Select decision...</option>
                            <option value="APPROVED">Approve</option>
                            <option value="REJECTED">Reject</option>
                          </select>
                        </div>

                        {/* Score */}
                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-2">Score (0-100)</label>
                          <input
                            type="number"
                            min="0"
                            max="100"
                            value={reviewData[submission.submission_id]?.score || ''}
                            onChange={(e) => setReviewData({
                              ...reviewData,
                              [submission.submission_id]: {
                                ...reviewData[submission.submission_id],
                                score: e.target.value,
                              },
                            })}
                            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter score"
                          />
                        </div>

                        {/* Feedback */}
                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-2">Feedback</label>
                          <textarea
                            value={reviewData[submission.submission_id]?.feedback || ''}
                            onChange={(e) => setReviewData({
                              ...reviewData,
                              [submission.submission_id]: {
                                ...reviewData[submission.submission_id],
                                feedback: e.target.value,
                              },
                            })}
                            placeholder="Provide feedback..."
                            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            rows={3}
                          />
                        </div>

                        {/* Submit Button */}
                        <button
                          onClick={() => handleReviewSubmission(submission.submission_id)}
                          disabled={reviewingSubmissionId === submission.submission_id || !reviewData[submission.submission_id]?.status}
                          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-slate-400 transition-colors font-medium flex items-center justify-center gap-2"
                        >
                          {reviewingSubmissionId === submission.submission_id ? (
                            <>
                              <Loader size={16} className="animate-spin" />
                              Submitting...
                            </>
                          ) : (
                            'Submit Review'
                          )}
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
