"""# type: ignore
Service layer for optimized module communication in Resync.  # type: ignore

This module provides a service layer that abstracts the communication between  # type: ignore
different modules, reducing direct dependencies and enabling better decoupling.  # type: ignore
"""  # type: ignore

from __future__ import annotations  # type: ignore

import asyncio  # type: ignore
import logging  # type: ignore
from abc import abstractmethod  # type: ignore
from typing import Any, Optional, Protocol, Union  # type: ignore

from resync.core.cache_hierarchy import \
    get_cache_hierarchy  # type: ignore[attr-defined]
from resync.core.interfaces import (  # type: ignore[attr-defined]
    IAgentManager, IKnowledgeGraph, ITWSClient)
from resync.core.logger import \
    log_with_correlation  # type: ignore[attr-defined]
from resync.models.tws import (CriticalJob,  # type: ignore[attr-defined]
                               JobStatus, SystemStatus, WorkstationStatus)


class ITWSService(Protocol):  # type: ignore
    """Protocol for TWS service operations."""  # type: ignore

    @abstractmethod  # type: ignore
    async def get_system_status(self) -> SystemStatus:  # type: ignore
        """Get the overall system status."""  # type: ignore
        pass  # type: ignore

    @abstractmethod  # type: ignore
    async def get_workstations_status(self) -> list[WorkstationStatus]:  # type: ignore
        """Get the status of all workstations."""  # type: ignore
        pass  # type: ignore

    @abstractmethod  # type: ignore
    async def get_jobs_status(self) -> list[JobStatus]:  # type: ignore
        """Get the status of all jobs."""  # type: ignore
        pass  # type: ignore

    @abstractmethod  # type: ignore
    async def get_critical_path_status(self) -> list[CriticalJob]:  # type: ignore
        """Get the status of jobs on the critical path."""  # type: ignore
        pass  # type: ignore

    @abstractmethod  # type: ignore
    async def get_job_status_batch(self, job_ids: list[str]) -> dict[str, Optional[JobStatus]]:  # type: ignore
        """Get the status of multiple jobs in a batch."""  # type: ignore
        pass  # type: ignore


class IAgentService(Protocol):  # type: ignore
    """Protocol for agent service operations."""  # type: ignore

    @abstractmethod  # type: ignore
    async def get_agent(self, agent_id: str) -> Any:  # type: ignore
        """Get an agent by ID."""  # type: ignore
        pass  # type: ignore

    @abstractmethod  # type: ignore
    async def get_all_agents(self) -> list[Any]:  # type: ignore
        """Get all agents."""  # type: ignore
        pass  # type: ignore


class IKnowledgeService(Protocol):  # type: ignore
    """Protocol for knowledge service operations."""  # type: ignore

    @abstractmethod  # type: ignore
    async def search_similar_issues(self, query: str, limit: int = 5) -> list[dict[str, Any]]:  # type: ignore
        """Search for similar issues in the knowledge graph."""  # type: ignore
        pass  # type: ignore

    @abstractmethod  # type: ignore
    async def get_relevant_context(self, user_query: str) -> str:  # type: ignore
        """Get relevant context for a user query."""  # type: ignore
        pass  # type: ignore


class TWSService:  # type: ignore
    """Concrete implementation of TWS service."""  # type: ignore

    def __init__(self, tws_client: ITWSClient) -> None:  # type: ignore
        self.tws_client = tws_client  # type: ignore
        self.cache = get_cache_hierarchy()  # type: ignore
        self.logger = logging.getLogger(__name__)  # type: ignore

    async def get_system_status(self) -> SystemStatus:  # type: ignore
        """Get the overall system status."""  # type: ignore
        try:  # type: ignore
            # Try to retrieve from cache first
            cache_key = "service_system_status"  # type: ignore
            cached_result = await self.cache.get(cache_key)  # type: ignore
            if cached_result:  # type: ignore
                return SystemStatus(**cached_result)  # type: ignore

            # Fetch from TWS client if not in cache
            result = await self.tws_client.get_system_status()  # type: ignore

            # Store in cache
            await self.cache.set(cache_key, result.dict(), ttl=30)  # type: ignore

            return result  # type: ignore
        except Exception as e:  # type: ignore
            log_with_correlation(  # type: ignore
                logging.ERROR,  # type: ignore
                f"Failed to get system status: {str(e)}",  # type: ignore
                component="tws_service",  # type: ignore
            )  # type: ignore
            raise  # type: ignore

    async def get_workstations_status(self) -> list[WorkstationStatus]:  # type: ignore
        """Get the status of all workstations."""  # type: ignore
        try:  # type: ignore
            # Try to retrieve from cache first
            cache_key = "service_workstations_status"  # type: ignore
            cached_result = await self.cache.get(cache_key)  # type: ignore
            if cached_result:  # type: ignore
                return [WorkstationStatus(**ws) for ws in cached_result]  # type: ignore

            # Fetch from TWS client if not in cache
            result = await self.tws_client.get_workstations_status()  # type: ignore

            # Store in cache
            await self.cache.set(cache_key, [ws.dict() for ws in result], ttl=30)  # type: ignore

            return result  # type: ignore
        except Exception as e:  # type: ignore
            log_with_correlation(  # type: ignore
                logging.ERROR,  # type: ignore
                f"Failed to get workstations status: {str(e)}",  # type: ignore
                component="tws_service",  # type: ignore
            )  # type: ignore
            raise  # type: ignore

    async def get_jobs_status(self) -> list[JobStatus]:  # type: ignore
        """Get the status of all jobs."""  # type: ignore
        try:  # type: ignore
            # Try to retrieve from cache first
            cache_key = "service_jobs_status"  # type: ignore
            cached_result = await self.cache.get(cache_key)  # type: ignore
            if cached_result:  # type: ignore
                return [JobStatus(**job) for job in cached_result]  # type: ignore

            # Fetch from TWS client if not in cache
            result = await self.tws_client.get_jobs_status()  # type: ignore

            # Store in cache
            await self.cache.set(cache_key, [job.dict() for job in result], ttl=30)  # type: ignore

            return result  # type: ignore
        except Exception as e:  # type: ignore
            log_with_correlation(  # type: ignore
                logging.ERROR,  # type: ignore
                f"Failed to get jobs status: {str(e)}",  # type: ignore
                component="tws_service",  # type: ignore
            )  # type: ignore
            raise  # type: ignore

    async def get_critical_path_status(self) -> list[CriticalJob]:  # type: ignore
        """Get the status of jobs on the critical path."""  # type: ignore
        try:  # type: ignore
            # Try to retrieve from cache first
            cache_key = "service_critical_path_status"  # type: ignore
            cached_result = await self.cache.get(cache_key)  # type: ignore
            if cached_result:  # type: ignore
                return [CriticalJob(**cj) for cj in cached_result]  # type: ignore

            # Fetch from TWS client if not in cache
            result = await self.tws_client.get_critical_path_status()  # type: ignore

            # Store in cache
            await self.cache.set(cache_key, [cj.dict() for cj in result], ttl=30)  # type: ignore

            return result  # type: ignore
        except Exception as e:  # type: ignore
            log_with_correlation(  # type: ignore
                logging.ERROR,  # type: ignore
                f"Failed to get critical path status: {str(e)}",  # type: ignore
                component="tws_service",  # type: ignore
            )  # type: ignore
            raise  # type: ignore

    async def get_job_status_batch(self, job_ids: list[str]) -> dict[str, Optional[JobStatus]]:  # type: ignore
        """Get the status of multiple jobs in a batch."""  # type: ignore
        try:  # type: ignore
            results = {}  # type: ignore
            uncached_job_ids = []  # type: ignore

            # Check cache for each job
            for job_id in job_ids:  # type: ignore
                cache_key = f"service_job_status_{job_id}"  # type: ignore
                cached_result = await self.cache.get(cache_key)  # type: ignore
                if cached_result:  # type: ignore
                    results[job_id] = JobStatus(**cached_result) if cached_result else None  # type: ignore
                else:  # type: ignore
                    uncached_job_ids.append(job_id)  # type: ignore

            # Fetch uncached jobs from TWS client
            if uncached_job_ids:  # type: ignore
                uncached_results = await self.tws_client.get_job_status_batch(uncached_job_ids)  # type: ignore
                for job_id, job_status in uncached_results.items():  # type: ignore
                    results[job_id] = job_status  # type: ignore
                    # Cache the individual result
                    await self.cache.set(  # type: ignore
                        f"service_job_status_{job_id}",  # type: ignore
                        job_status.dict() if job_status else None,  # type: ignore
                        ttl=30,  # type: ignore
                    )  # type: ignore

            return results  # type: ignore
        except Exception as e:  # type: ignore
            log_with_correlation(  # type: ignore
                logging.ERROR,  # type: ignore
                f"Failed to get job status batch: {str(e)}",  # type: ignore
                component="tws_service",  # type: ignore
            )  # type: ignore
            raise  # type: ignore


class AgentService:  # type: ignore
    """Concrete implementation of agent service."""  # type: ignore

    def __init__(self, agent_manager: IAgentManager) -> None:  # type: ignore
        self.agent_manager = agent_manager  # type: ignore
        self.logger = logging.getLogger(__name__)  # type: ignore

    async def get_agent(self, agent_id: str) -> Any:  # type: ignore
        """Get an agent by ID."""  # type: ignore
        try:  # type: ignore
            return await self.agent_manager.get_agent(agent_id)  # type: ignore
        except Exception as e:  # type: ignore
            log_with_correlation(  # type: ignore
                logging.ERROR,  # type: ignore
                f"Failed to get agent {agent_id}: {str(e)}",  # type: ignore
                component="agent_service",  # type: ignore
            )  # type: ignore
            raise  # type: ignore

    async def get_all_agents(self) -> list[Any]:  # type: ignore
        """Get all agents."""  # type: ignore
        try:  # type: ignore
            return await self.agent_manager.get_all_agents()  # type: ignore
        except Exception as e:  # type: ignore
            log_with_correlation(  # type: ignore
                logging.ERROR,  # type: ignore
                f"Failed to get all agents: {str(e)}",  # type: ignore
                component="agent_service",  # type: ignore
            )  # type: ignore
            raise  # type: ignore


class KnowledgeService:  # type: ignore
    """Concrete implementation of knowledge service."""  # type: ignore

    def __init__(self, knowledge_graph: IKnowledgeGraph) -> None:  # type: ignore
        self.knowledge_graph = knowledge_graph  # type: ignore
        self.logger = logging.getLogger(__name__)  # type: ignore

    async def search_similar_issues(self, query: str, limit: int = 5) -> list[dict[str, Any]]:  # type: ignore
        """Search for similar issues in the knowledge graph."""  # type: ignore
        try:  # type: ignore
            return await self.knowledge_graph.search_similar_issues(query, limit=limit)  # type: ignore
        except Exception as e:  # type: ignore
            log_with_correlation(  # type: ignore
                logging.ERROR,  # type: ignore
                f"Failed to search similar issues: {str(e)}",  # type: ignore
                component="knowledge_service",  # type: ignore
            )  # type: ignore
            raise  # type: ignore

    async def get_relevant_context(self, user_query: str) -> str:  # type: ignore
        """Get relevant context for a user query."""  # type: ignore
        try:  # type: ignore
            return await self.knowledge_graph.get_relevant_context(user_query)  # type: ignore
        except Exception as e:  # type: ignore
            log_with_correlation(  # type: ignore
                logging.ERROR,  # type: ignore
                f"Failed to get relevant context: {str(e)}",  # type: ignore
                component="knowledge_service",  # type: ignore
            )  # type: ignore
            raise  # type: ignore


class ServiceFactory:  # type: ignore
    """Factory for creating service instances with proper dependency injection."""  # type: ignore

    @staticmethod  # type: ignore
    def create_tws_service(tws_client: ITWSClient) -> ITWSService:  # type: ignore
        """Create a TWS service instance."""  # type: ignore
        return TWSService(tws_client)  # type: ignore

    @staticmethod  # type: ignore
    def create_agent_service(agent_manager: IAgentManager) -> IAgentService:  # type: ignore
        """Create an agent service instance."""  # type: ignore
        return AgentService(agent_manager)  # type: ignore

    @staticmethod  # type: ignore
    def create_knowledge_service(knowledge_graph: IKnowledgeGraph) -> IKnowledgeService:  # type: ignore
        """Create a knowledge service instance."""  # type: ignore
        return KnowledgeService(knowledge_graph)  # type: ignore
