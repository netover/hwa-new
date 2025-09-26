#!/usr/bin/env python3
"""Test script to verify async method signatures."""

import inspect

from resync.core.knowledge_graph import AsyncKnowledgeGraph

# Test that methods are async
kg = AsyncKnowledgeGraph()
async_methods = [
    "add_conversation",
    "search_similar_issues",
    "search_conversations",
    "add_solution_feedback",
    "get_all_recent_conversations",
    "get_relevant_context",
    "is_memory_flagged",
    "is_memory_approved",
    "delete_memory",
    "add_observations",
    "is_memory_already_processed",
    "atomic_check_and_flag",
    "atomic_check_and_delete",
]

print("Checking async method signatures...")
all_async = True
for method_name in async_methods:
    method = getattr(kg, method_name)
    is_async = inspect.iscoroutinefunction(method)
    status = "ASYNC" if is_async else "NOT ASYNC"
    print(f"{method_name}: {status}")
    if not is_async:
        all_async = False

print(f"\nAll methods are async: {all_async}")
