# Database Migration Guide

This guide walks you through updating the CA-Assists database to match the comprehensive Excel database design.

## What's New

This migration adds **25 new tables** to support:

- 📁 **Company Management**: Tenant and customer companies with document management
- 🎂 **Event Tracking**: Birthday, anniversary, and custom event notifications
- 📧 **Email System**: Templates, queues, logs, and automated scheduling
- 💬 **WhatsApp Integration**: Message templates, queues, and delivery tracking
- 💳 **Subscription Plans**: Two-tier subscription system (CA plans + Client plans)
- 💰 **Accounting Module**: Chart of accounts, transactions, and ledgers
- 📱 **Social Media**: Multi-platform post management and scheduling

## Prerequisites

1. **Backup your database** before running migrations
2. Ensure PostgreSQL is running
3. Python environment is activated
4. All dependencies are installed

```bash
# Backup database
pg_dump -U postgres ca_assists > backup_$(date +%Y%m%d).sql

# Install dependencies
pip install -r requirements.txt
```

## Migration Steps

### Step 1: Review the Changes

```bash
cd ca-assists/backend

# Check current migration status
alembic current

# View migration history
alembic history

# Review the new migration file
cat alembic/versions/005_comprehensive_schema_update.py
```

### Step 2: Run the Migration

```bash
# Upgrade to the latest version
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade 004_billing -> 005_comprehensive
# INFO  [alembic.runtime.migration] Creating table tenant_companies
# INFO  [alembic.runtime.migration] Creating table customer_companies
# ... (more tables)
```

### Step 3: Verify the Migration

```bash
# Run verification script
python verify_schema.py

# Expected output:
# ✓ Found 39 expected tables
# ✓ Schema verification successful!

# Check specific table details
python verify_schema.py customer_companies
```

### Step 4: Test the New Models

```python
# Test in Python shell
python

from app.db.session import SessionLocal
from app.models import CustomerCompany, EmailTemplate, CAPlan

db = SessionLocal()

# Test creating a customer company
company = CustomerCompany(
    company_code="COMP001",
    customer_id=1,
    tenant_id=1,
    company_name="Test Company Pvt Ltd",
    company_type="PRIVATE_LIMITED"
)
db.add(company)
db.commit()

print(f"Created company: {company.company_id}")
```

## Rollback (If Needed)

If you encounter issues, you can rollback:

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade 004_billing

# Restore from backup
psql -U postgres ca_assists < backup_YYYYMMDD.sql
```

## New Model Files

The following model files have been added:

1. **`app/models/company.py`**
   - `TenantCompany` - Companies owned by CA firms
   - `CustomerCompany` - Companies owned by customers
   - `ClientDocument` - Document management

2. **`app/models/events.py`**
   - `CustomerEvent` - Birthday/anniversary events
   - `CustomerEventNotification` - Event notifications

3. **`app/models/communication.py`**
   - `EmailTemplate`, `EmailQueue`, `EmailLog`, `EmailScheduler`
   - `WATemplate`, `WAQueue`, `WALog`, `WAScheduler`

4. **`app/models/subscription.py`**
   - `CAPlan`, `CASubscription` - CA firm subscriptions
   - `ClientPlan`, `ClientSubscription`, `ClientInvoice` - Client subscriptions

5. **`app/models/accounts.py`**
   - `AccountHead` - Chart of accounts
   - `AccountTransaction` - Financial transactions
   - `AccountLedger` - Account balances

6. **`app/models/social.py`**
   - `SocialAccount`, `SocialPostTemplate`, `SocialPost`, `SocialScheduler`

## Updated Files

- **`app/models/task.py`**: Added `company_id` foreign key to link tasks to customer companies
- **`app/models/__init__.py`**: Updated to import all new models

## Database Schema Changes

### New Tables (25)

| Module | Tables |
|--------|--------|
| Company | `tenant_companies`, `customer_companies`, `client_documents` |
| Events | `customer_events`, `customer_event_notifications` |
| Email | `email_templates`, `email_queue`, `email_logs`, `email_schedulers` |
| WhatsApp | `wa_templates`, `wa_queue`, `wa_logs`, `wa_schedulers` |
| Subscriptions | `ca_plans`, `ca_subscriptions`, `client_plans`, `client_subscriptions`, `client_invoices` |
| Accounting | `account_heads`, `account_transactions`, `account_ledgers` |
| Social | `social_accounts`, `social_post_templates`, `social_posts`, `social_schedulers` |

### Modified Tables (1)

- **`task`**: Added `company_id` column (UUID, nullable, FK to `customer_companies`)

## Common Issues & Solutions

### Issue 1: Alembic can't find migrations

```bash
# Solution: Ensure you're in the backend directory
cd ca-assists/backend
alembic upgrade head
```

### Issue 2: Foreign key constraint errors

```bash
# Solution: Ensure existing data is consistent
# Check for orphaned records before migration
```

### Issue 3: UUID extension not available

```sql
-- Solution: Enable UUID extension in PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Issue 4: Migration fails midway

```bash
# Solution: Check the error, fix it, then retry
alembic upgrade head

# If needed, mark migration as complete manually
alembic stamp head
```

## Post-Migration Tasks

### 1. Update API Endpoints

Create new API endpoints for the new tables:

```bash
# Create endpoint files
touch app/api/v1/endpoints/companies.py
touch app/api/v1/endpoints/events.py
touch app/api/v1/endpoints/communications.py
# ... etc
```

### 2. Create Pydantic Schemas

Add validation schemas for new models:

```bash
# Create schema files
touch app/schemas/company.py
touch app/schemas/events.py
touch app/schemas/communication.py
# ... etc
```

### 3. Implement Services

Add business logic services:

```bash
# Create service files
touch app/services/company.py
touch app/services/events.py
touch app/services/communication.py
# ... etc
```

### 4. Seed Initial Data

Create seed data for system tables:

```python
# Example: Seed CA plans
from app.models import CAPlan
from app.db.session import SessionLocal

db = SessionLocal()

plans = [
    CAPlan(
        plan_name="Starter",
        plan_code="CA_STARTER",
        price_monthly=999.00,
        price_yearly=9999.00,
        max_clients=50,
        max_users=3,
        max_storage_gb=10
    ),
    CAPlan(
        plan_name="Professional",
        plan_code="CA_PRO",
        price_monthly=2999.00,
        price_yearly=29999.00,
        max_clients=200,
        max_users=10,
        max_storage_gb=50
    ),
    # ... more plans
]

db.add_all(plans)
db.commit()
```

## Testing Checklist

- [ ] All migrations run successfully
- [ ] Schema verification passes
- [ ] Can create records in new tables
- [ ] Foreign key relationships work correctly
- [ ] Existing functionality still works
- [ ] API endpoints return correct data
- [ ] No orphaned records or data inconsistencies

## Performance Considerations

1. **Indexes**: All foreign keys and frequently queried fields have indexes
2. **UUID vs Integer**: Core tables use integers for performance; new tables use UUIDs for flexibility
3. **JSONB Fields**: Used for flexible schema-less data (features, variables, etc.)
4. **Partitioning**: Consider partitioning large tables (logs, transactions) by date

## Next Steps

1. ✅ Run migration
2. ✅ Verify schema
3. ⏳ Create API endpoints
4. ⏳ Add Pydantic schemas
5. ⏳ Implement services
6. ⏳ Write tests
7. ⏳ Update documentation
8. ⏳ Deploy to staging

## Support

If you encounter issues:

1. Check the error message carefully
2. Review the migration file
3. Check database logs: `tail -f /var/log/postgresql/postgresql-*.log`
4. Consult the DATABASE_SCHEMA_UPDATE.md for detailed schema information

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL UUID Documentation](https://www.postgresql.org/docs/current/datatype-uuid.html)
