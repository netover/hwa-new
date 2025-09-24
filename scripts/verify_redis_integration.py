#!/usr/bin/env python3
"""
Redis Integration Verification Script

This script verifies that the distributed locking implementation is properly
configured and can connect to Redis when available.

Usage:
    python scripts/verify_redis_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from resync.core.audit_lock import DistributedAuditLock, audit_lock
from resync.core.audit_queue import AsyncAuditQueue
from resync.settings import settings


async def test_distributed_audit_lock():
    """Test the DistributedAuditLock class."""
    print("🔍 Testing DistributedAuditLock...")

    lock = DistributedAuditLock(settings.REDIS_URL)

    try:
        # Test connection
        await lock.connect()
        print("✅ Connected to Redis successfully")

        # Test basic lock operations
        memory_id = "test_memory_123"

        # Test lock acquisition
        async with await lock.acquire(memory_id, timeout=5):
            print(f"✅ Acquired lock for memory: {memory_id}")
            assert await lock.is_locked(memory_id)

            # Test that same lock cannot be acquired again
            try:
                async with await lock.acquire(memory_id, timeout=5):
                    print("❌ ERROR: Should not be able to acquire same lock twice")
                    return False
            except Exception:
                print("✅ Correctly prevented duplicate lock acquisition")

        # Test lock release
        assert not await lock.is_locked(memory_id)
        print("✅ Lock released correctly")

        # Test force release
        async with await lock.acquire(memory_id, timeout=30):
            assert await lock.is_locked(memory_id)

        result = await lock.force_release(memory_id)
        assert result
        assert not await lock.is_locked(memory_id)
        print("✅ Force release works correctly")

        await lock.disconnect()
        print("✅ Disconnected from Redis successfully")

        return True

    except Exception as e:
        print(f"❌ DistributedAuditLock test failed: {e}")
        return False


async def test_audit_queue_integration():
    """Test that AsyncAuditQueue uses the new DistributedAuditLock."""
    print("\n🔍 Testing AsyncAuditQueue integration...")

    try:
        audit_queue = AsyncAuditQueue(settings.REDIS_URL)

        # Test that the audit queue has the distributed lock instance
        assert hasattr(audit_queue, 'distributed_lock')
        assert isinstance(audit_queue.distributed_lock, DistributedAuditLock)
        print("✅ AsyncAuditQueue properly initialized with DistributedAuditLock")

        # Test lock delegation
        memory_id = "test_audit_queue_lock"

        async with await audit_queue.with_lock(memory_id, timeout=5):
            print(f"✅ Audit queue lock acquisition works for memory: {memory_id}")
            assert await audit_queue.distributed_lock.is_locked(memory_id)

        print("✅ Audit queue lock delegation works correctly")

        return True

    except Exception as e:
        print(f"❌ AsyncAuditQueue integration test failed: {e}")
        return False


async def test_global_audit_lock():
    """Test the global audit_lock instance."""
    print("\n🔍 Testing global audit_lock instance...")

    try:
        memory_id = "test_global_lock"

        # Test global instance
        async with await audit_lock.acquire(memory_id, timeout=5):
            print(f"✅ Global audit_lock works for memory: {memory_id}")
            assert await audit_lock.is_locked(memory_id)

        assert not await audit_lock.is_locked(memory_id)
        print("✅ Global audit_lock released correctly")

        return True

    except Exception as e:
        print(f"❌ Global audit_lock test failed: {e}")
        return False


async def test_configuration():
    """Test configuration settings."""
    print("\n🔍 Testing configuration...")

    try:
        # Test that Redis URL is configured
        assert hasattr(settings, 'REDIS_URL')
        assert settings.REDIS_URL
        print(f"✅ Redis URL configured: {settings.REDIS_URL}")

        # Test that required environment variables are accessible
        assert settings.REDIS_URL.startswith(('redis://', 'rediss://'))
        print("✅ Redis URL format is valid")

        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def main():
    """Run all verification tests."""
    print("🚀 Starting Redis Integration Verification")
    print("=" * 50)

    tests = [
        test_configuration,
        test_distributed_audit_lock,
        test_audit_queue_integration,
        test_global_audit_lock,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All tests passed! Redis integration is properly configured.")
        print("\n📝 Next steps:")
        print("1. Start Redis server (if not already running)")
        print("2. Run the unit tests: pytest tests/test_audit_lock.py")
        print("3. Deploy and test in production environment")
        return True
    else:
        print("❌ Some tests failed. Please check the configuration and Redis setup.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Verification failed with error: {e}")
        sys.exit(1)