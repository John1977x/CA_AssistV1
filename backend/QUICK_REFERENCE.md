# Quick Reference - New Database Tables

## Table Overview by Module

### 🏢 Company Management

#### TenantCompany
Companies owned/managed by the CA firm itself.
```python
from app.models import TenantCompany

company = TenantCompany(
    company_code="TC001",
    tenant_id=1,
    company_name="ABC Chartered Accountants LLP",
    status='Y'
)
```

#### CustomerCompany
Companies owned by customers (clients).
```python
from app.models import CustomerCompany

company = CustomerCompany(
    company_code="CC001",
    customer_id=1,
    tenant_id=1,
    company_name="XYZ Industries Pvt Ltd",
    company_type="PRIVATE_LIMITED",
    cin="U12345MH2020PTC123456",
    pan="ABCDE1234F",
    gstin="27ABCDE1234F1Z5",
    is_primary=True
)
```

#### ClientDocument
Documents for customers and their companies.
```python
from app.models import ClientDocument

doc = ClientDocument(
    customer_id=1,
    company_id=company.company_id,  # Optional
    tenant_id=1,
    document_type="PAN",
    document_number="ABCDE1234F",
    document_name="PAN Card.pdf",
    url="s3://bucket/docs/pan_123.pdf",
    status="Active"
)
```

### 🎂 Event Management

#### CustomerEvent
Track birthdays, anniversaries, and custom events.
```python
from app.models import CustomerEvent
from datetime import date

event = CustomerEvent(
    customer_id=1,
    tenant_id=1,
    event_type="BIRTHDAY",
    event_date=date(1990, 5, 15),
    recurring_yearly=True,
    is_active=True
)
```

#### CustomerEventNotification
Notifications for events.
```python
from app.models import CustomerEventNotification
from datetime import datetime

notification = CustomerEventNotification(
    event_id=event.event_id,
    customer_id=1,
    tenant_id=1,
    channel="EMAIL",
    template_id=email_template.template_id,
    scheduled_at=datetime(2024, 5, 15, 9, 0),
    status="Pending"
)
```

### 📧 Email System

#### EmailTemplate
Reusable email templates with variables.
```python
from app.models import EmailTemplate

template = EmailTemplate(
    tenant_id=1,
    template_name="Welcome Email",
    template_code="WELCOME_EMAIL",
    subject="Welcome to {{company_name}}!",
    body_html="<p>Dear {{customer_name}},</p><p>Welcome!</p>",
    variables_json={"customer_name": "string", "company_name": "string"},
    category="Onboarding",
    is_active=True
)
```

#### EmailQueue
Queue emails for sending.
```python
from app.models import EmailQueue

email = EmailQueue(
    tenant_id=1,
    template_id=template.template_id,
    from_email="noreply@cafirm.com",
    to_email="customer@example.com",
    subject="Welcome!",
    body_html="<p>Rendered HTML</p>",
    priority="NORMAL",
    status="Queued"
)
```

### 💬 WhatsApp System

#### WATemplate
WhatsApp message templates (must be approved by Meta).
```python
from app.models import WATemplate

wa_template = WATemplate(
    tenant_id=1,
    template_name="Task Reminder",
    template_code="TASK_REMINDER",
    language="en",
    category="UTILITY",
    body_text="Hi {{1}}, your task {{2}} is due on {{3}}.",
    status="APPROVED"
)
```

#### WAQueue
Queue WhatsApp messages.
```python
from app.models import WAQueue

wa_msg = WAQueue(
    tenant_id=1,
    wa_template_id=wa_template.wa_template_id,
    to_phone="919876543210",
    variables_json={"1": "John", "2": "GST Filing", "3": "2024-05-31"},
    status="Queued"
)
```

### 💳 Subscription Management

#### CAPlan
Subscription plans for CA firms.
```python
from app.models import CAPlan

plan = CAPlan(
    plan_name="Professional",
    plan_code="CA_PRO",
    price_monthly=2999.00,
    price_yearly=29999.00,
    gst_pct=18.00,
    max_clients=200,
    max_users=10,
    max_storage_gb=50,
    features_json={"whatsapp": True, "social_media": True},
    is_active=True
)
```

#### CASubscription
Active subscriptions for CA firms.
```python
from app.models import CASubscription
from datetime import date

subscription = CASubscription(
    tenant_id=1,
    ca_plan_id=plan.ca_plan_id,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    billing_cycle="YEARLY",
    amount=29999.00,
    gst_amount=5399.82,
    total_amount=35398.82,
    payment_status="Paid",
    status="Active",
    auto_renew=True
)
```

#### ClientPlan
Service plans that CAs offer to their clients.
```python
from app.models import ClientPlan

client_plan = ClientPlan(
    tenant_id=1,
    plan_name="GST Compliance Package",
    plan_code="GST_BASIC",
    price_monthly=5000.00,
    price_yearly=50000.00,
    gst_pct=18.00,
    services_included=["GSTR1", "GSTR3B", "Annual Return"],
    max_documents=100,
    is_active=True
)
```

#### ClientSubscription
Client subscriptions to service plans.
```python
from app.models import ClientSubscription

client_sub = ClientSubscription(
    tenant_id=1,
    customer_id=1,
    client_plan_id=client_plan.client_plan_id,
    start_date=date(2024, 4, 1),
    end_date=date(2025, 3, 31),
    billing_cycle="YEARLY",
    amount=50000.00,
    gst_amount=9000.00,
    total_amount=59000.00,
    payment_status="Paid",
    status="Active"
)
```

### 💰 Accounting Module

#### AccountHead
Chart of accounts.
```python
from app.models import AccountHead

account = AccountHead(
    tenant_id=1,
    head_name="Professional Fees",
    head_code="INC-001",
    head_type="INCOME",
    head_sub_type="SERVICE_FEES",
    is_system=False,
    is_active=True
)
```

#### AccountTransaction
Financial transactions.
```python
from app.models import AccountTransaction
from datetime import date

txn = AccountTransaction(
    tenant_id=1,
    account_head_id=account.account_head_id,
    ref_type="TASK_PAYMENT",
    ref_id="123",
    financial_year="2024-25",
    txn_date=date(2024, 4, 15),
    amount=10000.00,
    txn_type="CREDIT",
    currency="INR",
    description="Payment for GST filing",
    created_by=1,
    status="Posted"
)
```

### 📱 Social Media

#### SocialAccount
Connected social media accounts.
```python
from app.models import SocialAccount

social = SocialAccount(
    tenant_id=1,
    platform="LINKEDIN",
    account_name="ABC Chartered Accountants",
    account_handle="@abc_ca",
    access_token="encrypted_token",
    status="Active"
)
```

#### SocialPost
Social media posts.
```python
from app.models import SocialPost
from datetime import datetime

post = SocialPost(
    tenant_id=1,
    social_account_id=social.social_account_id,
    content_text="Important tax deadline reminder! #GST #TaxCompliance",
    scheduled_at=datetime(2024, 5, 1, 10, 0),
    status="Scheduled"
)
```

## Common Queries

### Get all companies for a customer
```python
from app.models import CustomerCompany

companies = db.query(CustomerCompany).filter(
    CustomerCompany.customer_id == customer_id,
    CustomerCompany.status == 'Y'
).all()
```

### Get upcoming birthdays
```python
from app.models import CustomerEvent
from datetime import date

today = date.today()
events = db.query(CustomerEvent).filter(
    CustomerEvent.event_type == "BIRTHDAY",
    CustomerEvent.is_active == True,
    func.extract('month', CustomerEvent.event_date) == today.month,
    func.extract('day', CustomerEvent.event_date) >= today.day
).all()
```

### Get pending emails
```python
from app.models import EmailQueue

pending = db.query(EmailQueue).filter(
    EmailQueue.status.in_(['Queued', 'Failed']),
    EmailQueue.retry_count < 3
).order_by(EmailQueue.priority.desc(), EmailQueue.created_at).all()
```

### Get active subscriptions
```python
from app.models import ClientSubscription
from datetime import date

active_subs = db.query(ClientSubscription).filter(
    ClientSubscription.tenant_id == tenant_id,
    ClientSubscription.status == 'Active',
    ClientSubscription.end_date >= date.today()
).all()
```

### Get account balance
```python
from app.models import AccountLedger

ledger = db.query(AccountLedger).filter(
    AccountLedger.tenant_id == tenant_id,
    AccountLedger.account_head_id == account_head_id,
    AccountLedger.financial_year == "2024-25"
).first()

balance = ledger.closing_balance if ledger else 0
```

## Field Types Reference

### Common Field Types
- `UUID` - Universally unique identifier (for new tables)
- `Integer` - Whole numbers (for existing core tables)
- `String(n)` - Variable length text (max n characters)
- `Text` - Unlimited length text
- `Numeric(p, s)` - Decimal numbers (p=precision, s=scale)
- `Boolean` - True/False
- `Date` - Date only (YYYY-MM-DD)
- `DateTime(timezone=True)` - Date and time with timezone
- `JSONB` - JSON data (indexed, queryable)

### Status Values

#### General Status
- `'Y'` / `'N'` - Active/Inactive (single char)
- `'Active'` / `'Inactive'` - Active/Inactive (descriptive)

#### Payment Status
- `'Pending'`, `'Paid'`, `'Failed'`, `'Partial'`, `'Refunded'`

#### Task/Queue Status
- `'Pending'`, `'In Progress'`, `'Completed'`, `'Failed'`, `'Cancelled'`

#### Email/WhatsApp Status
- `'Queued'`, `'Sending'`, `'Sent'`, `'Delivered'`, `'Read'`, `'Failed'`

#### Document Status
- `'Active'`, `'Expired'`, `'Rejected'`

## Relationships

### One-to-Many
```python
# Customer has many companies
customer.companies  # Access via relationship

# Company has many documents
company.documents
```

### Many-to-One
```python
# Company belongs to customer
company.customer

# Document belongs to company
document.company
```

### Through Foreign Keys
```python
# Task linked to customer company
task.company_id  # UUID foreign key
task.company     # Relationship access
```

## Best Practices

1. **Always set tenant_id** for multi-tenancy
2. **Use transactions** for related operations
3. **Validate UUIDs** before querying
4. **Index foreign keys** (already done in migration)
5. **Use JSONB** for flexible data, not core fields
6. **Set proper status** values
7. **Handle NULL** values appropriately
8. **Use timezone-aware** datetimes

## Migration Commands

```bash
# Check current version
alembic current

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Show history
alembic history

# Verify schema
python verify_schema.py
```
