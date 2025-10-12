from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from resync.models.tws import (CriticalJob, JobStatus, SystemStatus,
                               WorkstationStatus)

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
            logger.error(
                "Failed to decode mock data JSON from %s: %s", mock_data_path, e
            )
            self.mock_data = {}
            # Don't raise here to allow the service to continue with empty data
        except (IOError, IsADirectoryError) as e:
            logger.error("Failed to access mock data file at %s: %s", mock_data_path, e)
            self.mock_data = {}
            # Don't raise here to allow the service to continue with empty data
        except FileNotFoundError as e:
            logger.error("Mock data file not found at %s: %s", mock_data_path, e)
            self.mock_data = {}
            # Don't raise here to allow the service to continue with empty data
        except PermissionError as e:
            logger.error(
                "Permission denied accessing mock data file at %s: %s",
                mock_data_path,
                e,
            )
            self.mock_data = {}
            # Don't raise here to allow the service to continue with empty data
        except UnicodeDecodeError as e:
            logger.error(
                "Unicode decode error reading mock data file at %s: %s",
                mock_data_path,
                e,
            )
            self.mock_data = {}
            # Don't raise here to allow the service to continue with empty data
        except Exception as e:
            logger.error(
                "Unexpected error loading mock data from %s: %s", mock_data_path, e
            )
            self.mock_data = {}
            # In a production environment, consider raising a FileProcessingError here
            # but for a mock service, it's better to continue with empty data

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
        connection_status = self.mock_data.get("connection_status")
        return bool(connection_status) if connection_status is not None else False

    async def ping(self) -> None:
        """
        Performs a lightweight connectivity test for the mock TWS server.

        This method simulates a ping operation for health checks.

        Raises:
            ConnectionError: If the mock server is configured as unreachable
            TimeoutError: If the mock server is configured to timeout
        """
        await asyncio.sleep(0.05)  # Simulate quick network delay

        # Check mock configuration for ping behavior
        ping_config = self.mock_data.get("ping_config", {})

        if ping_config.get("timeout", False):
            raise TimeoutError("Mock TWS server ping timed out")

        if not ping_config.get("reachable", True):
            raise ConnectionError("Mock TWS server is unreachable")

        # Ping successful for mock
        return None

    async def get_workstations_status(self) -> List[WorkstationStatus]:
        """
        Mocks retrieving workstation status.

        Returns:
            List[WorkstationStatus]: List of workstation status objects

        Note:
            Simulates an asynchronous delay with a 0.1 second wait
        """
        await asyncio.sleep(0.1)
        workstations_data = self.mock_data.get("workstations_status", [])
        workstations = []
        for ws in workstations_data:
            if isinstance(ws, dict):
                try:
                    workstations.append(WorkstationStatus(**ws))
                except Exception as e:
                    logger.warning(f"Failed to create WorkstationStatus from data: {e}")
        return workstations

    async def get_jobs_status(self) -> List[JobStatus]:
        """
        Mocks retrieving job status.

        Returns:
            List[JobStatus]: List of job status objects

        Note:
            Simulates an asynchronous delay with a 0.1 second wait
        """
        await asyncio.sleep(0.1)
        jobs_data = self.mock_data.get("jobs_status", [])
        jobs = []
        for job in jobs_data:
            if isinstance(job, dict):
                try:
                    jobs.append(JobStatus(**job))
                except Exception as e:
                    logger.warning(f"Failed to create JobStatus from data: {e}")
        return jobs

    async def get_critical_path_status(self) -> List[CriticalJob]:
        """
        Mocks retrieving critical path status.

        Returns:
            List[CriticalJob]: List of critical job status objects

        Note:
            Simulates an asynchronous delay with a 0.1 second wait
        """
        await asyncio.sleep(0.1)
        critical_jobs = []
        for job in self.mock_data.get("critical_path_status", []):
            if isinstance(job, dict):
                try:
                    critical_jobs.append(CriticalJob(**job))
                except Exception as e:
                    logger.warning(f"Failed to create CriticalJob from data: {e}")
        return critical_jobs

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

    async def restart_job(self, job_id: str) -> Dict[str, Any]:
        """
        Mocks restarting a job.

        Args:
            job_id: The ID of the job to restart

        Returns:
            Dict containing job restart information

        Note:
            Simulates an asynchronous delay and returns mock restart data
        """
        await asyncio.sleep(0.1)  # Simulate network delay
        return {
            "job_id": job_id,
            "action": "restarted",
            "status": "PENDING",
            "timestamp": "2024-01-01T12:00:00Z",
        }

    async def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """
        Mocks canceling a job.

        Args:
            job_id: The ID of the job to cancel

        Returns:
            Dict containing job cancellation information

        Note:
            Simulates an asynchronous delay and returns mock cancellation data
        """
        await asyncio.sleep(0.1)  # Simulate network delay
        return {
            "job_id": job_id,
            "action": "canceled",
            "status": "CANCELED",
            "timestamp": "2024-01-01T12:00:00Z",
        }

    async def get_job_status(self, job_id: str) -> JobStatus:
        """
        Mocks getting the status of a specific job.

        Args:
            job_id: The ID of the job to get status for

        Returns:
            JobStatus: The status of the requested job

        Note:
            Simulates an asynchronous delay and returns mock job status
        """
        await asyncio.sleep(0.1)  # Simulate network delay
        # Find a job that matches the job_id (for simplicity, return first job)
        jobs = self.mock_data.get("jobs_status", [])
        if jobs:
            return JobStatus(**jobs[0])
        # Return a default job if none found
        return JobStatus(
            name=f"JOB_{job_id}",
            workstation="CPU_WS",
            status="SUCC",
            job_stream="STREAM_A",
        )

    async def get_job_history(self, job_id: str) -> List[Dict[str, Any]]:
        """
        Mocks getting the history of a specific job.

        Args:
            job_id: The ID of the job to get history for

        Returns:
            List of job history entries

        Note:
            Simulates an asynchronous delay and returns mock job history
        """
        await asyncio.sleep(0.1)  # Simulate network delay
        return [
            {
                "job_id": str(job_id),
                "status": "SUCC",
                "timestamp": "2024-01-01T10:00:00Z",
                "duration": "5m",
            },
            {
                "job_id": str(job_id),
                "status": "RUNNING",
                "timestamp": "2024-01-01T11:00:00Z",
                "duration": "2m",
            },
        ]

    async def list_jobs(self, status_filter: Optional[str] = None) -> List[JobStatus]:
        """
        Mocks listing all jobs, optionally filtered by status.

        Args:
            status_filter: Optional status filter (e.g., 'SUCC', 'ABEND')

        Returns:
            List[JobStatus]: List of job status objects

        Note:
            Simulates an asynchronous delay and returns filtered mock jobs
        """
        await asyncio.sleep(0.1)  # Simulate network delay
        jobs = [JobStatus(**job) for job in self.mock_data.get("jobs_status", [])]

        if status_filter:
            jobs = [job for job in jobs if job.status == status_filter]

        return jobs

    async def validate_connection(
        self, host: str = None, port: int = None, user: str = None, password: str = None
    ) -> dict[str, bool]:
        """
        Mocks validating TWS connection parameters.

        Args:
            host: TWS server hostname (optional)
            port: TWS server port (optional)
            user: TWS username (optional)
            password: TWS password (optional)

        Returns:
            Dictionary with validation result
        """
        # Simulate validation process
        await asyncio.sleep(0.05)  # Simulate short network delay for validation

        # Get validation config from mock data or default to success
        validation_config = self.mock_data.get("validation_config", {})
        validation_success = validation_config.get("connection_valid", True)

        if validation_success:
            return {
                "valid": True,
                "message": "Successfully validated connection to mock TWS server",
                "host": host or "mock-tws-server",
                "port": port or 31111,
            }
        else:
            return {
                "valid": False,
                "message": "Mock TWS connection validation failed as configured",
                "host": host or "mock-tws-server",
                "port": port or 31111,
            }

    async def close(self) -> None:
        """
        Mocks closing the client connection.

        Note:
            Simulates proper cleanup of client resources
        """
        logger.info("MockTWSClient closed.")
