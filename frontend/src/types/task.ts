export interface Task {
  task_id:                number
  tenant_id:              number
  customer_id:            number
  task_type_code:         string
  task_title:             string
  description:            string | null
  financial_year:         string | null
  return_period:          string | null
  due_date:               string
  internal_due_date:      string | null
  priority:               TaskPriority
  status:                 TaskStatus
  completion_percentage:  number
  billing_status:         BillingStatus
  billed_amount:          number | null
  estimated_hours:        number | null
  actual_hours:           number | null
  acknowledgement_number: string | null
  filed_at:               string | null
  tags:                   string[] | null
  branch_id:              number | null
  parent_task_id:         number | null
  created_at:             string
  updated_at:             string
  customer:               TaskCustomerBrief | null
  assigned_to:            TaskUserBrief | null
  reviewer:               TaskUserBrief | null
  details:                TaskStep[] | null
}

export interface TaskStep {
  task_detail_id:     number
  task_id:            number
  step_title:         string
  step_description:   string | null
  step_order:         number
  status:             StepStatus
  is_required:        boolean
  is_client_action:   boolean
  due_date:           string | null
  completed_at:       string | null
  notes_json:         StepNote[] | null
  form_data_json:     Record<string, any> | null
  attachments_json:   Attachment[] | null
  assigned_to:        TaskUserBrief | null
  completed_by:       TaskUserBrief | null
  created_at:         string
  updated_at:         string
}

export interface StepNote {
  user:      string
  text:      string
  timestamp: string
}

export interface Attachment {
  name: string
  url:  string
  type: string
}

export interface TaskUserBrief {
  user_id:      number
  display_name: string | null
  email:        string
}

export interface TaskCustomerBrief {
  customer_id:   number
  customer_code: string
  display_name:  string
  pan:           string | null
  phone:         string
}

export interface TaskStats {
  total:          number
  pending:        number
  in_progress:    number
  completed:      number
  overdue:        number
  due_today:      number
  due_this_week:  number
  by_status:      Record<string, number>
  by_priority:    Record<string, number>
  by_type:        Record<string, number>
}

export type TaskStatus    = 'PENDING' | 'IN_PROGRESS' | 'PENDING_DOCS' | 'UNDER_REVIEW' | 'COMPLETED' | 'FILED' | 'CANCELLED'
export type TaskPriority  = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
export type BillingStatus = 'UNBILLED' | 'INVOICED' | 'PAID'
export type StepStatus    = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'SKIPPED' | 'BLOCKED'

export const TASK_TYPE_LABELS: Record<string, string> = {
  GSTR1:            'GSTR-1',
  GSTR3B:           'GSTR-3B',
  GSTR9:            'GSTR-9 Annual',
  GSTR9C:           'GSTR-9C Reconciliation',
  ITR1:             'ITR-1 (Sahaj)',
  ITR2:             'ITR-2',
  ITR3:             'ITR-3',
  ITR4:             'ITR-4 (Sugam)',
  ITR5:             'ITR-5',
  ITR6:             'ITR-6',
  ITR7:             'ITR-7',
  TDS_RETURN_24Q:   'TDS Return 24Q',
  TDS_RETURN_26Q:   'TDS Return 26Q',
  TDS_RETURN_27Q:   'TDS Return 27Q',
  ROC_AOC4:         'ROC - AOC-4',
  ROC_MGT7:         'ROC - MGT-7',
  ROC_DIR3KYC:      'ROC - DIR-3 KYC',
  AUDIT_TAX:        'Tax Audit',
  AUDIT_STAT:       'Statutory Audit',
  AUDIT_INTERNAL:   'Internal Audit',
  PT_RETURN:        'PT Return',
  PF_RETURN:        'PF Return',
  ESIC_RETURN:      'ESIC Return',
  ADVANCE_TAX:      'Advance Tax',
  FORM_15CA:        'Form 15CA/CB',
  CUSTOM:           'Custom Task',
}

export const TASK_TYPE_GROUPS: Record<string, string[]> = {
  'GST':            ['GSTR1', 'GSTR3B', 'GSTR9', 'GSTR9C'],
  'Income Tax':     ['ITR1', 'ITR2', 'ITR3', 'ITR4', 'ITR5', 'ITR6', 'ITR7', 'ADVANCE_TAX', 'FORM_15CA'],
  'TDS':            ['TDS_RETURN_24Q', 'TDS_RETURN_26Q', 'TDS_RETURN_27Q'],
  'ROC / Company':  ['ROC_AOC4', 'ROC_MGT7', 'ROC_DIR3KYC'],
  'Audit':          ['AUDIT_TAX', 'AUDIT_STAT', 'AUDIT_INTERNAL'],
  'Payroll':        ['PT_RETURN', 'PF_RETURN', 'ESIC_RETURN'],
  'Other':          ['CUSTOM'],
}
