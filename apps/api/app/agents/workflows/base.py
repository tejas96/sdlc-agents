"""Base agent workflow implementation."""

import asyncio
import shutil
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, Optional

from claude_code_sdk import ClaudeSDKClient
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from app.agents.enums import AgentIdentifier, WorkflowStep
from app.core.config import get_settings


class AgentWorkflow(ABC):
    """Base class for all agent workflows."""

    identifier: AgentIdentifier
    module: str

    def __init__(
        self,
        *,
        workspace_dir: Path,
        mcp_configs: dict[str, Any],
        integration_service: Any = None,
        system_prompt: Optional[str] = None,
        llm_session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        project_id: Optional[int] = None,
    ) -> None:
        """Initialize the agent workflow."""
        self.workspace_dir = workspace_dir
        self.mcp_configs = mcp_configs
        self.integration_service = integration_service
        self.system_prompt = system_prompt
        self.llm_session_id = llm_session_id
        self.user_id = user_id
        self.project_id = project_id

        # Initialize Claude SDK Client
        settings = get_settings()
        self.claude_sdk = ClaudeSDKClient(
            api_key=settings.ANTHROPIC_API_KEY,
        )

        # Template environment
        self.template_env = Environment(
            loader=FileSystemLoader(Path(__file__).parent.parent / "templates")
        )

    async def execute_workflow(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Execute the complete agent workflow with all steps."""
        try:
            # Step 1: Preparation
            async for chunk in self.prepare(session=session, messages=messages):
                yield chunk

            # Step 2: Main execution
            async for chunk in self.run(session=session, messages=messages):
                yield chunk

            # Step 3: Finalization
            async for chunk in self.finalize(session=session, messages=messages):
                yield chunk

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            yield {
                "type": "error",
                "step": "execution",
                "message": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }

    @abstractmethod
    async def prepare(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Perform pre-execution setup."""
        pass

    @abstractmethod
    async def run(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Execute the main agent workflow."""
        pass

    @abstractmethod
    async def finalize(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Perform post-execution cleanup."""
        pass

    async def _prepare_system_prompt(self, **kwargs) -> str:
        """Prepare the system prompt using templates."""
        template_name = f"{self.identifier.value}/system.j2"
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            logger.warning(f"Failed to load template {template_name}: {e}")
            return self.system_prompt or f"You are an AI assistant specialized in {self.identifier.value.replace('_', ' ')}."

    async def _prepare_user_prompt(self, **kwargs) -> str:
        """Prepare the user prompt using templates."""
        template_name = f"{self.identifier.value}/user.j2"
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            logger.warning(f"Failed to load template {template_name}: {e}")
            return "Please analyze the provided files and generate appropriate output."

    async def _prepare_user_followup_prompt(self, **kwargs) -> str:
        """Prepare follow-up prompt using templates."""
        template_name = f"{self.identifier.value}/followup.j2"
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            logger.warning(f"Failed to load template {template_name}: {e}")
            return "Please continue with the analysis."

    async def _copy_files_to_workspace(self, file_paths: list[Path]) -> None:
        """Copy files to the agent workspace."""
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        for file_path in file_paths:
            if file_path.exists():
                dest_path = self.workspace_dir / file_path.name
                shutil.copy2(file_path, dest_path)
                logger.info(f"Copied {file_path} to {dest_path}")

    async def _cleanup_workspace(self) -> None:
        """Clean up the agent workspace."""
        if self.workspace_dir.exists():
            shutil.rmtree(self.workspace_dir)
            logger.info(f"Cleaned up workspace: {self.workspace_dir}")

    async def _stream_claude_response(
        self,
        messages: list[dict[str, str]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream responses from Claude SDK."""
        try:
            # Convert messages to Claude format
            claude_messages = []
            for msg in messages:
                claude_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

            # For now, create a mock streaming response
            # TODO: Implement actual Claude SDK streaming when API is available
            mock_response = f"Analysis complete for {len(messages)} messages. This is a mock response until Claude API key is configured."

            # Simulate streaming by yielding chunks
            words = mock_response.split()
            for i, word in enumerate(words):
                yield {
                    "type": "claude_response",
                    "data": {
                        "content": word + " ",
                        "role": "assistant"
                    },
                    "timestamp": asyncio.get_event_loop().time()
                }
                await asyncio.sleep(0.1)  # Simulate processing time

        except Exception as e:
            logger.error(f"Claude streaming failed: {e}")
            yield {
                "type": "error",
                "message": f"Claude API error: {e!s}",
                "timestamp": asyncio.get_event_loop().time()
            }

    def _emit_step_update(self, step: WorkflowStep, message: str, data: Any = None) -> dict[str, Any]:
        """Emit a workflow step update."""
        return {
            "type": "step_update",
            "step": step.value,
            "message": message,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }

    def _emit_progress_update(self, progress: int, message: str) -> dict[str, Any]:
        """Emit a progress update."""
        return {
            "type": "progress",
            "progress": progress,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        }
