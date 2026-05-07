import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { FileText, Send, Loader2, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { companiesApi } from '@/api/companies'
import { useAuthStoreV2 } from '@/store/authStoreV2'

const DOCUMENT_OPTIONS = [
  { value: 'PAN', label: 'PAN Certificate' },
  { value: 'TAN', label: 'TAN Certificate' },
  { value: 'COMPANY_ESTABLISHED_DATE', label: 'Company Established Date' },
  { value: 'GST', label: 'GST Certificate' },
  { value: 'CIN', label: 'CIN Certificate' },
  { value: 'UDYAM', label: 'Udyam Registration' },
  { value: 'IEC', label: 'IEC Code' },
  { value: 'OTHER', label: 'Other Document' },
]

interface DocumentRequestFormProps {
  clientId: string
  onClose?: () => void
}

export default function DocumentRequestForm({ clientId, onClose }: DocumentRequestFormProps) {
  const qc = useQueryClient()
  const { company } = useAuthStoreV2()
  const [selectedDocs, setSelectedDocs] = useState<string[]>([])
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState('NORMAL')

  const createRequest = useMutation({
    mutationFn: () =>
      companiesApi.createDocumentRequest(company!.company_id, clientId, {
        document_types: selectedDocs,
        description: description || undefined,
        priority,
      }),
    onSuccess: () => {
      toast.success('Document request submitted successfully!')
      setSelectedDocs([])
      setDescription('')
      setPriority('NORMAL')
      qc.invalidateQueries({ queryKey: ['documentRequests'] })
      onClose?.()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to submit request')
    },
  })

  const toggleDocument = (docType: string) => {
    setSelectedDocs((prev) =>
      prev.includes(docType) ? prev.filter((d) => d !== docType) : [...prev, docType]
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (selectedDocs.length === 0) {
      toast.error('Please select at least one document')
      return
    }
    createRequest.mutate()
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FileText className="text-brand-600" size={24} />
          <h3 className="text-lg font-bold text-slate-900">Request Documents</h3>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X size={20} />
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Document Selection */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-3">
            Select Documents *
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {DOCUMENT_OPTIONS.map((doc) => (
              <label key={doc.value} className="flex items-center gap-2 p-2 rounded hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedDocs.includes(doc.value)}
                  onChange={() => toggleDocument(doc.value)}
                  className="w-4 h-4 rounded border-slate-300 text-brand-600"
                />
                <span className="text-sm text-slate-700">{doc.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Priority</label>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="LOW">Low</option>
            <option value="NORMAL">Normal</option>
            <option value="URGENT">Urgent</option>
          </select>
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Additional Notes</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add any additional details or context..."
            rows={3}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none"
          />
        </div>

        {/* Submit Button */}
        <div className="flex gap-2 pt-2">
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={createRequest.isPending || selectedDocs.length === 0}
            className="flex-1 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {createRequest.isPending ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <Send size={16} />
                Submit Request
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
