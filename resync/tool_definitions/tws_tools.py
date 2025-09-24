from __future__ import annotations

import logging
from typing import Optional

from pydantic import BaseModel, Field

from resync.services.tws_service import OptimizedTWSClient

# --- Logging Setup ---
logger = logging.getLogger(__name__)


class TWSToolReadOnly(BaseModel):
    """
    Base model for TWS tools that provides a shared, lazily-injected TWS client.
    This prevents each tool from creating its own client instance.
    """

    # The client is optional and will be injected by the AgentManager
    tws_client: Optional[OptimizedTWSClient] = Field(
        default=None,
        exclude=True,  # Exclude from Pydantic's model representation
        description="The TWS client instance, injected at runtime.",
    )

    class Config:
        # Allow arbitrary types like the OptimizedTWSClient
        arbitrary_types_allowed = True


class TWSStatusTool(TWSToolReadOnly):
    """A tool for retrieving the overall status of the TWS environment."""

    async def get_tws_status(self) -> str:
        """
        Fetches the current status of TWS workstations and jobs.

        This tool provides a high-level overview of the environment's health,
        summarizing the state of all monitored components.

        Returns:
            A string summarizing the status of workstations and jobs.
        """
        if not self.tws_client:
            logger.error("TWS client not available for TWSStatusTool.")
            return "Erro: Cliente TWS não configurado."

        try:
            logger.info("TWSStatusTool: Fetching system status.")
            status = await self.tws_client.get_system_status()

            # Format the output for the LLM
            workstation_summary = ", ".join(
                [f"{ws.name} ({ws.status})" for ws in status.workstations]
            )
            job_summary = ", ".join(
                [
                    f"{job.name} on {job.workstation} ({job.status})"
                    for job in status.jobs
                ]
            )

            return (
                "Situação atual do TWS:\n"
                f"- Workstations: {workstation_summary or 'Nenhuma encontrada.'}\n"
                f"- Jobs: {job_summary or 'Nenhum encontrado.'}"
            )
        except Exception as e:
            logger.error(f"Error in TWSStatusTool: {e}", exc_info=True)
            return f"Erro ao obter o status do TWS: {e}"


class TWSTroubleshootingTool(TWSToolReadOnly):
    """A tool for diagnosing and providing solutions for TWS issues."""

    async def analyze_failures(self) -> str:
        """
        Analyzes failed jobs and down workstations to identify root causes.

        This tool inspects jobs in an 'ABEND' (abnormally ended) state and
        workstations in a 'DOWN' state, providing a diagnostic summary.

        Returns:
            A string with a diagnostic analysis of TWS failures.
        """
        if not self.tws_client:
            logger.error("TWS client not available for TWSTroubleshootingTool.")
            return "Erro: Cliente TWS não configurado."

        try:
            logger.info("TWSTroubleshootingTool: Fetching system status for analysis.")
            status = await self.tws_client.get_system_status()

            failed_jobs = [j for j in status.jobs if j.status.upper() == "ABEND"]
            down_workstations = [
                w for w in status.workstations if w.status.upper() != "LINKED"
            ]

            if not failed_jobs and not down_workstations:
                return (
                    "Nenhuma falha crítica encontrada. O ambiente TWS parece estável."
                )

            analysis = "Análise de Problemas no TWS:\n"
            if failed_jobs:
                analysis += f"- Jobs com Falha ({len(failed_jobs)}): "
                analysis += ", ".join(
                    [f"{j.name} (workstation: {j.workstation})" for j in failed_jobs]
                )
                analysis += "\n"

            if down_workstations:
                analysis += f"- Workstations com Problemas ({len(down_workstations)}): "
                analysis += ", ".join(
                    [f"{w.name} (status: {w.status})" for w in down_workstations]
                )
                analysis += "\n"

            return analysis

        except Exception as e:
            logger.error(f"Error in TWSTroubleshootingTool: {e}", exc_info=True)
            return f"Erro ao analisar as falhas do TWS: {e}"


# --- Tool Instantiation ---
# Create single, reusable instances of the tools.
tws_status_tool = TWSStatusTool()

tws_troubleshooting_tool = TWSTroubleshootingTool()
