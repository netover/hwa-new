#!/usr/bin/env python3
"""
Test script for Redis-based audit queue functionality.
This script tests the core functionality of the Redis audit queue implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from resync.core.audit_queue import audit_queue


async def test_redis_audit_queue():
    """Test the Redis audit queue functionality."""
    print("🧪 Testing Redis Audit Queue...")

    # Test 1: Health Check
    print("\n1. Testing Redis connection health...")
    is_healthy = await audit_queue.health_check()
    if is_healthy:
        print("✅ Redis connection is healthy")
    else:
        print("❌ Redis connection failed")
        return False

    # Test 2: Connection Info
    print("\n2. Getting Redis connection information...")
    conn_info = await audit_queue.get_connection_info()
    print(f"📊 Redis Info: {conn_info}")

    # Test 3: Add audit record
    print("\n3. Testing audit record addition...")
    test_memory = {
        "id": "test_memory_123",
        "user_query": "How do I restart a job in TWS?",
        "agent_response": "You can restart a job using the 'rerun' command.",
        "ia_audit_reason": "Incorrect command suggestion",
        "ia_audit_confidence": 0.85,
    }

    success = await audit_queue.add_audit_record(test_memory)
    if success:
        print("✅ Successfully added audit record")
    else:
        print("❌ Failed to add audit record")
        return False

    # Test 4: Get pending audits
    print("\n4. Testing retrieval of pending audits...")
    pending = await audit_queue.get_pending_audits(limit=10)
    print(f"📋 Found {len(pending)} pending audit(s)")

    if pending:
        print(f"   - Memory ID: {pending[0]['memory_id']}")
        print(f"   - Status: {pending[0]['status']}")
        print(f"   - Created: {pending[0]['created_at']}")

    # Test 5: Get all audits
    print("\n5. Testing retrieval of all audits...")
    all_audits = await audit_queue.get_all_audits()
    print(f"📋 Found {len(all_audits)} total audit(s)")

    # Test 6: Get audits by status
    print("\n6. Testing retrieval of approved audits...")
    approved = await audit_queue.get_audits_by_status("approved")
    print(f"📋 Found {len(approved)} approved audit(s)")

    # Test 7: Update audit status
    print("\n7. Testing audit status update...")
    success = await audit_queue.update_audit_status("test_memory_123", "approved")
    if success:
        print("✅ Successfully updated audit status to 'approved'")
    else:
        print("❌ Failed to update audit status")
        return False

    # Test 8: Get audit metrics
    print("\n8. Testing audit metrics retrieval...")
    metrics = await audit_queue.get_audit_metrics()
    print(f"📊 Audit Metrics: {metrics}")

    # Test 9: Queue length
    print("\n9. Testing queue length...")
    queue_length = await audit_queue.get_queue_length()
    print(f"📏 Current queue length: {queue_length}")

    # Test 10: Clean up
    print("\n10. Testing audit record deletion...")
    success = await audit_queue.delete_audit_record("test_memory_123")
    if success:
        print("✅ Successfully deleted test audit record")
    else:
        print("❌ Failed to delete test audit record")

    print("\n🎉 All Redis audit queue tests completed successfully!")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_redis_audit_queue())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
