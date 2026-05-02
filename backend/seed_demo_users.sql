-- Seed demo users directly into the database
-- Run this with: psql -U username -d ca_assists -f seed_demo_users.sql

-- Insert demo users
INSERT INTO "user" (
    email, first_name, last_name, password_hash, phone, 
    is_owner, status, is_email_verified, failed_login_attempts, created_at, updated_at
) VALUES
(
    'owner@company.com',
    'Owner',
    'User',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq',  -- Owner@123456
    '9876543210',
    true,
    'ACTIVE',
    true,
    0,
    NOW(),
    NOW()
),
(
    'manager@company.com',
    'Manager',
    'User',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq',  -- Manager@123456
    '9876543211',
    false,
    'ACTIVE',
    true,
    0,
    NOW(),
    NOW()
),
(
    'employee@company.com',
    'Employee',
    'User',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq',  -- Employee@123456
    '9876543212',
    false,
    'ACTIVE',
    true,
    0,
    NOW(),
    NOW()
),
(
    'client@company.com',
    'Client',
    'User',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq',  -- Client@123456
    '9876543213',
    false,
    'ACTIVE',
    true,
    0,
    NOW(),
    NOW()
);

-- Verify insertion
SELECT email, first_name, is_owner FROM "user" WHERE email LIKE '%@company.com' ORDER BY email;
