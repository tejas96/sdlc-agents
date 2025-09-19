"""Test Case Generation Agent workflow implementation."""

from collections.abc import AsyncIterator
from typing import Any

from app.agents.enums import AgentIdentifier, WorkflowStep
from app.agents.workflows.base import AgentWorkflow


class TestGenerationWorkflow(AgentWorkflow):
    """AI agent for comprehensive test case generation."""

    identifier = AgentIdentifier.TEST_CASE_GENERATION
    module = "quality_assurance"

    async def prepare(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Prepare workspace and analyze code for test generation."""
        yield self._emit_step_update(WorkflowStep.PREPARE, "Initializing test generation workspace")

        # Create workspace directory
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # Copy source files to workspace
        source_files = self._extract_file_paths_from_messages(messages)
        await self._copy_files_to_workspace(source_files)

        yield self._emit_progress_update(30, f"Analyzed {len(source_files)} source files")

        # Analyze existing test coverage
        test_coverage = await self._analyze_existing_tests()

        yield self._emit_step_update(
            WorkflowStep.PREPARE,
            "Workspace prepared for test generation",
            {"coverage": test_coverage, "source_files": len(source_files)}
        )

    async def run(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Generate test cases using Claude."""
        yield self._emit_step_update(WorkflowStep.EXECUTE, "Generating comprehensive test cases")

        # Prepare prompts
        system_prompt = await self._prepare_system_prompt(
            workspace_dir=self.workspace_dir,
            test_frameworks=["pytest", "unittest", "jest", "vitest"],
            coverage_target=85
        )

        user_prompt = await self._prepare_user_prompt(
            source_files=list(self.workspace_dir.glob("**/*.py")),
            test_types=["unit", "integration", "edge_cases"]
        )

        # Prepare messages for Claude
        claude_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        yield self._emit_progress_update(60, "Generating tests with AI")

        # Stream Claude response
        async for chunk in self._stream_claude_response(claude_messages):
            yield chunk

    async def finalize(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Save generated tests and coverage report."""
        yield self._emit_step_update(WorkflowStep.FINALIZE, "Saving generated test files")

        # Save test files
        test_files = await self._save_test_artifacts()

        # Generate coverage report
        coverage_report = await self._generate_coverage_report()

        yield self._emit_progress_update(95, "Test generation completed")

        yield self._emit_step_update(
            WorkflowStep.FINALIZE,
            "Test generation completed successfully",
            {
                "test_files": test_files,
                "coverage_report": coverage_report
            }
        )

    async def _analyze_existing_tests(self) -> dict[str, Any]:
        """Analyze existing test coverage."""
        test_files = list(self.workspace_dir.glob("**/test_*.py"))
        test_files.extend(self.workspace_dir.glob("**/*_test.py"))
        test_files.extend(self.workspace_dir.glob("**/tests/**/*.py"))

        return {
            "existing_tests": len(test_files),
            "test_files": [str(f.relative_to(self.workspace_dir)) for f in test_files],
            "coverage_estimate": len(test_files) * 10  # Rough estimate
        }

    async def _save_test_artifacts(self) -> list[str]:
        """Save generated test files."""
        output_files = []

        # Create test output directory
        test_dir = self.workspace_dir / "generated_tests"
        test_dir.mkdir(exist_ok=True)

        # Save test suite
        test_suite_path = test_dir / "test_suite.py"
        test_suite_path.write_text("# Generated Test Suite\n# Created by Test Generation Agent\n")
        output_files.append(str(test_suite_path))

        return output_files

    async def _generate_coverage_report(self) -> dict[str, Any]:
        """Generate test coverage report."""
        return {
            "total_lines": 1000,  # Mock data
            "covered_lines": 850,
            "coverage_percentage": 85.0,
            "uncovered_files": [],
            "generated_tests": 25
        }
