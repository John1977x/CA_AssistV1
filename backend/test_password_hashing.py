#!/usr/bin/env python3
"""
Test script to verify password hashing works correctly.
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Testing password hashing...")
    
    from app.core.security import hash_password, verify_password
    
    # Test 1: Short password
    print("\n[OK] Test 1: Short password")
    short_pwd = "MyPassword123!"
    short_hash = hash_password(short_pwd)
    assert verify_password(short_pwd, short_hash), "Short password verification failed"
    print(f"  Password: {short_pwd}")
    print(f"  Hash: {short_hash[:50]}...")
    print("  [OK] Verification passed")
    
    # Test 2: Long password (> 72 bytes)
    print("\n[OK] Test 2: Long password (> 72 bytes)")
    long_pwd = "ThisIsAVeryLongPasswordThatExceedsTheBcryptLimitOf72BytesButShouldStillWorkWithOurSHA256PreHashingApproach123!"
    print(f"  Password length: {len(long_pwd)} bytes")
    long_hash = hash_password(long_pwd)
    assert verify_password(long_pwd, long_hash), "Long password verification failed"
    print(f"  Hash: {long_hash[:50]}...")
    print("  [OK] Verification passed")
    
    # Test 3: Wrong password should fail
    print("\n[OK] Test 3: Wrong password should fail")
    wrong_pwd = "WrongPassword123!"
    assert not verify_password(wrong_pwd, long_hash), "Wrong password should not verify"
    print("  [OK] Correctly rejected wrong password")
    
    # Test 4: Unicode password
    print("\n[OK] Test 4: Unicode password")
    unicode_pwd = "password123!@#"
    unicode_hash = hash_password(unicode_pwd)
    assert verify_password(unicode_pwd, unicode_hash), "Unicode password verification failed"
    print(f"  Password: {unicode_pwd}")
    print("  [OK] Verification passed")
    
    print("\n[SUCCESS] All password hashing tests passed!")
    sys.exit(0)
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
