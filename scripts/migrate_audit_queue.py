#!/usr/bin/env python3
"""
Migration script to migrate audit queue data from SQLite to Redis.

This script should be run once during deployment to migrate existing audit data.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from resync.core.audit_queue import migrate_from_sqlite

async def main():
    """Run the migration from SQLite to Redis."""
    print("Starting audit queue migration from SQLite to Redis...")

    try:
        await migrate_from_sqlite()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())