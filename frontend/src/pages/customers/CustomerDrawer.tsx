import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Phone, Mail, MapPin, Building2, CreditCard, ShieldCheck,
  Edit2, Trash2, FileText, Calendar, Tag, User, AlertTriangle,
  CheckCircle, Clock, XCircle,
} from 'lucide-react'
import { customersApi } from '@/api/customers'
import { Drawer, StatusBadge, Tabs, SectionHeader } from '@/components/ui'
import type { Customer } from '@/types/customer'
import toast from 'react-hot-toast'
import clsx from 'clsx'

const KYC_ICON: Record<string, React.ReactNode> = {
  VERIFIED:  <CheckCircle size={14} className="text-green-600" />,
  PENDING:   <Clock size={14} className="text-yellow-600" />,
  REJECTED:  <XCircle size={14} className="text-red-600" />,
  EXPIRED:   <AlertTriangle size={14} className="text-red-600" />,
}

function InfoRow({ label, value, icon }: { label: string; value?: string | null; icon?: React.ReactNode }) {
  if (!value) return null
  return (
    <div className="flex items-start gap-3 py-2.5 border-b border-slate-50 last:border-0">
      {icon && <span className="text-slate-400 mt-0.5 flex-shrink-0">{icon}</span>}
      <div className="flex-1 min-w-0">
        <p className="text-xs text-slate-400 mb-0.5">{label}</p>
        <p className="text-sm text-slate-900 font-medium truncate">{value}</p>
      </div>
    </div>
  )
}

interface Props {
  customerId: number | null
  onClose:    () => void
  onEdit:     (c: Customer) => void
}

export default function CustomerDrawer({ customerId, onClose, onEdit }: Props) {
  const qc = useQueryClient()
  const [tab, setTab] = useState('overview')

  const { data: customer, isLoading } = useQuery({
    queryKey: ['customer', customerId],
    queryFn: () => customersApi.get(customerId!),
    enabled: !!customerId,
  })

  const updateKyc = useMutation({
    mutationFn: (status: string) => customersApi.updateKyc(customerId!, status),
    onSuccess: () => {
      toast.success('KYC status updated.')
      qc.invalidateQueries({ queryKey: ['customer', customerId] })
      qc.invalidateQueries({ queryKey: ['customers'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => customersApi.delete(customerId!),
    onSuccess: () => {
      toast.success('Customer deleted.')
      qc.invalidateQueries({ queryKey: ['customers'] })
      onClose()
    },
  })

  return (
    <Drawer
      open={!!customerId}
      onClose={onClose}
      title={customer?.display_name || 'Loading...'}
      subtitle={customer ? `${customer.customer_code} · ${customer.customer_type}` : ''}
      width="lg"
    >
      {isLoading ? (
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin w-8 h-8 border-2 border-brand-600 border-t-transparent rounded-full" />
        </div>
      ) : customer ? (
        <div>
          {/* Action bar */}
          <div className="flex items-center gap-2 px-6 py-3 bg-slate-50 border-b border-slate-100">
            <button onClick={() => onEdit(customer)} className="btn-secondary btn-sm">
              <Edit2 size={13} /> Edit
            </button>
            <div className="flex-1" />
            <select
              value={customer.kyc_status}
              onChange={e => updateKyc.mutate(e.target.value)}
              className="text-xs border border-slate-200 rounded-lg px-2 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              {['PENDING', 'VERIFIED', 'EXPIRED', 'REJECTED'].map(s => (
                <option key={s} value={s}>KYC: {s}</option>
              ))}
            </select>
            <button
              onClick={() => {
                if (confirm(`Delete ${customer.display_name}?`)) deleteMutation.mutate()
              }}
              className="btn-danger btn-sm"
            >
              <Trash2 size={13} />
            </button>
          </div>

          {/* Status chips */}
          <div className="flex flex-wrap items-center gap-2 px-6 py-3 border-b border-slate-100">
            <StatusBadge status={customer.status} />
            <div className="flex items-center gap-1">
              {KYC_ICON[customer.kyc_status]}
              <StatusBadge status={customer.kyc_status} />
            </div>
            {customer.risk_level && <StatusBadge status={customer.risk_level} label={`Risk: ${customer.risk_level}`} />}
            {customer.tags?.map(t => (
              <span key={t} className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                <Tag size={10} />{t}
              </span>
            ))}
          </div>

          {/* Tabs */}
          <div className="px-6 pt-4">
            <Tabs
              tabs={[
                { key: 'overview', label: 'Overview' },
                { key: 'address', label: 'Address & Bank' },
                { key: 'compliance', label: 'Compliance' },
                { key: 'notes', label: 'Notes' },
              ]}
              active={tab}
              onChange={setTab}
            />
          </div>

          <div className="px-6 py-4">
            {tab === 'overview' && (
              <div className="space-y-1">
                <SectionHeader title="Contact Information" />
                <InfoRow label="Phone" value={customer.phone} icon={<Phone size={14} />} />
                <InfoRow label="Alternate Phone" value={customer.alternate_phone} icon={<Phone size={14} />} />
                <InfoRow label="WhatsApp" value={customer.whatsapp} icon={<Phone size={14} />} />
                <InfoRow label="Email" value={customer.email} icon={<Mail size={14} />} />

                <div className="pt-4">
                  <SectionHeader title="Identity & Tax" />
                  <InfoRow label="PAN" value={customer.pan} icon={<CreditCard size={14} />} />
                  <InfoRow label="GSTIN" value={customer.gstin} icon={<FileText size={14} />} />
                  <InfoRow label="Legal Name" value={customer.legal_name} icon={<Building2 size={14} />} />
                </div>

                <div className="pt-4">
                  <SectionHeader title="Account Details" />
                  <InfoRow label="Client Code" value={customer.customer_code} icon={<Tag size={14} />} />
                  <InfoRow label="Source Channel" value={customer.source_channel?.replace('_', ' ')} icon={<User size={14} />} />
                  <InfoRow label="Onboarded" value={customer.onboarded_at ? new Date(customer.onboarded_at).toLocaleDateString('en-IN') : null} icon={<Calendar size={14} />} />
                  {customer.assigned_user && (
                    <InfoRow
                      label="Assigned To"
                      value={customer.assigned_user.display_name || customer.assigned_user.email}
                      icon={<User size={14} />}
                    />
                  )}
                </div>
              </div>
            )}

            {tab === 'address' && (
              <div className="space-y-1">
                {customer.details ? (
                  <>
                    <SectionHeader title="Registered Address" />
                    <InfoRow label="Address Line 1" value={customer.details.registered_address_line1} icon={<MapPin size={14} />} />
                    <InfoRow label="Address Line 2" value={customer.details.registered_address_line2} />
                    <InfoRow label="City" value={customer.details.registered_city} />
                    <InfoRow label="State" value={customer.details.registered_state} />
                    <InfoRow label="PIN Code" value={customer.details.registered_pincode} />

                    <div className="pt-4">
                      <SectionHeader title="Bank Details" />
                      <InfoRow label="Bank Name" value={customer.details.bank_name} icon={<Building2 size={14} />} />
                      <InfoRow label="Account Number" value={customer.details.bank_account_number ? '••••' + customer.details.bank_account_number.slice(-4) : null} />
                      <InfoRow label="IFSC Code" value={customer.details.bank_ifsc} />
                      <InfoRow label="Account Type" value={customer.details.bank_account_type} />
                    </div>
                  </>
                ) : (
                  <p className="text-slate-400 text-sm text-center py-8">No address details added yet.</p>
                )}
              </div>
            )}

            {tab === 'compliance' && (
              <div className="space-y-1">
                <SectionHeader title="GST & Tax Details" />
                {customer.details ? (
                  <>
                    <InfoRow label="Income Tax Status" value={customer.details.income_tax_status} />
                    <InfoRow label="GST Registration Type" value={customer.details.gst_registration_type} />
                    <InfoRow label="GST Registration Date" value={customer.details.gst_registration_date
                      ? new Date(customer.details.gst_registration_date).toLocaleDateString('en-IN') : null} />
                    <InfoRow label="TDS Deductor Type" value={customer.details.tds_deductor_type} />

                    {customer.details.director_partners_json?.length ? (
                      <div className="pt-4">
                        <SectionHeader title="Directors / Partners" />
                        <div className="space-y-2">
                          {customer.details.director_partners_json.map((d, i) => (
                            <div key={i} className="bg-slate-50 rounded-lg p-3 text-sm">
                              <p className="font-medium text-slate-900">{d.name}</p>
                              <div className="flex gap-3 mt-1 text-xs text-slate-500">
                                {d.din && <span>DIN: {d.din}</span>}
                                {d.pan && <span>PAN: {d.pan}</span>}
                                {d.share_pct && <span>Share: {d.share_pct}%</span>}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                  </>
                ) : (
                  <p className="text-slate-400 text-sm text-center py-8">No compliance details added yet.</p>
                )}
              </div>
            )}

            {tab === 'notes' && (
              <div>
                <SectionHeader title="Internal Notes" />
                {customer.notes ? (
                  <div className="bg-yellow-50 border border-yellow-100 rounded-xl p-4 text-sm text-slate-700 whitespace-pre-wrap">
                    {customer.notes}
                  </div>
                ) : (
                  <p className="text-slate-400 text-sm text-center py-8">No notes added for this client.</p>
                )}
              </div>
            )}
          </div>
        </div>
      ) : null}
    </Drawer>
  )
}
