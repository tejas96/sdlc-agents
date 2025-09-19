"""Requirements to Tickets Agent workflow implementation."""

from collections.abc import AsyncIterator
from typing import Any

from app.agents.enums import AgentIdentifier, WorkflowStep
from app.agents.workflows.base import AgentWorkflow


class RequirementsToTicketsWorkflow(AgentWorkflow):
    """AI agent for converting requirements into structured development tickets."""

    identifier = AgentIdentifier.REQUIREMENTS_TO_TICKETS
    module = "project_management"

    async def prepare(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Prepare requirements analysis workspace."""
        yield self._emit_step_update(WorkflowStep.PREPARE, "Initializing requirements analysis")

        # Create workspace directory
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # Extract requirements documents
        requirements_docs = self._extract_requirements_from_messages(messages)

        yield self._emit_progress_update(25, f"Found {len(requirements_docs)} requirements documents")

        # Analyze requirements structure
        requirements_analysis = await self._analyze_requirements_structure(requirements_docs)

        yield self._emit_step_update(
            WorkflowStep.PREPARE,
            "Requirements analysis prepared",
            {"analysis": requirements_analysis}
        )

    async def run(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Generate tickets from requirements using Claude."""
        yield self._emit_step_update(WorkflowStep.EXECUTE, "Converting requirements to tickets")

        # Prepare prompts
        system_prompt = await self._prepare_system_prompt(
            workspace_dir=self.workspace_dir,
            ticket_format="jira",
            estimation_method="story_points"
        )

        user_prompt = await self._prepare_user_prompt(
            requirements=messages,
            output_format="structured_tickets"
        )

        # Prepare messages for Claude
        claude_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        yield self._emit_progress_update(60, "Generating tickets with AI")

        # Stream Claude response
        async for chunk in self._stream_claude_response(claude_messages):
            yield chunk

    async def finalize(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Save generated tickets and create integration tasks."""
        yield self._emit_step_update(WorkflowStep.FINALIZE, "Saving generated tickets")

        # Save ticket artifacts
        ticket_files = await self._save_ticket_artifacts()

        # Create Jira tickets if integration is available
        jira_tickets = await self._create_jira_tickets_if_available()

        yield self._emit_progress_update(95, "Tickets saved and created")

        yield self._emit_step_update(
            WorkflowStep.FINALIZE,
            "Requirements to tickets conversion completed",
            {
                "ticket_files": ticket_files,
                "jira_tickets": jira_tickets
            }
        )

    def _extract_requirements_from_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Extract requirements documents from messages."""
        requirements = []
        for message in messages:
            if message.get("content"):
                requirements.append({
                    "content": message["content"],
                    "type": message.get("type", "text"),
                    "metadata": message.get("metadata", {})
                })
        return requirements

    async def _analyze_requirements_structure(self, requirements: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze the structure of requirements."""
        return {
            "total_requirements": len(requirements),
            "estimated_epics": max(1, len(requirements) // 5),
            "estimated_stories": len(requirements),
            "estimated_tasks": len(requirements) * 3,
            "complexity_distribution": {
                "simple": len(requirements) // 3,
                "medium": len(requirements) // 2,
                "complex": len(requirements) // 6
            }
        }

    async def _save_ticket_artifacts(self) -> list[str]:
        """Save generated ticket artifacts."""
        output_files = []

        # Create tickets output directory
        tickets_dir = self.workspace_dir / "generated_tickets"
        tickets_dir.mkdir(exist_ok=True)

        # Save tickets as JSON
        tickets_json_path = tickets_dir / "tickets.json"
        tickets_json_path.write_text('{"tickets": [], "epics": [], "stories": []}')
        output_files.append(str(tickets_json_path))

        # Save tickets as CSV for import
        tickets_csv_path = tickets_dir / "tickets.csv"
        tickets_csv_path.write_text("Title,Description,Type,Priority,Story Points\n")
        output_files.append(str(tickets_csv_path))

        return output_files

    async def _create_jira_tickets_if_available(self) -> dict[str, Any]:
        """Create Jira tickets if integration is configured."""
        if not self.integration_service:
            return {"created": 0, "message": "No Jira integration configured"}

        # TODO: Implement Jira ticket creation
        return {
            "created": 0,
            "message": "Jira integration not yet implemented",
            "tickets": []
        }
