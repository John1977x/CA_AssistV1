# API Endpoints Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints (except auth endpoints) require Bearer token authentication:
```
Authorization: Bearer <access_token>
```

---

## Companies Module

### Tenant Companies
Manage companies owned by the CA firm.

#### List Tenant Companies
```http
GET /companies/tenant-companies?skip=0&limit=100
```

#### Create Tenant Company
```http
POST /companies/tenant-companies
Content-Type: application/json

{
  "company_code": "TC001",
  "tenant_id": 1,
  "company_name": "ABC Chartered Accountants LLP",
  "phone": "9876543210",
  "city": "Mumbai",
  "state": "Maharashtra",
  "status": "Y"
}
```

#### Get Tenant Company
```http
GET /companies/tenant-companies/{company_id}
```

#### Update Tenant Company
```http
PUT /companies/tenant-companies/{company_id}
Content-Type: application/json

{
  "company_name": "Updated Company Name",
  "phone": "9876543211"
}
```

#### Delete Tenant Company
```http
DELETE /companies/tenant-companies/{company_id}
```

### Customer Companies
Manage companies owned by customers (clients).

#### List Customer Companies
```http
GET /companies/customer-companies?customer_id=1&skip=0&limit=100
```

#### Create Customer Company
```http
POST /companies/customer-companies
Content-Type: application/json

{
  "company_code": "CC001",
  "customer_id": 1,
  "tenant_id": 1,
  "company_name": "XYZ Industries Pvt Ltd",
  "company_type": "PRIVATE_LIMITED",
  "cin": "U12345MH2020PTC123456",
  "pan": "ABCDE1234F",
  "gstin": "27ABCDE1234F1Z5",
  "is_primary": true,
  "status": "Y"
}
```

#### Get Customer Company
```http
GET /companies/customer-companies/{company_id}
```

#### Update Customer Company
```http
PUT /companies/customer-companies/{company_id}
Content-Type: application/json

{
  "company_name": "Updated Company Name",
  "gstin": "27ABCDE1234F1Z6"
}
```

#### Delete Customer Company
```http
DELETE /companies/customer-companies/{company_id}
```

### Client Documents
Manage documents for customers and their companies.

#### List Documents
```http
GET /companies/documents?customer_id=1&company_id={uuid}&document_type=PAN&skip=0&limit=100
```

#### Create Document
```http
POST /companies/documents
Content-Type: application/json

{
  "customer_id": 1,
  "company_id": "uuid-here",
  "tenant_id": 1,
  "document_type": "PAN",
  "document_number": "ABCDE1234F",
  "document_name": "PAN Card.pdf",
  "url": "s3://bucket/docs/pan_123.pdf",
  "size_kb": 250,
  "issue_date": "2020-01-15",
  "status": "Active"
}
```

#### Get Document
```http
GET /companies/documents/{document_id}
```

#### Update Document
```http
PUT /companies/documents/{document_id}
Content-Type: application/json

{
  "status": "Verified",
  "verified_by": 1,
  "remarks": "Document verified successfully"
}
```

#### Delete Document
```http
DELETE /companies/documents/{document_id}
```

---

## Communications Module

### Email Templates

#### List Email Templates
```http
GET /communications/email-templates?category=Onboarding&is_active=true&skip=0&limit=100
```

#### Create Email Template
```http
POST /communications/email-templates
Content-Type: application/json

{
  "tenant_id": 1,
  "template_name": "Welcome Email",
  "template_code": "WELCOME_EMAIL",
  "subject": "Welcome to {{company_name}}!",
  "body_html": "<p>Dear {{customer_name}},</p><p>Welcome!</p>",
  "variables_json": {
    "customer_name": "string",
    "company_name": "string"
  },
  "category": "Onboarding",
  "is_active": true
}
```

#### Get Email Template
```http
GET /communications/email-templates/{template_id}
```

#### Update Email Template
```http
PUT /communications/email-templates/{template_id}
Content-Type: application/json

{
  "subject": "Updated Subject",
  "is_active": false
}
```

#### Delete Email Template
```http
DELETE /communications/email-templates/{template_id}
```

### Email Queue

#### List Email Queue
```http
GET /communications/email-queue?status=Queued&skip=0&limit=100
```

#### Create Email Queue Entry
```http
POST /communications/email-queue
Content-Type: application/json

{
  "tenant_id": 1,
  "template_id": "uuid-here",
  "from_email": "noreply@cafirm.com",
  "to_email": "customer@example.com",
  "subject": "Welcome!",
  "body_html": "<p>Rendered HTML</p>",
  "priority": "NORMAL",
  "status": "Queued"
}
```

#### Get Email Queue Entry
```http
GET /communications/email-queue/{queue_id}
```

#### Update Email Queue Entry
```http
PUT /communications/email-queue/{queue_id}
Content-Type: application/json

{
  "status": "Sent",
  "sent_at": "2024-04-28T10:30:00Z"
}
```

### WhatsApp Templates

#### List WhatsApp Templates
```http
GET /communications/whatsapp-templates?category=UTILITY&status=APPROVED&skip=0&limit=100
```

#### Create WhatsApp Template
```http
POST /communications/whatsapp-templates
Content-Type: application/json

{
  "tenant_id": 1,
  "template_name": "Task Reminder",
  "template_code": "TASK_REMINDER",
  "language": "en",
  "category": "UTILITY",
  "body_text": "Hi {{1}}, your task {{2}} is due on {{3}}.",
  "status": "PENDING"
}
```

#### Get WhatsApp Template
```http
GET /communications/whatsapp-templates/{template_id}
```

#### Update WhatsApp Template
```http
PUT /communications/whatsapp-templates/{template_id}
Content-Type: application/json

{
  "status": "APPROVED",
  "provider_template_id": "meta_template_123"
}
```

### WhatsApp Queue

#### List WhatsApp Queue
```http
GET /communications/whatsapp-queue?status=Queued&skip=0&limit=100
```

#### Create WhatsApp Queue Entry
```http
POST /communications/whatsapp-queue
Content-Type: application/json

{
  "tenant_id": 1,
  "wa_template_id": "uuid-here",
  "to_phone": "919876543210",
  "variables_json": {
    "1": "John",
    "2": "GST Filing",
    "3": "2024-05-31"
  },
  "priority": "NORMAL",
  "status": "Queued"
}
```

#### Get WhatsApp Queue Entry
```http
GET /communications/whatsapp-queue/{queue_id}
```

#### Update WhatsApp Queue Entry
```http
PUT /communications/whatsapp-queue/{queue_id}
Content-Type: application/json

{
  "status": "Sent",
  "wa_message_id": "wamid.123456",
  "sent_at": "2024-04-28T10:30:00Z"
}
```

### Email Schedulers

#### List Email Schedulers
```http
GET /communications/email-schedulers?is_active=true
```

#### Create Email Scheduler
```http
POST /communications/email-schedulers
Content-Type: application/json

{
  "tenant_id": 1,
  "template_id": "uuid-here",
  "trigger_type": "CRON",
  "cron_expression": "0 9 * * MON",
  "recipient_type": "All",
  "is_active": true
}
```

#### Update Email Scheduler
```http
PUT /communications/email-schedulers/{scheduler_id}
Content-Type: application/json

{
  "is_active": false,
  "cron_expression": "0 10 * * MON"
}
```

### WhatsApp Schedulers

#### List WhatsApp Schedulers
```http
GET /communications/whatsapp-schedulers?is_active=true
```

#### Create WhatsApp Scheduler
```http
POST /communications/whatsapp-schedulers
Content-Type: application/json

{
  "tenant_id": 1,
  "wa_template_id": "uuid-here",
  "trigger_type": "EVENT",
  "trigger_event": "BIRTHDAY",
  "recipient_type": "Customer",
  "is_active": true
}
```

#### Update WhatsApp Scheduler
```http
PUT /communications/whatsapp-schedulers/{scheduler_id}
Content-Type: application/json

{
  "is_active": false
}
```

---

## Response Formats

### Success Response
```json
{
  "field1": "value1",
  "field2": "value2",
  "created_at": "2024-04-28T10:30:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

### Validation Error Response
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Status Codes

- `200 OK` - Successful GET/PUT request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Validation error or business logic error
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## Common Query Parameters

- `skip` - Number of records to skip (pagination)
- `limit` - Maximum number of records to return (max: 1000)
- `status` - Filter by status
- `is_active` - Filter by active status (boolean)
- `customer_id` - Filter by customer ID
- `company_id` - Filter by company ID

---

## Data Types

### UUID
All new tables use UUID (v4) for primary keys:
```
"company_id": "550e8400-e29b-41d4-a716-446655440000"
```

### Dates
ISO 8601 format:
```
"created_at": "2024-04-28T10:30:00Z"
"event_date": "2024-05-15"
```

### Status Values

#### General Status
- `Y` / `N` - Active/Inactive (single char)
- `Active` / `Inactive` - Active/Inactive (descriptive)

#### Payment Status
- `Pending`, `Paid`, `Failed`, `Partial`, `Refunded`

#### Queue Status
- `Queued`, `Sending`, `Sent`, `Delivered`, `Read`, `Failed`

#### Document Status
- `Active`, `Expired`, `Rejected`

#### WhatsApp Template Status
- `PENDING`, `APPROVED`, `REJECTED`

---

## Testing with cURL

### Example: Create Customer Company
```bash
curl -X POST http://localhost:8000/api/v1/companies/customer-companies \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_code": "CC001",
    "customer_id": 1,
    "tenant_id": 1,
    "company_name": "Test Company Pvt Ltd",
    "company_type": "PRIVATE_LIMITED",
    "is_primary": true,
    "status": "Y"
  }'
```

### Example: List Email Templates
```bash
curl -X GET "http://localhost:8000/api/v1/communications/email-templates?is_active=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Notes

1. All endpoints require authentication except `/auth/login` and `/auth/register`
2. Tenant isolation is enforced - users can only access data for their tenant
3. UUIDs are used for new tables to support distributed systems
4. All timestamps are in UTC
5. Pagination is recommended for list endpoints
6. Soft deletes are used where applicable (check `is_deleted` field)
