#!/usr/bin/env python3
"""
Test script to verify all models load correctly without relationship errors.
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Loading models...")
    
    # Import all models
    from app.models.auth import Subscription, SubscriptionHistory, Tenant, UserRole, Branch, User, UserLog
    from app.models.customer import Customer, CustomerDetails, Enquiry
    from app.models.task import Task, TaskDetail, TaskReminder
    from app.models.billing import Invoice, InvoiceLineItem, TimeLog, Expense, PaymentReceived
    from app.models.company import TenantCompany, CustomerCompany, ClientDocument
    from app.models.events import CustomerEvent, CustomerEventNotification
    from app.models.communication import (
        EmailTemplate, EmailQueue, EmailLog, EmailScheduler,
        WATemplate, WAQueue, WALog, WAScheduler
    )
    from app.models.subscription import CAPlan, CASubscription, ClientPlan, ClientSubscription, ClientInvoice
    from app.models.accounts import AccountHead, AccountTransaction, AccountLedger
    from app.models.social import SocialAccount, SocialPostTemplate, SocialPost, SocialScheduler
    
    print("[OK] All models loaded successfully!")
    print("\nModel Summary:")
    print("  Auth models: 7")
    print("  Customer models: 3")
    print("  Task models: 3")
    print("  Billing models: 5")
    print("  Company models: 3")
    print("  Event models: 2")
    print("  Communication models: 8")
    print("  Subscription models: 5")
    print("  Accounting models: 3")
    print("  Social models: 4")
    print("  ─────────────────")
    print("  Total: 43 models")
    
    # Test that relationships are properly configured
    print("\n[OK] Testing relationships...")
    
    # Test Subscription.history relationship
    assert hasattr(Subscription, 'history'), "Subscription.history relationship missing"
    print("  [OK] Subscription.history relationship OK")
    
    # Test AccountHead self-referencing
    assert hasattr(AccountHead, 'parent'), "AccountHead.parent relationship missing"
    print("  [OK] AccountHead.parent relationship OK")
    
    print("\n[SUCCESS] All tests passed! Models are ready to use.")
    sys.exit(0)
    
except Exception as e:
    print(f"\n[ERROR] Error loading models: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
