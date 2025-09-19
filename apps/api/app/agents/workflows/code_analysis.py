"""Code Analysis Agent workflow implementation."""

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, Optional

from app.agents.enums import AgentIdentifier, WorkflowStep
from app.agents.workflows.base import AgentWorkflow


class CodeAnalysisWorkflow(AgentWorkflow):
    """AI agent for comprehensive code analysis and documentation generation."""

    identifier = AgentIdentifier.CODE_ANALYSIS
    module = "development"

    async def prepare(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Prepare workspace and analyze code structure."""
        yield self._emit_step_update(WorkflowStep.PREPARE, "Initializing code analysis workspace")

        # Create workspace directory
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        yield self._emit_progress_update(20, "Workspace created")

        # Copy source files to workspace
        source_files = self._extract_file_paths_from_messages(messages)
        await self._copy_files_to_workspace(source_files)

        yield self._emit_progress_update(50, f"Copied {len(source_files)} files to workspace")

        # Analyze project structure
        project_structure = await self._analyze_project_structure()

        yield self._emit_step_update(
            WorkflowStep.PREPARE,
            "Workspace prepared for code analysis",
            {"structure": project_structure, "file_count": len(source_files)}
        )

    async def run(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Execute code analysis using Claude."""
        yield self._emit_step_update(WorkflowStep.EXECUTE, "Starting code analysis")

        # Prepare prompts
        system_prompt = await self._prepare_system_prompt(
            workspace_dir=self.workspace_dir,
            analysis_type="comprehensive"
        )

        user_prompt = await self._prepare_user_prompt(
            files=list(self.workspace_dir.glob("**/*")),
            analysis_focus="documentation,architecture,patterns"
        )

        # Prepare messages for Claude
        claude_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        yield self._emit_progress_update(70, "Analyzing code with AI")

        # Stream Claude response
        async for chunk in self._stream_claude_response(claude_messages):
            yield chunk

    async def finalize(
        self,
        *,
        session: Any,
        messages: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Save analysis results and clean up."""
        yield self._emit_step_update(WorkflowStep.FINALIZE, "Saving analysis results")

        # Save generated documentation
        output_files = await self._save_analysis_artifacts()

        yield self._emit_progress_update(90, "Analysis artifacts saved")

        # Clean up workspace if needed
        # await self._cleanup_workspace()

        yield self._emit_step_update(
            WorkflowStep.FINALIZE,
            "Code analysis completed successfully",
            {"output_files": output_files}
        )

    def _extract_file_paths_from_messages(self, messages: list[dict[str, Any]]) -> list[Path]:
        """Extract file paths from user messages."""
        file_paths = []
        for message in messages:
            if message.get("type") == "file_upload":
                file_path = Path(message.get("file_path", ""))
                if file_path.exists():
                    file_paths.append(file_path)
        return file_paths

    async def _analyze_project_structure(self) -> dict[str, Any]:
        """Analyze the project structure."""
        structure = {
            "total_files": 0,
            "file_types": {},
            "directories": [],
            "languages": set()
        }

        for file_path in self.workspace_dir.rglob("*"):
            if file_path.is_file():
                structure["total_files"] += 1
                suffix = file_path.suffix.lower()
                structure["file_types"][suffix] = structure["file_types"].get(suffix, 0) + 1

                # Detect language
                language = self._detect_language(suffix)
                if language:
                    structure["languages"].add(language)
            elif file_path.is_dir():
                structure["directories"].append(str(file_path.relative_to(self.workspace_dir)))

        structure["languages"] = list(structure["languages"])
        return structure

    def _detect_language(self, file_extension: str) -> Optional[str]:
        """Detect programming language from file extension."""
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript React",
            ".jsx": "JavaScript React",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".php": "PHP",
            ".rb": "Ruby",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala",
            ".r": "R",
            ".sql": "SQL",
            ".sh": "Shell",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".json": "JSON",
            ".xml": "XML",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".less": "LESS",
            ".md": "Markdown",
            ".rst": "reStructuredText",
        }
        return language_map.get(file_extension)

    async def _save_analysis_artifacts(self) -> list[str]:
        """Save analysis artifacts to the workspace."""
        output_files = []

        # Create output directory
        output_dir = self.workspace_dir / "analysis_output"
        output_dir.mkdir(exist_ok=True)

        # Save README if generated
        readme_path = output_dir / "README.md"
        if not readme_path.exists():
            readme_path.write_text("# Code Analysis Results\n\nGenerated by Code Analysis Agent")
            output_files.append(str(readme_path))

        # Save architecture documentation
        arch_path = output_dir / "ARCHITECTURE.md"
        if not arch_path.exists():
            arch_path.write_text("# Architecture Documentation\n\nGenerated by Code Analysis Agent")
            output_files.append(str(arch_path))

        return output_files
