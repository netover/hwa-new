"""
Configuration file for pytest fixtures.
This module provides shared fixtures for all tests in the project.
"""

from typing import Callable, List, Tuple


class BackgroundTasksFixture:
    """
    A fixture for capturing and manually executing background tasks.

    This fixture can intercept calls to asyncio.create_task() and store
    the coroutines for later manual execution in tests.
    """

    def __init__(self):
        self._captured_tasks: List[Tuple[Callable, tuple, dict]] = []
        self._original_create_task
