-- Create PostgreSQL enum types for company management

-- Drop existing types if they exist (for idempotency)
DROP TYPE IF EXISTS userstatusenum CASCADE;
DROP TYPE IF EXISTS companyroleenum CASCADE;
DROP TYPE IF EXISTS companystatusenum CASCADE;

-- Create enum types
CREATE TYPE companystatusenum AS ENUM ('ACTIVE', 'INACTIVE', 'SUSPENDED');
CREATE TYPE companyroleenum AS ENUM ('OWNER', 'MANAGER', 'EMPLOYEE', 'CLIENT');
CREATE TYPE userstatusenum AS ENUM ('ACTIVE', 'INACTIVE', 'INVITED', 'SUSPENDED');

-- Verify creation
SELECT typname FROM pg_type WHERE typname IN ('companystatusenum', 'companyroleenum', 'userstatusenum');
