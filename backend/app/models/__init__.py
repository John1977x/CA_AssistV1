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

from app.models.company import (
    TenantCompany,
    CustomerCompany,
    ClientDocument
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
    
    # Company models
    "TenantCompany",
    "CustomerCompany",
    "ClientDocument",
    
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
]
