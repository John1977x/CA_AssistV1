"""
Basic seed script to create demo users for testing
This creates users in the existing user table without company_v2 dependencies
Run this after migrations: python seed_demo_users_basic.py
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.db.session import Base
from app.models.auth import User
from app.core.security import hash_password
from app.core.config import settings
from datetime import datetime, timezone

# Demo users data
DEMO_USERS = [
    {
        "email": "owner@company.com",
        "first_name": "Owner",
        "last_name": "User",
        "password": "Owner@123456",
        "phone": "9876543210",
        "is_owner": True,
    },
    {
        "email": "manager@company.com",
        "first_name": "Manager",
        "last_name": "User",
        "password": "Manager@123456",
        "phone": "9876543211",
        "is_owner": False,
    },
    {
        "email": "employee@company.com",
        "first_name": "Employee",
        "last_name": "User",
        "password": "Employee@123456",
        "phone": "9876543212",
        "is_owner": False,
    },
    {
        "email": "client@company.com",
        "first_name": "Client",
        "last_name": "User",
        "password": "Client@123456",
        "phone": "9876543213",
        "is_owner": False,
    },
]


async def seed_demo_users():
    """Create demo users in the user table"""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    # Create session factory
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            print("🌱 Starting demo user seeding...")
            
            # Check if demo users already exist
            result = await session.execute(
                select(User).where(User.email == "owner@company.com")
            )
            if result.scalar_one_or_none():
                print("⚠️  Demo users already exist. Skipping seeding.")
                return
            
            # Create demo users
            for user_data in DEMO_USERS:
                user = User(
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    password_hash=hash_password(user_data["password"]),
                    phone=user_data["phone"],
                    is_owner=user_data["is_owner"],
                    status="ACTIVE",
                    is_email_verified=True,
                    failed_login_attempts=0,
                )
                session.add(user)
                await session.flush()
                
                print(f"✅ Created user: {user.email}")
            
            await session.flush()
            
            # Commit all changes
            await session.commit()
            print("\n✅ Demo users seeded successfully!")
            print("\n📋 Demo Credentials:")
            print("=" * 50)
            for user_data in DEMO_USERS:
                print(f"\nEmail: {user_data['email']}")
                print(f"Password: {user_data['password']}")
            print("\n" + "=" * 50)
            print("\n🌐 Access the system:")
            print("  Frontend: http://localhost:5173")
            print("  Login: http://localhost:5173/login")
            print("  API Docs: http://localhost:8000/docs")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding demo users: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_demo_users())
