# Import all models for Alembic to detect them
from app.models.auth import (
    Subscription,
    SubscriptionHistory,
    Tenant,
    UserRole,
    Branch,
    User,
    UserLog
)

from app.models.customer import (
    Customer,
    CustomerDetails,
    Enquiry
)

from app.models.task import (
    Task,
    TaskDetail,
    TaskReminder
)

from app.models.billing import (
    Invoice,
    InvoiceLineItem,
    TimeLog,
    Expense,
    PaymentReceived
)

from app.models.events import (
    CustomerEvent,
    CustomerEventNotification
)

from app.models.communication import (
    EmailTemplate,
    EmailQueue,
    EmailLog,
    EmailScheduler,
    WATemplate,
    WAQueue,
    WALog,
    WAScheduler
)

from app.models.subscription import (
    CAPlan,
    CASubscription,
    ClientPlan,
    ClientSubscription,
    ClientInvoice
)

from app.models.accounts import (
    AccountHead,
    AccountTransaction,
    AccountLedger
)

from app.models.social import (
    SocialAccount,
    SocialPostTemplate,
    SocialPost,
    SocialScheduler
)

from app.models.ticket import (
    Ticket,
    TicketComment
)

from app.models.assignment import (
    AssignmentTemplate,
    AssignmentTemplateStep,
    Assignment,
    AssignmentStepSubmission
)

from app.models.compliance import (
    Compliance,
    ComplianceTask,
    ComplianceHistory,
    ComplianceReminder
)

# Note: Deprecated models removed
# - company.py (replaced by company_v2.py)
# - tenant_companies, customer_companies, client_documents tables removed

__all__ = [
    # Auth models
    "Subscription",
    "SubscriptionHistory",
    "Tenant",
    "UserRole",
    "Branch",
    "User",
    "UserLog",
    
    # Customer models
    "Customer",
    "CustomerDetails",
    "Enquiry",
    
    # Task models
    "Task",
    "TaskDetail",
    "TaskReminder",
    
    # Billing models
    "Invoice",
    "InvoiceLineItem",
    "TimeLog",
    "Expense",
    "PaymentReceived",
    
    # Event models
    "CustomerEvent",
    "CustomerEventNotification",
    
    # Communication models
    "EmailTemplate",
    "EmailQueue",
    "EmailLog",
    "EmailScheduler",
    "WATemplate",
    "WAQueue",
    "WALog",
    "WAScheduler",
    
    # Subscription models
    "CAPlan",
    "CASubscription",
    "ClientPlan",
    "ClientSubscription",
    "ClientInvoice",
    
    # Accounting models
    "AccountHead",
    "AccountTransaction",
    "AccountLedger",
    
    # Social media models
    "SocialAccount",
    "SocialPostTemplate",
    "SocialPost",
    "SocialScheduler",
    
    # Ticket models
    "Ticket",
    "TicketComment",
    
    # Assignment models
    "AssignmentTemplate",
    "AssignmentTemplateStep",
    "Assignment",
    "AssignmentStepSubmission",
    
    # Compliance models
    "Compliance",
    "ComplianceTask",
    "ComplianceHistory",
    "ComplianceReminder",
]
