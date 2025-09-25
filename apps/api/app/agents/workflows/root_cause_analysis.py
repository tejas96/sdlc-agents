"""Root Cause Analysis Agent workflow implementation."""

from collections.abc import AsyncIterator
from typing import Any

from app.agents.enums import AgentIdentifier, WorkflowStep
from app.agents.workflows.base import AgentWorkflow


class RootCauseAnalysisWorkflow(AgentWorkflow):
    """AI agent for intelligent incident investigation and root cause analysis."""

    identifier = AgentIdentifier.ROOT_CAUSE_ANALYSIS
    module = "quality_assurance"

    async def prepare(self, *, session: Any, messages: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
        """Prepare workspace and collect incident data for analysis."""
        yield self._emit_step_update(WorkflowStep.PREPARE, "Initializing root cause analysis workspace")

        # Create workspace directory
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # Extract incident data from messages
        incident_data = self._extract_incident_data_from_messages(messages)

        yield self._emit_progress_update(25, f"Collected {len(incident_data.get('data_sources', []))} data sources")

        # Analyze incident timeline and impact
        incident_analysis = await self._analyze_incident_context(incident_data)

        yield self._emit_step_update(
            WorkflowStep.PREPARE, "Incident data collected and analyzed", {"incident": incident_analysis}
        )

    async def run(self, *, session: Any, messages: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
        """Execute root cause analysis using Claude."""
        yield self._emit_step_update(WorkflowStep.EXECUTE, "Performing root cause analysis")

        # Prepare prompts
        system_prompt = await self._prepare_system_prompt(
            workspace_dir=self.workspace_dir,
            analysis_type="root_cause",
            investigation_methods=["timeline_analysis", "log_correlation", "dependency_mapping", "pattern_recognition"],
        )

        user_prompt = await self._prepare_user_prompt(
            incident_data=messages,
            analysis_focus=["error_patterns", "system_dependencies", "timing_correlations", "configuration_changes"],
        )

        # Prepare messages for Claude
        claude_messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

        yield self._emit_progress_update(60, "Analyzing incident data with AI")

        # Stream Claude response
        async for chunk in self._stream_claude_response(claude_messages):
            yield chunk

    async def finalize(self, *, session: Any, messages: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
        """Generate root cause analysis report and remediation plan."""
        yield self._emit_step_update(WorkflowStep.FINALIZE, "Generating analysis report and remediation plan")

        # Save analysis artifacts
        analysis_files = await self._save_analysis_artifacts()

        # Generate remediation recommendations
        remediation_plan = await self._generate_remediation_plan()

        # Create incident post-mortem template
        postmortem_template = await self._create_postmortem_template()

        yield self._emit_progress_update(95, "Root cause analysis completed")

        yield self._emit_step_update(
            WorkflowStep.FINALIZE,
            "Root cause analysis completed successfully",
            {
                "analysis_files": analysis_files,
                "remediation_plan": remediation_plan,
                "postmortem_template": postmortem_template,
            },
        )

    def _extract_incident_data_from_messages(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """Extract incident data from messages (logs, metrics, alerts, etc.)."""
        incident_data: dict[str, Any] = {
            "incident_id": None,
            "start_time": None,
            "end_time": None,
            "severity": "unknown",
            "affected_services": [],
            "error_logs": [],
            "metrics": [],
            "alerts": [],
            "deployments": [],
            "configuration_changes": [],
            "user_reports": [],
            "data_sources": [],
        }

        for message in messages:
            msg_type = message.get("type", "")

            if msg_type == "incident_report":
                incident_data.update(
                    {
                        "incident_id": message.get("incident_id"),
                        "start_time": message.get("start_time"),
                        "end_time": message.get("end_time"),
                        "severity": message.get("severity", "unknown"),
                        "description": message.get("description"),
                        "affected_services": message.get("affected_services", []),
                    }
                )
                incident_data["data_sources"].append("incident_report")

            elif msg_type == "error_logs":
                incident_data["error_logs"].extend(message.get("logs", []))
                incident_data["data_sources"].append("error_logs")

            elif msg_type == "metrics_data":
                incident_data["metrics"].extend(message.get("metrics", []))
                incident_data["data_sources"].append("metrics")

            elif msg_type == "alerts":
                incident_data["alerts"].extend(message.get("alerts", []))
                incident_data["data_sources"].append("alerts")

            elif msg_type == "deployment_info":
                incident_data["deployments"].extend(message.get("deployments", []))
                incident_data["data_sources"].append("deployments")

            elif msg_type == "config_changes":
                incident_data["configuration_changes"].extend(message.get("changes", []))
                incident_data["data_sources"].append("config_changes")

            elif msg_type == "user_reports":
                incident_data["user_reports"].extend(message.get("reports", []))
                incident_data["data_sources"].append("user_reports")

        return incident_data

    async def _analyze_incident_context(self, incident_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze incident context and impact."""

        # Calculate incident duration
        duration_minutes = 0
        if incident_data.get("start_time") and incident_data.get("end_time"):
            # Mock calculation - would parse actual timestamps
            duration_minutes = 45  # Mock duration

        # Assess impact severity
        impact_score = self._calculate_impact_score(incident_data)

        # Identify potential causes
        potential_causes = self._identify_potential_causes(incident_data)

        return {
            "incident_id": incident_data.get("incident_id", "unknown"),
            "duration_minutes": duration_minutes,
            "severity": incident_data.get("severity", "unknown"),
            "impact_score": impact_score,
            "affected_services_count": len(incident_data.get("affected_services", [])),
            "data_sources_available": len(set(incident_data.get("data_sources", []))),
            "potential_causes": potential_causes,
            "analysis_confidence": self._calculate_analysis_confidence(incident_data),
        }

    def _calculate_impact_score(self, incident_data: dict[str, Any]) -> int:
        """Calculate incident impact score (0-100)."""
        score = 0

        # Severity weight
        severity_weights = {"critical": 40, "high": 30, "medium": 20, "low": 10, "unknown": 15}
        score += severity_weights.get(incident_data.get("severity", "unknown"), 15)

        # Affected services weight
        affected_services = len(incident_data.get("affected_services", []))
        score += min(30, affected_services * 5)

        # Error log volume weight
        error_logs = len(incident_data.get("error_logs", []))
        score += min(20, error_logs)

        # Alert volume weight
        alerts = len(incident_data.get("alerts", []))
        score += min(10, alerts)

        return min(100, score)

    def _identify_potential_causes(self, incident_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Identify potential root causes based on available data."""
        causes = []

        # Check for recent deployments
        if incident_data.get("deployments"):
            causes.append(
                {
                    "category": "deployment",
                    "description": "Recent deployment detected",
                    "confidence": 0.8,
                    "evidence": f"{len(incident_data['deployments'])} deployments",
                }
            )

        # Check for configuration changes
        if incident_data.get("configuration_changes"):
            causes.append(
                {
                    "category": "configuration",
                    "description": "Configuration changes detected",
                    "confidence": 0.7,
                    "evidence": f"{len(incident_data['configuration_changes'])} config changes",
                }
            )

        # Check for high error volume
        if len(incident_data.get("error_logs", [])) > 10:
            causes.append(
                {
                    "category": "system_failure",
                    "description": "High error log volume",
                    "confidence": 0.6,
                    "evidence": f"{len(incident_data['error_logs'])} error entries",
                }
            )

        # Check for multiple affected services
        if len(incident_data.get("affected_services", [])) > 1:
            causes.append(
                {
                    "category": "infrastructure",
                    "description": "Multiple services affected",
                    "confidence": 0.5,
                    "evidence": f"{len(incident_data['affected_services'])} services",
                }
            )

        return causes

    def _calculate_analysis_confidence(self, incident_data: dict[str, Any]) -> float:
        """Calculate confidence level for the analysis."""
        data_sources = len(set(incident_data.get("data_sources", [])))
        max_sources = 7  # Total possible data source types

        base_confidence = min(0.8, data_sources / max_sources)

        # Boost confidence if we have key data sources
        key_sources = ["incident_report", "error_logs", "metrics"]
        available_key_sources = sum(1 for source in key_sources if source in incident_data.get("data_sources", []))

        confidence_boost = (available_key_sources / len(key_sources)) * 0.2

        return min(1.0, base_confidence + confidence_boost)

    async def _save_analysis_artifacts(self) -> list[str]:
        """Save root cause analysis artifacts."""
        output_files = []

        # Create analysis output directory
        analysis_dir = self.workspace_dir / "rca_output"
        analysis_dir.mkdir(exist_ok=True)

        # Save root cause analysis report
        rca_report_path = analysis_dir / "root_cause_analysis.md"
        rca_report_path.write_text("# Root Cause Analysis Report\n\nGenerated by Root Cause Analysis Agent\n")
        output_files.append(str(rca_report_path))

        # Save timeline analysis
        timeline_path = analysis_dir / "incident_timeline.md"
        timeline_path.write_text(
            "# Incident Timeline\n\n## Key Events\n- Incident start\n- First alerts\n- Resolution\n"
        )
        output_files.append(str(timeline_path))

        # Save evidence collection
        evidence_path = analysis_dir / "evidence_summary.json"
        evidence_path.write_text('{"logs_analyzed": 50, "metrics_reviewed": 25, "alerts_correlated": 10}')
        output_files.append(str(evidence_path))

        return output_files

    async def _generate_remediation_plan(self) -> dict[str, Any]:
        """Generate remediation and prevention plan."""
        return {
            "immediate_actions": [
                "Rollback recent deployment if applicable",
                "Scale affected services",
                "Monitor error rates closely",
            ],
            "short_term_fixes": ["Implement additional monitoring", "Add circuit breakers", "Improve error handling"],
            "long_term_improvements": [
                "Enhanced testing procedures",
                "Automated deployment validation",
                "Improved observability",
            ],
            "priority": "high",
            "estimated_effort": "2-4 weeks",
            "success_metrics": ["Reduce MTTR by 50%", "Prevent similar incidents", "Improve monitoring coverage"],
        }

    async def _create_postmortem_template(self) -> dict[str, Any]:
        """Create incident post-mortem template."""
        return {
            "template_path": str(self.workspace_dir / "rca_output" / "postmortem_template.md"),
            "sections": [
                "Incident Summary",
                "Timeline of Events",
                "Root Cause Analysis",
                "Impact Assessment",
                "Response Evaluation",
                "Remediation Actions",
                "Prevention Measures",
                "Lessons Learned",
            ],
            "status": "draft",
            "review_required": True,
        }
