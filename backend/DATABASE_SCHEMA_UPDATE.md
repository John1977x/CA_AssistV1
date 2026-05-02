# Database Schema Update - Excel Design Implementation

This document describes the comprehensive database schema update to match the Excel database design specification.

## Overview

The database has been updated to include all 39 tables from the Excel design document, organized into the following modules:

### Core Modules (CORE)
- ✅ Tenant - CA firm/tenant information
- ✅ User - System users with roles
- ✅ TenantCompany - Companies owned by CA firms
- ✅ Branch - Branch offices
- ✅ Subscription - Subscription plans (existing, enhanced)
- ✅ SubscriptionHistory - Subscription change history

### Customer Relationship Management (CRM)
- ✅ Customer - Individual and business customers
- ✅ CustomerDetails - Extended customer information
- ✅ Enquiry - Lead/enquiry management

### Company Management (COMPANY)
- ✅ CustomerCompany - Companies owned by customers
- ✅ ClientDocument - Document management for customers and companies

### Task & Workflow (TASK)
- ✅ Task - Compliance and document tasks
- ✅ TaskDetail - Task steps and sub-tasks
- ✅ TaskReminder - Task reminders and notifications
- ✅ TaskDocument - Task-related documents (via ClientDocument)
- ✅ TaskFeePayment - Task fees and payments (via Invoice/PaymentReceived)

### Billing & Invoicing (BILLING)
- ✅ Invoice - Customer invoices
- ✅ InvoiceLineItem - Invoice line items
- ✅ PaymentReceived - Payment tracking
- ✅ TimeLog - Time tracking for billing
- ✅ Expense - Expense management

### Events & Notifications (BIRTHDAY)
- ✅ CustomerEvent - Birthday, anniversary, and custom events
- ✅ CustomerEventNotification - Event notification tracking

### Email Communication (EMAIL)
- ✅ EmailTemplate - Email templates with variables
- ✅ EmailQueue - Email sending queue
- ✅ EmailLog - Email delivery logs
- ✅ EmailScheduler - Automated email scheduling

### WhatsApp Communication (WHATSAPP)
- ✅ WATemplate - WhatsApp message templates
- ✅ WAQueue - WhatsApp message queue
- ✅ WALog - WhatsApp delivery logs
- ✅ WAScheduler - Automated WhatsApp scheduling

### Subscription Management (SUB_CA, SUB_CLIENT)
- ✅ CAPlan - Subscription plans for CA firms
- ✅ CASubscription - CA firm subscriptions
- ✅ ClientPlan - Service plans for clients
- ✅ ClientSubscription - Client subscriptions
- ✅ ClientInvoice - Subscription invoices

### Accounting (ACCOUNTS)
- ✅ AccountHead - Chart of accounts
- ✅ AccountTransaction - Financial transactions
- ✅ AccountLedger - Account balances and snapshots

### Social Media (SOCIAL)
- ✅ SocialAccount - Connected social media accounts
- ✅ SocialPostTemplate - Post templates
- ✅ SocialPost - Social media posts
- ✅ SocialScheduler - Automated post scheduling

### Logging (LOG)
- ✅ UserLog - User activity logs

## Key Design Decisions

### ID Strategy
- **Excel Design**: Uses UNIQUEIDENTIFIER (SQL Server GUID) for all primary keys
- **Implementation**: 
  - Core tables (Tenant, User, Customer, Task, etc.) use Integer IDs for performance
  - New tables use UUID for compatibility with distributed systems
  - Foreign keys maintain appropriate types

### Field Mapping
- Excel `CHAR(1)` status fields → PostgreSQL `String(1)` or `String(20)` for clarity
- Excel `NVARCHAR(MAX)` → PostgreSQL `Text`
- Excel `DATETIME` → PostgreSQL `DateTime(timezone=True)`
- Excel `DECIMAL` → PostgreSQL `Numeric` with appropriate precision

### Relationships
All foreign key relationships from the Excel design have been implemented with proper indexes and cascading rules.

## Migration Files

### New Model Files
1. `app/models/company.py` - Tenant and customer companies, documents
2. `app/models/events.py` - Customer events and notifications
3. `app/models/communication.py` - Email and WhatsApp templates, queues, logs
4. `app/models/subscription.py` - CA and client subscription plans
5. `app/models/accounts.py` - Accounting module
6. `app/models/social.py` - Social media management

### Alembic Migration
- `alembic/versions/005_comprehensive_schema_update.py` - Creates all new tables

## Running the Migration

```bash
# Navigate to backend directory
cd ca-assists/backend

# Review the migration
alembic history

# Run the migration
alembic upgrade head

# If needed, rollback
alembic downgrade -1
```

## Database Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CORE MODULE                          │
├─────────────────────────────────────────────────────────────┤
│ Tenant ──┬─→ User ──→ UserLog                               │
│          ├─→ Branch                                          │
│          ├─→ TenantCompany                                   │
│          └─→ Subscription ──→ SubscriptionHistory           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      CRM & COMPANY                           │
├─────────────────────────────────────────────────────────────┤
│ Customer ──┬─→ CustomerDetails                              │
│            ├─→ CustomerCompany ──→ ClientDocument           │
│            ├─→ CustomerEvent ──→ CustomerEventNotification  │
│            └─→ ClientSubscription                           │
│                                                              │
│ Enquiry ──→ Customer (conversion)                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      TASK & WORKFLOW                         │
├─────────────────────────────────────────────────────────────┤
│ Task ──┬─→ TaskDetail                                       │
│        ├─→ TaskReminder                                     │
│        ├─→ ClientDocument                                   │
│        └─→ Invoice                                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    BILLING & ACCOUNTING                      │
├─────────────────────────────────────────────────────────────┤
│ Invoice ──┬─→ InvoiceLineItem                               │
│           └─→ PaymentReceived                               │
│                                                              │
│ AccountHead ──┬─→ AccountTransaction                        │
│               └─→ AccountLedger                             │
│                                                              │
│ TimeLog, Expense                                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     COMMUNICATION                            │
├─────────────────────────────────────────────────────────────┤
│ EmailTemplate ──┬─→ EmailQueue ──→ EmailLog                │
│                 └─→ EmailScheduler                          │
│                                                              │
│ WATemplate ──┬─→ WAQueue ──→ WALog                         │
│              └─→ WAScheduler                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    SUBSCRIPTION PLANS                        │
├─────────────────────────────────────────────────────────────┤
│ CAPlan ──→ CASubscription                                   │
│                                                              │
│ ClientPlan ──┬─→ ClientSubscription                        │
│              └─→ ClientInvoice                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      SOCIAL MEDIA                            │
├─────────────────────────────────────────────────────────────┤
│ SocialAccount ──┬─→ SocialPost                             │
│                 └─→ SocialScheduler                         │
│                                                              │
│ SocialPostTemplate ──→ SocialPost                          │
└─────────────────────────────────────────────────────────────┘
```

## Features Implemented

### 1. Multi-Company Support
- Customers can have multiple companies
- Tasks can be linked to specific companies
- Documents can be personal or company-specific

### 2. Event Management
- Birthday and anniversary tracking
- Recurring yearly events
- Multi-channel notifications (Email, WhatsApp, SMS)

### 3. Communication Automation
- Template-based email and WhatsApp messaging
- Queue management with retry logic
- Delivery tracking and analytics
- Scheduled and event-triggered messaging

### 4. Subscription Management
- Two-tier subscriptions: CA plans and Client plans
- Flexible billing cycles
- Auto-renewal support
- Subscription invoicing

### 5. Accounting Integration
- Chart of accounts with hierarchy
- Double-entry transaction tracking
- Financial year-based ledgers
- Multi-currency support

### 6. Social Media Management
- Multi-platform support (Facebook, Twitter, LinkedIn, Instagram)
- Post templates and scheduling
- Engagement metrics tracking

## Next Steps

1. **Update API Endpoints**: Create REST API endpoints for new tables
2. **Update Schemas**: Add Pydantic schemas for validation
3. **Update Services**: Implement business logic services
4. **Testing**: Write unit and integration tests
5. **Documentation**: Update API documentation

## Notes

- All tables include proper indexes on foreign keys and frequently queried fields
- Timestamps use timezone-aware datetime for consistency
- Status fields use descriptive strings instead of single characters for clarity
- JSONB fields are used for flexible, schema-less data storage
- All relationships are properly defined with back_populates for bidirectional access
