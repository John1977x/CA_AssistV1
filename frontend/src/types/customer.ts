export interface Customer {
  customer_id:            number
  tenant_id:              number
  customer_code:          string
  customer_type:          CustomerType
  display_name:           string
  legal_name:             string | null
  pan:                    string | null
  gstin:                  string | null
  email:                  string | null
  phone:                  string
  alternate_phone:        string | null
  whatsapp:               string | null
  date_of_birth:          string | null
  date_of_incorporation:  string | null
  industry_code:          string | null
  source_channel:         string | null
  tags:                   string[] | null
  portal_access:          boolean
  status:                 CustomerStatus
  risk_level:             RiskLevel | null
  kyc_status:             KYCStatus
  kyc_verified_at:        string | null
  onboarded_at:           string | null
  notes:                  string | null
  branch_id:              number | null
  assigned_user_id:       number | null
  referred_by_customer_id: number | null
  created_at:             string
  updated_at:             string
  assigned_user:          AssignedUserBrief | null
  details:                CustomerDetails | null
}

export interface CustomerDetails {
  customer_detail_id:         number
  customer_id:                number
  registered_address_line1:   string | null
  registered_address_line2:   string | null
  registered_city:            string | null
  registered_state:           string | null
  registered_pincode:         string | null
  communication_address:      string | null
  bank_name:                  string | null
  bank_account_number:        string | null
  bank_ifsc:                  string | null
  bank_account_type:          string | null
  income_tax_status:          string | null
  gst_registration_type:      string | null
  gst_registration_date:      string | null
  gst_cancellation_date:      string | null
  tds_deductor_type:          string | null
  director_partners_json:     DirectorPartner[] | null
  custom_fields_json:         Record<string, any> | null
  updated_at:                 string
}

export interface DirectorPartner {
  name:       string
  din?:       string
  pan?:       string
  share_pct?: number
}

export interface AssignedUserBrief {
  user_id:      number
  display_name: string | null
  email:        string
}

export type CustomerType   = 'INDIVIDUAL' | 'COMPANY' | 'HUF' | 'TRUST' | 'LLP' | 'PARTNERSHIP' | 'AOP' | 'BOI'
export type CustomerStatus = 'ACTIVE' | 'INACTIVE' | 'PROSPECT' | 'CHURNED'
export type KYCStatus      = 'PENDING' | 'VERIFIED' | 'EXPIRED' | 'REJECTED'
export type RiskLevel      = 'LOW' | 'MEDIUM' | 'HIGH'

export interface CustomerStats {
  total:       number
  active:      number
  kyc_pending: number
  by_type:     Record<string, number>
}

// ── Enquiry ──────────────────────────────────────────────────────────────────

export interface Enquiry {
  enquiry_id:             number
  tenant_id:              number
  enquiry_number:         string
  enquiry_date:           string
  full_name:              string
  email:                  string | null
  phone:                  string
  company_name:           string | null
  service_interested:     string[] | null
  source:                 string | null
  message:                string | null
  estimated_value:        number | null
  status:                 EnquiryStatus
  follow_up_date:         string | null
  follow_up_notes:        string | null
  lost_reason:            string | null
  is_converted:           boolean
  converted_customer_id:  number | null
  converted_at:           string | null
  branch_id:              number | null
  assigned_to_user_id:    number | null
  referred_by_customer_id: number | null
  assigned_to_user:       AssignedUserBrief | null
  created_at:             string
  updated_at:             string
}

export type EnquiryStatus = 'NEW' | 'IN_PROGRESS' | 'PROPOSAL_SENT' | 'WON' | 'LOST' | 'DEFERRED'

export interface EnquiryStats {
  total:      number
  new:        number
  converted:  number
  by_status:  Record<string, number>
}
