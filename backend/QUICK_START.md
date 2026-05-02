# Quick Start - CA Assists Backend (Fixed)

## Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Virtual environment activated

## Setup Steps

### 1. Install Dependencies
```bash
cd ca-assists/backend
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Run Tests (Optional but Recommended)
```bash
# Test models load correctly
python test_models.py

# Test password hashing
python test_password_hashing.py
```

Expected output:
```
✅ All tests passed!
```

### 4. Start Backend Server
```bash
uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 5. Verify Server is Running
```bash
curl http://localhost:8000/docs
```

You should see the Swagger UI documentation.

---

## Testing the API

### Register a New Tenant
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "firm_name": "My CA Firm",
    "owner_name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "password": "SecurePassword123!"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123!"
  }'
```

### Create a Customer Company
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

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'app'"
**Solution:** Make sure you're in the `ca-assists/backend` directory

### Issue: "password cannot be longer than 72 bytes"
**Solution:** This is now fixed! The new hashing method supports passwords of any length.

### Issue: "Could not determine join condition between parent/child tables"
**Solution:** This is now fixed! The relationship ambiguity has been resolved.

### Issue: Database connection error
**Solution:** 
1. Verify PostgreSQL is running
2. Check `.env` file has correct database credentials
3. Ensure database exists: `createdb ca_assists`

### Issue: Port 8000 already in use
**Solution:** Use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

---

## Database Setup

### Create Database
```bash
createdb ca_assists
```

### Run Migrations
```bash
alembic upgrade head
```

### Verify Schema
```bash
python verify_schema.py
```

---

## Development Workflow

### 1. Make Code Changes
Edit files in `app/` directory

### 2. Server Auto-Reloads
The `--reload` flag automatically restarts the server when files change

### 3. Check Logs
Watch the terminal for any errors

### 4. Test Changes
Use curl or Postman to test API endpoints

---

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Useful Commands

### Run Specific Test
```bash
python test_models.py
python test_password_hashing.py
```

### Check Database Connection
```bash
psql -U postgres -d ca_assists -c "SELECT version();"
```

### View Server Logs
```bash
# Already visible in terminal with --reload
# Or check app logs:
tail -f logs/app.log
```

### Stop Server
```bash
# Press Ctrl+C in the terminal
```

---

## Next Steps

1. ✅ Backend is running
2. ⏳ Start frontend development server
3. ⏳ Test API endpoints
4. ⏳ Run database migrations
5. ⏳ Deploy to staging

---

## Support

For issues or questions:
1. Check `FIXES_APPLIED.md` for recent fixes
2. Review `API_ENDPOINTS.md` for endpoint documentation
3. Check `DATABASE_SCHEMA_UPDATE.md` for schema details

---

**Status:** Ready to use
**Last Updated:** 2026-04-28
