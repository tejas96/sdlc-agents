"""Agent execution service for managing AI agent workflows."""

import asyncio
import uuid
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.enums import AgentIdentifier, ExecutionStatus
from app.agents.workflows.code_analysis import CodeAnalysisWorkflow
from app.agents.workflows.code_reviewer import CodeReviewerWorkflow
from app.agents.workflows.requirements_to_tickets import RequirementsToTicketsWorkflow
from app.agents.workflows.root_cause_analysis import RootCauseAnalysisWorkflow
from app.agents.workflows.test_generation import TestGenerationWorkflow
from app.core.config import get_settings
from app.models.agent import Agent


class AgentExecutionService:
    """Service for executing AI agent workflows."""

    def __init__(self):
        """Initialize the agent execution service."""
        self.settings = get_settings()
        self.active_executions: dict[str, dict[str, Any]] = {}

        # Register available workflows
        self.workflow_registry = {
            AgentIdentifier.CODE_ANALYSIS: CodeAnalysisWorkflow,
            AgentIdentifier.TEST_CASE_GENERATION: TestGenerationWorkflow,
            AgentIdentifier.REQUIREMENTS_TO_TICKETS: RequirementsToTicketsWorkflow,
            AgentIdentifier.CODE_REVIEWER: CodeReviewerWorkflow,
            AgentIdentifier.ROOT_CAUSE_ANALYSIS: RootCauseAnalysisWorkflow,
        }

    async def execute_agent(
        self,
        *,
        agent: Agent,
        session: AsyncSession,
        messages: list[dict[str, Any]],
        user_id: int,
        execution_id: Optional[str] = None,
        mcp_configs: Optional[dict[str, Any]] = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Execute an agent workflow and stream responses."""

        # Generate execution ID if not provided
        if not execution_id:
            execution_id = str(uuid.uuid4())

        # Create workspace directory
        workspace_dir = Path(self.settings.AGENTS_DIR) / f"execution_{execution_id}"

        try:
            # Initialize execution tracking
            self.active_executions[execution_id] = {
                "agent_id": agent.id,
                "user_id": user_id,
                "status": ExecutionStatus.RUNNING,
                "workspace_dir": workspace_dir,
                "start_time": asyncio.get_event_loop().time()
            }

            yield {
                "type": "execution_started",
                "execution_id": execution_id,
                "agent_name": agent.name,
                "timestamp": asyncio.get_event_loop().time()
            }

            # Get workflow class
            workflow_class = self.workflow_registry.get(AgentIdentifier(agent.agent_type))
            if not workflow_class:
                raise ValueError(f"No workflow found for agent type: {agent.agent_type}")

            # Create workflow instance
            workflow = workflow_class(
                workspace_dir=workspace_dir,
                mcp_configs=mcp_configs or {},
                integration_service=None,  # TODO: Inject integration service
                system_prompt=agent.prompt_template,
                llm_session_id=execution_id,
                user_id=user_id,
                project_id=agent.project_id,
            )

            # Execute workflow
            async for chunk in workflow.execute_workflow(session=session, messages=messages):
                yield chunk

            # Update execution status
            self.active_executions[execution_id]["status"] = ExecutionStatus.COMPLETED
            self.active_executions[execution_id]["end_time"] = asyncio.get_event_loop().time()

            yield {
                "type": "execution_completed",
                "execution_id": execution_id,
                "status": ExecutionStatus.COMPLETED,
                "timestamp": asyncio.get_event_loop().time()
            }

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")

            # Update execution status
            if execution_id in self.active_executions:
                self.active_executions[execution_id]["status"] = ExecutionStatus.FAILED
                self.active_executions[execution_id]["error"] = str(e)

            yield {
                "type": "execution_failed",
                "execution_id": execution_id,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }

        finally:
            # Clean up execution tracking after some time
            asyncio.create_task(self._cleanup_execution(execution_id, delay=3600))

    async def get_execution_status(self, execution_id: str) -> Optional[dict[str, Any]]:
        """Get the status of an agent execution."""
        return self.active_executions.get(execution_id)

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an active agent execution."""
        if execution_id in self.active_executions:
            self.active_executions[execution_id]["status"] = ExecutionStatus.CANCELLED
            # TODO: Implement actual cancellation logic
            return True
        return False

    async def list_active_executions(self, user_id: Optional[int] = None) -> list[dict[str, Any]]:
        """List active executions, optionally filtered by user."""
        executions = []
        for exec_id, exec_data in self.active_executions.items():
            if user_id is None or exec_data.get("user_id") == user_id:
                executions.append({
                    "execution_id": exec_id,
                    **exec_data
                })
        return executions

    async def _cleanup_execution(self, execution_id: str, delay: int = 3600) -> None:
        """Clean up execution data after a delay."""
        await asyncio.sleep(delay)
        if execution_id in self.active_executions:
            # Clean up workspace directory
            workspace_dir = self.active_executions[execution_id].get("workspace_dir")
            if workspace_dir and isinstance(workspace_dir, Path) and workspace_dir.exists():
                try:
                    import shutil
                    shutil.rmtree(workspace_dir)
                    logger.info(f"Cleaned up workspace: {workspace_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean up workspace {workspace_dir}: {e}")

            # Remove from active executions
            del self.active_executions[execution_id]
            logger.info(f"Cleaned up execution: {execution_id}")


# Global service instance
agent_execution_service = AgentExecutionService()
