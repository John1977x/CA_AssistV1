#!/usr/bin/env python3
"""
Script to create missing PostgreSQL enum types
Run this before running migrations
"""
import asyncio
from sqlalchemy import text
from app.db.session import engine


async def create_enums():
    """Create the required enum types in PostgreSQL"""
    async with engine.begin() as conn:
        try:
            # Create enum types
            await conn.execute(text("CREATE TYPE companystatusenum AS ENUM ('ACTIVE', 'INACTIVE', 'SUSPENDED')"))
            print("✓ Created companystatusenum")
        except Exception as e:
            print(f"⚠ companystatusenum: {e}")

        try:
            await conn.execute(text("CREATE TYPE companyroleenum AS ENUM ('OWNER', 'MANAGER', 'EMPLOYEE', 'CLIENT')"))
            print("✓ Created companyroleenum")
        except Exception as e:
            print(f"⚠ companyroleenum: {e}")

        try:
            await conn.execute(text("CREATE TYPE userstatusenum AS ENUM ('ACTIVE', 'INACTIVE', 'INVITED', 'SUSPENDED')"))
            print("✓ Created userstatusenum")
        except Exception as e:
            print(f"⚠ userstatusenum: {e}")


if __name__ == "__main__":
    asyncio.run(create_enums())
    print("\nEnum types created successfully!")
