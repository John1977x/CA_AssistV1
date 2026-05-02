import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { customersApi } from '@/api/customers'
import { Modal, FormField } from '@/components/ui'
import type { Customer } from '@/types/customer'

const schema = z.object({
  customer_type:  z.string().default('INDIVIDUAL'),
  display_name:   z.string().min(2, 'Required'),
  legal_name:     z.string().optional(),
  pan:            z.string().regex(/^[A-Z]{5}[0-9]{4}[A-Z]$/, 'Invalid PAN').optional().or(z.literal('')),
  gstin:          z.string().optional(),
  email:          z.string().email('Invalid email').optional().or(z.literal('')),
  phone:          z.string().min(10, 'Valid phone required'),
  alternate_phone: z.string().optional(),
  whatsapp:       z.string().optional(),
  date_of_birth:  z.string().optional(),
  date_of_incorporation: z.string().optional(),
  source_channel: z.string().optional(),
  notes:          z.string().optional(),
})

type FormData = z.infer<typeof schema>

const CUSTOMER_TYPES = ['INDIVIDUAL', 'COMPANY', 'HUF', 'TRUST', 'LLP', 'PARTNERSHIP', 'AOP', 'BOI']
const SOURCE_CHANNELS = ['WALK_IN', 'WEBSITE', 'REFERRAL', 'SOCIAL_MEDIA', 'ADVERTISEMENT', 'OTHER']

interface Props {
  open:      boolean
  onClose:   () => void
  customer?: Customer | null   // null = create mode
}

export default function CustomerFormModal({ open, onClose, customer }: Props) {
  const qc = useQueryClient()
  const isEdit = !!customer

  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { customer_type: 'INDIVIDUAL' },
  })

  const customerType = watch('customer_type')
  const isCompany = !['INDIVIDUAL', 'HUF'].includes(customerType)

  useEffect(() => {
    if (customer) {
      reset({
        customer_type:  customer.customer_type,
        display_name:   customer.display_name,
        legal_name:     customer.legal_name || '',
        pan:            customer.pan || '',
        gstin:          customer.gstin || '',
        email:          customer.email || '',
        phone:          customer.phone,
        alternate_phone: customer.alternate_phone || '',
        whatsapp:       customer.whatsapp || '',
        date_of_birth:  customer.date_of_birth || '',
        date_of_incorporation: customer.date_of_incorporation || '',
        source_channel: customer.source_channel || '',
        notes:          customer.notes || '',
      })
    } else {
      reset({ customer_type: 'INDIVIDUAL' })
    }
  }, [customer, open])

  const mutation = useMutation({
    mutationFn: (data: FormData) => {
      const payload = { ...data, pan: data.pan?.toUpperCase() || undefined, gstin: data.gstin?.toUpperCase() || undefined }
      return isEdit
        ? customersApi.update(customer!.customer_id, payload)
        : customersApi.create(payload as any)
    },
    onSuccess: () => {
      toast.success(isEdit ? 'Customer updated.' : 'Customer added.')
      qc.invalidateQueries({ queryKey: ['customers'] })
      qc.invalidateQueries({ queryKey: ['customer-stats'] })
      onClose()
    },
  })

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? 'Edit Customer' : 'Add New Customer'}
      subtitle={isEdit ? `Editing ${customer?.display_name}` : 'Fill in the details to add a new client'}
      size="lg"
    >
      <form onSubmit={handleSubmit(d => mutation.mutate(d))} className="p-6 space-y-5">
        {/* Type + Name */}
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Client Type" required>
            <select {...register('customer_type')} className="input">
              {CUSTOMER_TYPES.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </FormField>

          <FormField label={isCompany ? 'Company Name' : 'Full Name'} error={errors.display_name?.message} required>
            <input {...register('display_name')} className={`input ${errors.display_name ? 'input-error' : ''}`}
              placeholder={isCompany ? 'e.g. ABC Pvt. Ltd.' : 'e.g. Rajesh Kumar'} />
          </FormField>
        </div>

        {isCompany && (
          <FormField label="Legal Registered Name">
            <input {...register('legal_name')} className="input" placeholder="Full legal name as per registration" />
          </FormField>
        )}

        {/* PAN + GSTIN */}
        <div className="grid grid-cols-2 gap-4">
          <FormField label="PAN" error={errors.pan?.message}
            hint="Format: ABCDE1234F">
            <input {...register('pan')} className={`input uppercase ${errors.pan ? 'input-error' : ''}`}
              placeholder="ABCDE1234F" maxLength={10} />
          </FormField>
          <FormField label="GSTIN">
            <input {...register('gstin')} className="input uppercase" placeholder="22ABCDE1234F1Z5" maxLength={15} />
          </FormField>
        </div>

        {/* Contact */}
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Mobile Number" error={errors.phone?.message} required>
            <input {...register('phone')} type="tel" className={`input ${errors.phone ? 'input-error' : ''}`}
              placeholder="9876543210" />
          </FormField>
          <FormField label="Alternate Phone">
            <input {...register('alternate_phone')} type="tel" className="input" placeholder="Optional" />
          </FormField>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <FormField label="Email Address" error={errors.email?.message}>
            <input {...register('email')} type="email" className={`input ${errors.email ? 'input-error' : ''}`}
              placeholder="client@example.com" />
          </FormField>
          <FormField label="WhatsApp Number">
            <input {...register('whatsapp')} type="tel" className="input" placeholder="If different from mobile" />
          </FormField>
        </div>

        {/* DOB / DOI */}
        <div className="grid grid-cols-2 gap-4">
          {!isCompany ? (
            <FormField label="Date of Birth">
              <input {...register('date_of_birth')} type="date" className="input" />
            </FormField>
          ) : (
            <FormField label="Date of Incorporation">
              <input {...register('date_of_incorporation')} type="date" className="input" />
            </FormField>
          )}
          <FormField label="Source Channel">
            <select {...register('source_channel')} className="input">
              <option value="">Select source...</option>
              {SOURCE_CHANNELS.map(s => (
                <option key={s} value={s}>{s.replace('_', ' ')}</option>
              ))}
            </select>
          </FormField>
        </div>

        {/* Notes */}
        <FormField label="Internal Notes">
          <textarea {...register('notes')} rows={3} className="input resize-none"
            placeholder="Any notes about this client..." />
        </FormField>

        {/* Actions */}
        <div className="flex gap-3 pt-2 border-t border-slate-100">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">
            Cancel
          </button>
          <button type="submit" disabled={mutation.isPending} className="btn-primary flex-1">
            {mutation.isPending
              ? <><Loader2 size={14} className="animate-spin" /> Saving...</>
              : isEdit ? 'Save Changes' : 'Add Customer'
            }
          </button>
        </div>
      </form>
    </Modal>
  )
}
