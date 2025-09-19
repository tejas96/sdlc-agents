"""Audit logging service for security and compliance tracking."""

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import Request
from loguru import logger
from sqlalchemy import and_, desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditEventType, AuditLog, AuditLogCreate, AuditLogFilter, AuditSeverity
from app.models.user import User


class AuditService:
    """Service for managing audit logs and compliance tracking."""

    async def log_event(
        self,
        event_data: AuditLogCreate,
        session: AsyncSession,
        request: Optional[Request] = None,
        user: Optional[User] = None
    ) -> AuditLog:
        """Log an audit event."""
        try:
            # Extract event category from event type
            event_category = event_data.event_type.value.split(".")[0]

            # Prepare audit log entry
            audit_log = AuditLog(
                event_type=event_data.event_type,
                event_category=event_category,
                severity=event_data.severity,
                user_id=event_data.user_id or (user.id if user else None),
                username=event_data.username or (user.email if user else None),
                session_id=event_data.session_id,
                action=event_data.action,
                description=event_data.description,
                resource_type=event_data.resource_type,
                resource_id=event_data.resource_id,
                resource_name=event_data.resource_name,
                success=event_data.success,
                error_message=event_data.error_message,
                duration_ms=event_data.duration_ms,
                response_status=event_data.response_status,
                risk_score=event_data.risk_score or self._calculate_risk_score(event_data),
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            )

            # Extract request information if available
            if request:
                audit_log.ip_address = self._get_client_ip(request)
                audit_log.user_agent = request.headers.get("user-agent")
                audit_log.request_method = request.method
                audit_log.request_path = str(request.url.path)
            else:
                audit_log.ip_address = event_data.ip_address
                audit_log.user_agent = event_data.user_agent
                audit_log.request_method = event_data.request_method
                audit_log.request_path = event_data.request_path

            # Serialize metadata and request data
            if event_data.metadata:
                audit_log.metadata = json.dumps(event_data.metadata)

            if event_data.request_data:
                # Sanitize sensitive data before logging
                sanitized_data = self._sanitize_request_data(event_data.request_data)
                audit_log.request_data = json.dumps(sanitized_data)

            if event_data.compliance_tags:
                audit_log.compliance_tags = json.dumps(event_data.compliance_tags)

            # Save to database
            session.add(audit_log)
            await session.commit()
            await session.refresh(audit_log)

            # Log high-severity events to application logs
            if event_data.severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
                logger.warning(
                    f"High-severity audit event: {event_data.event_type.value} - {event_data.description}",
                    extra={
                        "audit_id": audit_log.id,
                        "user_id": audit_log.user_id,
                        "ip_address": audit_log.ip_address,
                        "severity": event_data.severity.value
                    }
                )

            return audit_log

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            await session.rollback()
            # Don't raise exception to avoid disrupting main application flow
            return None

    async def get_audit_logs(
        self,
        filters: AuditLogFilter,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[AuditLog], int]:
        """Get audit logs with filtering and pagination."""
        try:
            # Build query conditions
            conditions = []

            if filters.event_type:
                conditions.append(AuditLog.event_type == filters.event_type)

            if filters.event_category:
                conditions.append(AuditLog.event_category == filters.event_category)

            if filters.severity:
                conditions.append(AuditLog.severity == filters.severity)

            if filters.user_id:
                conditions.append(AuditLog.user_id == filters.user_id)

            if filters.username:
                conditions.append(AuditLog.username.ilike(f"%{filters.username}%"))

            if filters.resource_type:
                conditions.append(AuditLog.resource_type == filters.resource_type)

            if filters.resource_id:
                conditions.append(AuditLog.resource_id == filters.resource_id)

            if filters.success is not None:
                conditions.append(AuditLog.success == filters.success)

            if filters.ip_address:
                conditions.append(AuditLog.ip_address == filters.ip_address)

            if filters.date_from:
                conditions.append(AuditLog.created_at >= filters.date_from)

            if filters.date_to:
                conditions.append(AuditLog.created_at <= filters.date_to)

            if filters.min_risk_score is not None:
                conditions.append(AuditLog.risk_score >= filters.min_risk_score)

            if filters.max_risk_score is not None:
                conditions.append(AuditLog.risk_score <= filters.max_risk_score)

            # Build query
            query = select(AuditLog)
            if conditions:
                query = query.where(and_(*conditions))

            # Get total count
            count_query = select(func.count()).select_from(
                query.subquery()
            )
            count_result = await session.execute(count_query)
            total_count = count_result.scalar()

            # Apply ordering, pagination
            query = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)

            # Execute query
            result = await session.execute(query)
            audit_logs = result.scalars().all()

            return audit_logs, total_count

        except Exception as e:
            logger.error(f"Failed to get audit logs: {e}")
            return [], 0

    async def get_user_activity(
        self,
        user_id: int,
        session: AsyncSession,
        days: int = 30,
        limit: int = 50
    ) -> list[AuditLog]:
        """Get recent activity for a specific user."""
        try:
            from_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            query = (
                select(AuditLog)
                .where(
                    AuditLog.user_id == user_id,
                    AuditLog.created_at >= from_date
                )
                .order_by(desc(AuditLog.created_at))
                .limit(limit)
            )

            result = await session.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Failed to get user activity: {e}")
            return []

    async def get_security_events(
        self,
        session: AsyncSession,
        hours: int = 24,
        min_risk_score: int = 50
    ) -> list[AuditLog]:
        """Get recent security-related events."""
        try:
            from_datetime = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

            security_categories = ["auth", "security", "rbac"]

            query = (
                select(AuditLog)
                .where(
                    AuditLog.event_category.in_(security_categories),
                    AuditLog.created_at >= from_datetime,
                    AuditLog.risk_score >= min_risk_score
                )
                .order_by(desc(AuditLog.risk_score), desc(AuditLog.created_at))
            )

            result = await session.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Failed to get security events: {e}")
            return []

    async def generate_compliance_report(
        self,
        session: AsyncSession,
        start_date: str,
        end_date: str,
        compliance_tags: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Generate a compliance report for a date range."""
        try:
            conditions = [
                AuditLog.created_at >= start_date,
                AuditLog.created_at <= end_date
            ]

            if compliance_tags:
                # Filter by compliance tags (stored as JSON)
                for tag in compliance_tags:
                    conditions.append(AuditLog.compliance_tags.contains(tag))

            query = select(AuditLog).where(and_(*conditions))
            result = await session.execute(query)
            logs = result.scalars().all()

            # Generate report statistics
            report = {
                "period": {"start": start_date, "end": end_date},
                "total_events": len(logs),
                "events_by_category": {},
                "events_by_severity": {},
                "failed_events": 0,
                "high_risk_events": 0,
                "users_active": set(),
                "compliance_summary": {
                    "authentication_events": 0,
                    "authorization_events": 0,
                    "data_access_events": 0,
                    "admin_events": 0
                }
            }

            for log in logs:
                # Count by category
                category = log.event_category
                report["events_by_category"][category] = report["events_by_category"].get(category, 0) + 1

                # Count by severity
                severity = log.severity.value
                report["events_by_severity"][severity] = report["events_by_severity"].get(severity, 0) + 1

                # Count failed events
                if not log.success:
                    report["failed_events"] += 1

                # Count high-risk events
                if log.risk_score and log.risk_score >= 70:
                    report["high_risk_events"] += 1

                # Track active users
                if log.user_id:
                    report["users_active"].add(log.user_id)

                # Compliance categorization
                if log.event_category == "auth":
                    report["compliance_summary"]["authentication_events"] += 1
                elif log.event_category == "rbac":
                    report["compliance_summary"]["authorization_events"] += 1
                elif log.event_type in [AuditEventType.PROJECT_VIEW, AuditEventType.FILE_DOWNLOAD]:
                    report["compliance_summary"]["data_access_events"] += 1
                elif log.event_category == "system":
                    report["compliance_summary"]["admin_events"] += 1

            report["users_active"] = len(report["users_active"])

            return report

        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            return {}

    def _calculate_risk_score(self, event_data: AuditLogCreate) -> int:
        """Calculate risk score for an audit event."""
        score = 0

        # Base scores by event type
        high_risk_events = [
            AuditEventType.LOGIN_FAILURE,
            AuditEventType.UNAUTHORIZED_ACCESS,
            AuditEventType.SYSTEM_CONFIG_CHANGE,
            AuditEventType.ROLE_ASSIGN,
            AuditEventType.PERMISSION_GRANT,
            AuditEventType.DATA_EXPORT,
            AuditEventType.ADMIN_ACTION
        ]

        medium_risk_events = [
            AuditEventType.PASSWORD_CHANGE,
            AuditEventType.USER_DELETE,
            AuditEventType.PROJECT_DELETE,
            AuditEventType.AGENT_DELETE,
            AuditEventType.INTEGRATION_DELETE
        ]

        if event_data.event_type in high_risk_events:
            score += 40
        elif event_data.event_type in medium_risk_events:
            score += 20
        else:
            score += 5

        # Severity multiplier
        severity_multipliers = {
            AuditSeverity.LOW: 1,
            AuditSeverity.MEDIUM: 1.5,
            AuditSeverity.HIGH: 2,
            AuditSeverity.CRITICAL: 3
        }
        score = int(score * severity_multipliers.get(event_data.severity, 1))

        # Failure penalty
        if not event_data.success:
            score += 30

        # Cap at 100
        return min(100, score)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to client host
        return getattr(request.client, "host", "unknown")

    def _sanitize_request_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Sanitize sensitive data from request data before logging."""
        sensitive_keys = {
            "password", "passwd", "pwd", "secret", "token", "key", "auth",
            "authorization", "credential", "private", "confidential"
        }

        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_request_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_request_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized

    # Convenience methods for common audit events
    async def log_login_success(self, user: User, session: AsyncSession, request: Optional[Request] = None):
        """Log successful login."""
        await self.log_event(
            AuditLogCreate(
                event_type=AuditEventType.LOGIN_SUCCESS,
                severity=AuditSeverity.LOW,
                action="login",
                description=f"User {user.email} logged in successfully",
                user_id=user.id,
                username=user.email
            ),
            session,
            request,
            user
        )

    async def log_login_failure(self, username: str, reason: str, session: AsyncSession, request: Optional[Request] = None):
        """Log failed login attempt."""
        await self.log_event(
            AuditLogCreate(
                event_type=AuditEventType.LOGIN_FAILURE,
                severity=AuditSeverity.MEDIUM,
                action="login_attempt",
                description=f"Failed login attempt for {username}: {reason}",
                username=username,
                success=False,
                error_message=reason
            ),
            session,
            request
        )

    async def log_resource_access(
        self,
        user: User,
        resource_type: str,
        resource_id: str,
        action: str,
        session: AsyncSession,
        request: Optional[Request] = None
    ):
        """Log resource access."""
        await self.log_event(
            AuditLogCreate(
                event_type=AuditEventType.PROJECT_VIEW,  # Use appropriate event type
                severity=AuditSeverity.LOW,
                action=action,
                description=f"User {user.email} {action} {resource_type} {resource_id}",
                resource_type=resource_type,
                resource_id=resource_id,
                user_id=user.id,
                username=user.email
            ),
            session,
            request,
            user
        )


# Global audit service instance
audit_service = AuditService()
