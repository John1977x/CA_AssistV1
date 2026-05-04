#!/usr/bin/env python3
"""
Setup script to create PostgreSQL enum types
Run this before starting the application
"""
import psycopg2
from psycopg2 import sql

# Database connection details
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "ca_assists"
DB_USER = "postgres"
DB_PASSWORD = "password"

def create_enums():
    """Create the required enum types in PostgreSQL"""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # SQL commands to create enum types
        commands = [
            "DROP TYPE IF EXISTS userstatusenum CASCADE;",
            "DROP TYPE IF EXISTS companyroleenum CASCADE;",
            "DROP TYPE IF EXISTS companystatusenum CASCADE;",
            "CREATE TYPE companystatusenum AS ENUM ('ACTIVE', 'INACTIVE', 'SUSPENDED');",
            "CREATE TYPE companyroleenum AS ENUM ('OWNER', 'MANAGER', 'EMPLOYEE', 'CLIENT');",
            "CREATE TYPE userstatusenum AS ENUM ('ACTIVE', 'INACTIVE', 'INVITED', 'SUSPENDED');",
        ]
        
        for command in commands:
            try:
                cursor.execute(command)
                print(f"✓ Executed: {command[:60]}...")
            except Exception as e:
                print(f"⚠ Error: {command[:60]}... - {e}")
        
        # Commit the changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ Enum types created successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False


if __name__ == "__main__":
    create_enums()
