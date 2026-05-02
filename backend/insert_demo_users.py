"""
Direct SQL insert script for demo users
This bypasses ORM issues by using raw SQL
"""

import asyncio
import asyncpg
from app.core.config import settings
from app.core.security import hash_password

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


async def insert_demo_users():
    """Insert demo users using raw SQL"""
    
    # Parse database URL
    db_url = settings.DATABASE_URL
    # Convert async URL to sync URL for asyncpg
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)
        print("✅ Connected to database")
        
        # Step 1: Check if default tenant exists
        tenant_id = await conn.fetchval(
            'SELECT tenant_id FROM tenant WHERE tenant_code = $1',
            'DEFAULT'
        )
        
        if not tenant_id:
            print("📝 Creating default tenant...")
            
            # First, ensure a subscription exists
            subscription_id = await conn.fetchval(
                'SELECT subscription_id FROM subscription WHERE plan_code = $1',
                'TRIAL'
            )
            
            if not subscription_id:
                print("  Creating TRIAL subscription...")
                subscription_id = await conn.fetchval(
                    '''INSERT INTO subscription (
                        plan_name, plan_code, price_monthly, max_users, max_clients, 
                        max_branches, trial_days, features_json, is_active
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING subscription_id''',
                    'Trial', 'TRIAL', 0, 10, 50, 5, 14,
                    '{"gst": true, "itr": true, "tds": false, "audit": false}',
                    True
                )
                print(f"  ✅ Created subscription with ID: {subscription_id}")
            
            # Create default tenant
            tenant_id = await conn.fetchval(
                '''INSERT INTO tenant (
                    subscription_id, tenant_code, firm_name, owner_name, email, 
                    phone, country, status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING tenant_id''',
                subscription_id, 'DEFAULT', 'Default Tenant', 'Admin',
                'admin@default.com', '0000000000', 'India', 'ACTIVE'
            )
            print(f"✅ Created default tenant with ID: {tenant_id}")
        else:
            print(f"✅ Using existing default tenant with ID: {tenant_id}")
        
        # Step 2: Check if users already exist
        existing = await conn.fetchval(
            'SELECT COUNT(*) FROM "user" WHERE email = $1',
            "owner@company.com"
        )
        
        if existing:
            print("⚠️  Demo users already exist. Skipping insertion.")
            await conn.close()
            return
        
        # Step 3: Get or create a default role
        role_id = await conn.fetchval(
            'SELECT role_id FROM user_role WHERE tenant_id = $1 AND role_code = $2',
            tenant_id, 'USER'
        )
        
        if not role_id:
            print("📝 Creating default user role...")
            role_id = await conn.fetchval(
                '''INSERT INTO user_role (
                    tenant_id, role_name, role_code, is_system_role, is_active
                ) VALUES ($1, $2, $3, $4, $5)
                RETURNING role_id''',
                tenant_id, 'User', 'USER', False, True
            )
            print(f"✅ Created default role with ID: {role_id}")
        
        # Step 4: Insert demo users
        print("\n📝 Inserting demo users...")
        for user_data in DEMO_USERS:
            password_hash = hash_password(user_data["password"])
            
            user_id = await conn.fetchval(
                '''INSERT INTO "user" (
                    tenant_id, role_id, email, first_name, last_name, password_hash, 
                    phone, is_owner, status, failed_login_attempts, display_name
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING user_id''',
                tenant_id, role_id, user_data["email"],
                user_data["first_name"], user_data["last_name"],
                password_hash, user_data["phone"],
                user_data["is_owner"], "ACTIVE", 0,
                f"{user_data['first_name']} {user_data['last_name']}"
            )
            print(f"✅ Created user: {user_data['email']} (ID: {user_id})")
        
        # Step 5: Verify insertion
        count = await conn.fetchval(
            'SELECT COUNT(*) FROM "user" WHERE email LIKE $1',
            '%@company.com'
        )
        
        print(f"\n✅ Successfully inserted {count} demo users!")
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
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(insert_demo_users())
