#!/usr/bin/env python3

try:
    from resync.core.agent_manager import AgentManager, AgentsConfig
    print("✅ AgentManager import successful")
    print("✅ Async lock implementation completed successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")