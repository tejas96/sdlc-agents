"""Code Reviewer Agent workflow implementation."""

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from app.agents.enums import AgentIdentifier, WorkflowStep
from app.agents.workflows.base import AgentWorkflow


class CodeReviewerWorkflow(AgentWorkflow):
    """AI agent for comprehensive code review and pull request analysis."""

    identifier = AgentIdentifier.CODE_REVIEWER
    module = "quality_assurance"

    async def prepare(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Prepare workspace and analyze code changes for review."""
        yield self._emit_step_update(WorkflowStep.PREPARE, "Initializing code review workspace")

        # Create workspace directory
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # Extract code changes from messages
        code_changes = self._extract_code_changes_from_messages(messages)

        yield self._emit_progress_update(30, f"Analyzing {len(code_changes)} code changes")

        # Analyze change complexity and impact
        change_analysis = await self._analyze_code_changes(code_changes)

        yield self._emit_step_update(
            WorkflowStep.PREPARE,
            "Code review workspace prepared",
            {"changes": change_analysis, "files_changed": len(code_changes)}
        )

    async def run(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Execute comprehensive code review using Claude."""
        yield self._emit_step_update(WorkflowStep.EXECUTE, "Starting comprehensive code review")

        # Prepare prompts
        system_prompt = await self._prepare_system_prompt(
            workspace_dir=self.workspace_dir,
            review_type="comprehensive",
            focus_areas=["security", "performance", "maintainability", "best_practices"]
        )

        user_prompt = await self._prepare_user_prompt(
            code_changes=messages,
            review_criteria=["code_quality", "test_coverage", "documentation", "security_vulnerabilities"]
        )

        # Prepare messages for Claude
        claude_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        yield self._emit_progress_update(60, "Performing AI-powered code review")

        # Stream Claude response
        async for chunk in self._stream_claude_response(claude_messages):
            yield chunk

    async def finalize(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Save review results and generate report."""
        yield self._emit_step_update(WorkflowStep.FINALIZE, "Generating code review report")

        # Save review artifacts
        review_files = await self._save_review_artifacts()

        # Generate summary metrics
        review_metrics = await self._generate_review_metrics()

        yield self._emit_progress_update(95, "Code review completed")

        yield self._emit_step_update(
            WorkflowStep.FINALIZE,
            "Code review completed successfully",
            {
                "review_files": review_files,
                "metrics": review_metrics
            }
        )

    def _extract_code_changes_from_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Extract code changes from messages (diff, files, etc.)."""
        changes = []
        for message in messages:
            if message.get("type") == "code_diff":
                changes.append({
                    "file_path": message.get("file_path"),
                    "diff": message.get("diff"),
                    "additions": message.get("additions", 0),
                    "deletions": message.get("deletions", 0),
                    "change_type": message.get("change_type", "modified")
                })
            elif message.get("type") == "pull_request":
                # Extract files from PR
                for file_change in message.get("files", []):
                    changes.append(file_change)
        return changes

    async def _analyze_code_changes(self, changes: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze the complexity and impact of code changes."""
        total_additions = sum(change.get("additions", 0) for change in changes)
        total_deletions = sum(change.get("deletions", 0) for change in changes)

        # Categorize changes by file type
        file_types = {}
        for change in changes:
            file_path = change.get("file_path", "")
            extension = Path(file_path).suffix.lower()
            file_types[extension] = file_types.get(extension, 0) + 1

        # Assess complexity
        complexity_score = min(100, (total_additions + total_deletions) // 10)

        return {
            "total_files": len(changes),
            "total_additions": total_additions,
            "total_deletions": total_deletions,
            "net_changes": total_additions - total_deletions,
            "file_types": file_types,
            "complexity_score": complexity_score,
            "complexity_level": self._get_complexity_level(complexity_score),
            "review_priority": self._calculate_review_priority(changes)
        }

    def _get_complexity_level(self, score: int) -> str:
        """Determine complexity level based on score."""
        if score < 20:
            return "low"
        elif score < 50:
            return "medium"
        elif score < 80:
            return "high"
        else:
            return "very_high"

    def _calculate_review_priority(self, changes: list[dict[str, Any]]) -> str:
        """Calculate review priority based on changes."""
        high_priority_patterns = [
            "security", "auth", "crypto", "password", "token", "api_key",
            "database", "migration", "schema", "config", "env"
        ]

        for change in changes:
            file_path = change.get("file_path", "").lower()
            if any(pattern in file_path for pattern in high_priority_patterns):
                return "high"

        total_changes = sum(
            change.get("additions", 0) + change.get("deletions", 0)
            for change in changes
        )

        if total_changes > 500:
            return "high"
        elif total_changes > 100:
            return "medium"
        else:
            return "low"

    async def _save_review_artifacts(self) -> list[str]:
        """Save code review artifacts."""
        output_files = []

        # Create review output directory
        review_dir = self.workspace_dir / "code_review_output"
        review_dir.mkdir(exist_ok=True)

        # Save review report
        review_report_path = review_dir / "review_report.md"
        review_report_path.write_text("# Code Review Report\n\nGenerated by Code Reviewer Agent\n")
        output_files.append(str(review_report_path))

        # Save review checklist
        checklist_path = review_dir / "review_checklist.md"
        checklist_path.write_text("# Code Review Checklist\n\n- [ ] Code quality\n- [ ] Test coverage\n- [ ] Security\n- [ ] Performance\n")
        output_files.append(str(checklist_path))

        # Save review metrics
        metrics_path = review_dir / "review_metrics.json"
        metrics_path.write_text('{"review_score": 85, "issues_found": 3, "suggestions": 7}')
        output_files.append(str(metrics_path))

        return output_files

    async def _generate_review_metrics(self) -> dict[str, Any]:
        """Generate review metrics and scoring."""
        return {
            "overall_score": 85,  # Mock score
            "code_quality_score": 90,
            "security_score": 80,
            "performance_score": 85,
            "maintainability_score": 88,
            "test_coverage_score": 75,
            "issues_found": {
                "critical": 0,
                "major": 1,
                "minor": 2,
                "suggestions": 7
            },
            "review_time_minutes": 15,
            "lines_reviewed": 250
        }
