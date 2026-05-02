#!/usr/bin/env python3
"""
Verify database schema matches the Excel design specification.
This script checks that all required tables and columns exist.
"""

from sqlalchemy import inspect, create_engine
from app.core.config import settings
from app.db.session import Base
import app.models  # Import all models

# Expected tables from Excel design
EXPECTED_TABLES = {
    # Core
    'tenant', 'user', 'tenant_companies', 'branch', 'user_log', 
    'subscription', 'subscription_history', 'user_role',
    
    # CRM
    'customer', 'customer_details', 'enquiry',
    
    # Company
    'customer_companies', 'client_documents',
    
    # Events
    'customer_events', 'customer_event_notifications',
    
    # Task
    'task', 'task_detail', 'task_reminder',
    
    # Billing
    'invoice', 'invoice_line_item', 'payment_received', 'time_log', 'expense',
    
    # Email
    'email_templates', 'email_queue', 'email_logs', 'email_schedulers',
    
    # WhatsApp
    'wa_templates', 'wa_queue', 'wa_logs', 'wa_schedulers',
    
    # Subscriptions
    'ca_plans', 'ca_subscriptions', 'client_plans', 
    'client_subscriptions', 'client_invoices',
    
    # Accounting
    'account_heads', 'account_transactions', 'account_ledgers',
    
    # Social
    'social_accounts', 'social_post_templates', 'social_posts', 'social_schedulers',
}


def verify_schema():
    """Verify that all expected tables exist in the database."""
    print("=" * 80)
    print("DATABASE SCHEMA VERIFICATION")
    print("=" * 80)
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    # Get existing tables
    existing_tables = set(inspector.get_table_names())
    
    print(f"\n✓ Connected to database: {settings.DATABASE_URL.split('@')[1]}")
    print(f"✓ Found {len(existing_tables)} tables in database")
    
    # Check for expected tables
    print("\n" + "-" * 80)
    print("TABLE VERIFICATION")
    print("-" * 80)
    
    missing_tables = EXPECTED_TABLES - existing_tables
    extra_tables = existing_tables - EXPECTED_TABLES
    matching_tables = EXPECTED_TABLES & existing_tables
    
    if matching_tables:
        print(f"\n✓ Found {len(matching_tables)} expected tables:")
        for table in sorted(matching_tables):
            print(f"  ✓ {table}")
    
    if missing_tables:
        print(f"\n✗ Missing {len(missing_tables)} expected tables:")
        for table in sorted(missing_tables):
            print(f"  ✗ {table}")
    
    if extra_tables:
        print(f"\n⚠ Found {len(extra_tables)} additional tables:")
        for table in sorted(extra_tables):
            print(f"  • {table}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Expected tables: {len(EXPECTED_TABLES)}")
    print(f"Found tables: {len(matching_tables)}")
    print(f"Missing tables: {len(missing_tables)}")
    print(f"Coverage: {len(matching_tables) / len(EXPECTED_TABLES) * 100:.1f}%")
    
    if missing_tables:
        print("\n⚠ Schema is incomplete. Run: alembic upgrade head")
        return False
    else:
        print("\n✓ Schema verification successful!")
        return True


def show_table_details(table_name):
    """Show detailed information about a specific table."""
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    print(f"\n{'=' * 80}")
    print(f"TABLE: {table_name}")
    print('=' * 80)
    
    if table_name not in inspector.get_table_names():
        print(f"✗ Table '{table_name}' does not exist")
        return
    
    # Get columns
    columns = inspector.get_columns(table_name)
    print(f"\nColumns ({len(columns)}):")
    print(f"{'Name':<30} {'Type':<20} {'Nullable':<10} {'Default'}")
    print('-' * 80)
    for col in columns:
        nullable = 'YES' if col['nullable'] else 'NO'
        default = str(col['default']) if col['default'] else ''
        print(f"{col['name']:<30} {str(col['type']):<20} {nullable:<10} {default}")
    
    # Get foreign keys
    fks = inspector.get_foreign_keys(table_name)
    if fks:
        print(f"\nForeign Keys ({len(fks)}):")
        for fk in fks:
            print(f"  • {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
    
    # Get indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print(f"\nIndexes ({len(indexes)}):")
        for idx in indexes:
            unique = 'UNIQUE' if idx['unique'] else ''
            print(f"  • {idx['name']}: {idx['column_names']} {unique}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Show details for specific table
        table_name = sys.argv[1]
        show_table_details(table_name)
    else:
        # Run full verification
        success = verify_schema()
        sys.exit(0 if success else 1)
