"""
Seed script to create demo users for testing
Run this after migrations: python seed_demo_users.py
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.db.session import Base
from app.models.auth import User, Tenant
from app.models.company_v2 import Company, CompanyBranch, CompanyRole, CompanyUser, CompanyRoleEnum
from app.models.subscription import CAPlan, CASubscription
from app.core.security import hash_password
from app.core.config import settings
from datetime import datetime, timezone, date
import uuid

# Demo users data
DEMO_USERS = [
    {
        "email": "owner@company.com",
        "first_name": "Owner",
        "last_name": "User",
        "password": "Owner@123456",
        "phone": "9876543210",
        "is_owner": True,
        "role": "OWNER",
    },
    {
        "email": "manager@company.com",
        "first_name": "Manager",
        "last_name": "User",
        "password": "Manager@123456",
        "phone": "9876543211",
        "is_owner": False,
        "role": "MANAGER",
    },
    {
        "email": "employee@company.com",
        "first_name": "Employee",
        "last_name": "User",
        "password": "Employee@123456",
        "phone": "9876543212",
        "is_owner": False,
        "role": "EMPLOYEE",
    },
    {
        "email": "client@company.com",
        "first_name": "Client",
        "last_name": "User",
        "password": "Client@123456",
        "phone": "9876543213",
        "is_owner": False,
        "role": "CLIENT",
    },
]


async def seed_demo_users():
    """Create demo users and their company associations"""
    
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
            
            # Create or get CA plan
            plan_result = await session.execute(
                select(CAPlan).where(CAPlan.plan_code == "CA_STARTER")
            )
            plan = plan_result.scalar_one_or_none()
            
            if not plan:
                plan = CAPlan(
                    ca_plan_id=uuid.uuid4(),
                    plan_name="Starter Plan",
                    plan_code="CA_STARTER",
                    description="Starter plan for CA firms",
                    price_monthly=999.00,
                    price_yearly=9999.00,
                    max_clients=10,
                    max_users=5,
                    max_storage_gb=10,
                    is_active=True,
                )
                session.add(plan)
                await session.flush()
                print(f"✅ Created CA plan: {plan.plan_name}")
            
            # Create subscription
            subscription = CASubscription(
                ca_sub_id=uuid.uuid4(),
                ca_plan_id=plan.ca_plan_id,
                start_date=date.today(),
                end_date=date(2025, 12, 31),
                billing_cycle="YEARLY",
                amount=9999.00,
                gst_amount=1799.82,
                total_amount=11798.82,
                payment_status="Paid",
                status="Active",
                auto_renew=True,
            )
            session.add(subscription)
            await session.flush()
            print(f"✅ Created subscription")
            
            # Create tenant
            tenant = Tenant(
                subscription_id=subscription.ca_sub_id,
                tenant_code="DEMO001",
                firm_name="Demo Firm",
                owner_name="Demo Owner",
                email="demo@company.com",
                phone="9876543200",
                country="India",
                status="ACTIVE",
            )
            session.add(tenant)
            await session.flush()
            print(f"✅ Created tenant: {tenant.firm_name}")
            
            # Create company
            company = Company(
                company_id=uuid.uuid4(),
                owner_id=None,  # Will be set after owner is created
                company_name="ABC Chartered Accountants",
                company_code="ABC001",
                email="abc@company.com",
                phone="9876543200",
                country="India",
                status="ACTIVE",
            )
            session.add(company)
            await session.flush()
            print(f"✅ Created company: {company.company_name}")
            roles_data = [
                ("OWNER", "Owner role"),
                ("MANAGER", "Manager role"),
                ("EMPLOYEE", "Employee role"),
                ("CLIENT", "Client role"),
            ]
            
            roles = {}
            for role_name, description in roles_data:
                role = CompanyRole(
                    role_id=uuid.uuid4(),
                    company_id=company.company_id,
                    role_name=CompanyRoleEnum[role_name],
                    description=description,
                    permissions={},
                )
                session.add(role)
                roles[role_name] = role
            
            await session.flush()
            print(f"✅ Created {len(roles)} company roles")
            
            # Create head office branch
            head_office = CompanyBranch(
                branch_id=uuid.uuid4(),
                company_id=company.company_id,
                branch_name="Head Office",
                branch_code="HO001",
                email="headoffice@company.com",
                phone="9876543200",
                is_head_office=True,
                status="ACTIVE",
            )
            session.add(head_office)
            await session.flush()
            print(f"✅ Created head office branch")
            
            # Create demo users
            owner_user = None
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
                
                # If owner, set as company owner and create owned_companies relationship
                if user_data["is_owner"]:
                    owner_user = user
                    company.owner_id = user.user_id
                    await session.flush()
                
                # Create company user association
                company_user = CompanyUser(
                    company_user_id=uuid.uuid4(),
                    company_id=company.company_id,
                    user_id=user.user_id,
                    role_id=roles[user_data["role"]].role_id,
                    branch_id=head_office.branch_id,
                    status="ACTIVE",
                    joined_at=datetime.now(timezone.utc),
                )
                session.add(company_user)
                
                print(f"✅ Created user: {user.email} ({user_data['role']})")
            
            await session.flush()
            
            # Commit all changes
            await session.commit()
            print("\n✅ Demo users seeded successfully!")
            print("\n📋 Demo Credentials:")
            print("=" * 50)
            for user_data in DEMO_USERS:
                print(f"\n{user_data['role']}:")
                print(f"  Email: {user_data['email']}")
                print(f"  Password: {user_data['password']}")
            print("\n" + "=" * 50)
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding demo users: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_demo_users())
