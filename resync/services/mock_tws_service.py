from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from resync.models.tws import (
    CriticalJob,
    JobStatus,
    SystemStatus,
    WorkstationStatus,
)

logger = logging.getLogger(__name__)


class MockTWSClient:
    """
    A mock client for the HCL Workload Automation (TWS) API, used for
    development and testing without a live TWS connection.
    It loads static data from a JSON file.

    Args:
        *args: Additional positional arguments (unused)
        **kwargs: Additional keyword arguments (unused)

    Attributes:
        mock_data (Dict[str, Any]): The loaded mock data from the JSON file
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the MockTWSClient with default settings."""
        self.mock_data: Dict[str, Any] = {}
        self._load_mock_data()
        logger.info("MockTWSClient initialized. Using static mock data.")

    def _load_mock_data(self) -> None:
        """
        Load mock data from a JSON file.

        This method:
        1. Constructs the path to the mock data file
        2. Checks if the file exists
        3. Tries to load and parse the JSON data
        4. Handles different types of errors gracefully

        Returns:
            None
        """
        mock_data_path = Path(__file__).parent.parent.parent / "mock_tws_data.json"
        if not mock_data_path.exists():
            logger.warning(
                f"Mock data file not found at {mock_data_path}. Returning empty data."
            )
            return

        try:
            with open(mock_data_path, "r", encoding="utf-8") as f:
                self.mock_data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode mock data JSON from {mock_data_path}: {e}")
            self.mock_data = {}
        except (IOError, IsADirectoryError) as e:
            logger.error(f"Failed to access mock data file at {mock_data_path}: {e}")
            self.mock_data = {}
        except Exception as e:
            logger.error(
                f"Unexpected error loading mock data from {mock_data_path}: {e}"
            )
            self.mock_data = {}

    async def check_connection(self) -> bool:
        """
        Mocks checking the connection status.

        Returns:
            bool: The connection status from the mock data

        Note:
            Simulates an asynchronous network delay with a 0.1 second wait

        Example:
            >>> client = MockTWSClient()
            >>> status = client.check_connection()
            >>> print(status)
            True
        """
        await asyncio.sleep(0.1)  # Simulate network delay
        return self.mock_data.get("connection_status", False)

    async def get_workstations_status(self) -> List[WorkstationStatus]:
        """
        Mocks retrieving workstation status.

        Returns:
            List[WorkstationStatus]: List of workstation status objects

        Note:
            Simulates an asynchronous delay with a 0.1 second wait
        """
        await asyncio.sleep(0.1)
        return [
            WorkstationStatus(**ws)
            for ws in self.mock_data.get("workstations_status", [])
        ]

    async def get_jobs_status(self) -> List[JobStatus]:
        """
        Mocks retrieving job status.

        Returns:
            List[JobStatus]: List of job status objects

        Note:
            Simulates an asynchronous delay with a 0.1 second wait
        """
        await asyncio.sleep(0.1)
        return [JobStatus(**job) for job in self.mock_data.get("jobs_status", [])]

    async def get_critical_path_status(self) -> List[CriticalJob]:
        """
        Mocks retrieving critical path status.

        Returns:
            List[CriticalJob]: List of critical job status objects

        Note:
            Simulates an asynchronous delay with a 0.1 second wait
        """
        await asyncio.sleep(0.1)
        return [
            CriticalJob(**job) for job in self.mock_data.get("critical_path_status", [])
        ]

    async def get_system_status(self) -> SystemStatus:
        """
        Mocks retrieving comprehensive system status.

        Returns:
            SystemStatus: Object containing the overall system status

        Note:
            Aggregates status data from multiple sources with appropriate delays
        """
        workstations = await self.get_workstations_status()
        jobs = await self.get_jobs_status()
        critical_jobs = await self.get_critical_path_status()
        return SystemStatus(
            workstations=workstations, jobs=jobs, critical_jobs=critical_jobs
        )

    async def close(self) -> None:
        """
        Mocks closing the client connection.

        Note:
            Simulates proper cleanup of client resources
        """
        logger.info("MockTWSClient closed.")
