"""Jira integration service."""

import base64
from typing import Any

from loguru import logger

from app.services.integrations.base_service import BaseIntegrationService


class JiraService(BaseIntegrationService):
    """Jira API integration service."""

    def _get_default_api_url(self) -> str:
        """Get the default Jira API URL."""
        # This should be configured per instance
        return self.integration.api_url or "https://your-domain.atlassian.net"

    def _get_auth_headers(self) -> dict[str, str]:
        """Get Jira authentication headers."""
        headers = {"Content-Type": "application/json"}

        credentials = self._decrypt_credentials()
        username = credentials.get("username")
        api_token = credentials.get("api_token")

        if username and api_token:
            # Basic authentication with API token
            auth_string = f"{username}:{api_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            headers["Authorization"] = f"Basic {auth_b64}"
        elif self.integration.oauth_token:
            # OAuth token authentication
            headers["Authorization"] = f"Bearer {self.integration.oauth_token}"

        return headers

    async def test_connection(self) -> dict[str, Any]:
        """Test Jira API connection."""
        try:
            response = await self._make_request("GET", "/rest/api/3/myself")
            return {
                "status": "success",
                "message": "Jira connection successful",
                "user": response.get("emailAddress"),
                "display_name": response.get("displayName")
            }
        except Exception as e:
            logger.error(f"Jira connection test failed: {e}")
            return {
                "status": "error",
                "message": f"Jira connection failed: {e!s}"
            }

    async def get_service_info(self) -> dict[str, Any]:
        """Get Jira service information."""
        try:
            server_info = await self._make_request("GET", "/rest/api/3/serverInfo")
            user_info = await self._make_request("GET", "/rest/api/3/myself")

            return {
                "service": "jira",
                "server_version": server_info.get("version"),
                "server_title": server_info.get("serverTitle"),
                "base_url": server_info.get("baseUrl"),
                "user": user_info.get("emailAddress"),
                "display_name": user_info.get("displayName"),
                "api_version": "3",
                "capabilities": [
                    "projects",
                    "issues",
                    "workflows",
                    "fields",
                    "users",
                    "webhooks"
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get Jira service info: {e}")
            return {"service": "jira", "error": str(e)}

    async def get_projects(self, expand: str = "description,lead,url") -> dict[str, Any]:
        """Get Jira projects."""
        try:
            params = {"expand": expand}
            response = await self._make_request("GET", "/rest/api/3/project", params=params)

            return {
                "projects": [
                    {
                        "id": project["id"],
                        "key": project["key"],
                        "name": project["name"],
                        "description": project.get("description"),
                        "lead": project.get("lead", {}).get("displayName"),
                        "project_type": project.get("projectTypeKey"),
                        "url": project.get("self")
                    }
                    for project in response
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return {"projects": [], "error": str(e)}

    async def get_project_issues(self, project_key: str, max_results: int = 50) -> dict[str, Any]:
        """Get issues for a specific project."""
        try:
            jql = f"project = {project_key} ORDER BY created DESC"
            params = {
                "jql": jql,
                "maxResults": max_results,
                "fields": "summary,status,priority,assignee,created,updated,issuetype"
            }

            response = await self._make_request("GET", "/rest/api/3/search", params=params)

            return {
                "issues": [
                    {
                        "id": issue["id"],
                        "key": issue["key"],
                        "summary": issue["fields"]["summary"],
                        "status": issue["fields"]["status"]["name"],
                        "priority": issue["fields"]["priority"]["name"] if issue["fields"]["priority"] else None,
                        "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else None,
                        "issue_type": issue["fields"]["issuetype"]["name"],
                        "created": issue["fields"]["created"],
                        "updated": issue["fields"]["updated"],
                        "url": f"{self._get_base_url()}/browse/{issue['key']}"
                    }
                    for issue in response["issues"]
                ],
                "total": response["total"],
                "max_results": response["maxResults"]
            }
        except Exception as e:
            logger.error(f"Failed to get project issues: {e}")
            return {"issues": [], "error": str(e)}

    async def create_issue(self, project_key: str, summary: str, description: str, issue_type: str = "Task", priority: str = "Medium") -> dict[str, Any]:
        """Create a new Jira issue."""
        try:
            # Get project and issue type details first
            project_response = await self._make_request("GET", f"/rest/api/3/project/{project_key}")

            # Get issue types for the project
            issue_types_response = await self._make_request("GET", f"/rest/api/3/project/{project_key}/statuses")

            # Find the issue type ID
            issue_type_id = None
            for it in issue_types_response:
                if it["name"].lower() == issue_type.lower():
                    issue_type_id = it["id"]
                    break

            if not issue_type_id and issue_types_response:
                # Use the first available issue type
                issue_type_id = issue_types_response[0]["id"]

            data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": description
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {"id": issue_type_id}
                }
            }

            response = await self._make_request("POST", "/rest/api/3/issue", data=data)

            return {
                "issue": {
                    "id": response["id"],
                    "key": response["key"],
                    "url": f"{self._get_base_url()}/browse/{response['key']}"
                }
            }
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            return {"error": str(e)}

    async def update_issue(self, issue_key: str, fields: dict[str, Any]) -> dict[str, Any]:
        """Update a Jira issue."""
        try:
            data = {"fields": fields}
            await self._make_request("PUT", f"/rest/api/3/issue/{issue_key}", data=data)

            return {
                "issue": {
                    "key": issue_key,
                    "updated": True,
                    "url": f"{self._get_base_url()}/browse/{issue_key}"
                }
            }
        except Exception as e:
            logger.error(f"Failed to update issue: {e}")
            return {"error": str(e)}

    async def add_comment(self, issue_key: str, comment: str) -> dict[str, Any]:
        """Add a comment to a Jira issue."""
        try:
            data = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": comment
                                }
                            ]
                        }
                    ]
                }
            }

            response = await self._make_request("POST", f"/rest/api/3/issue/{issue_key}/comment", data=data)

            return {
                "comment": {
                    "id": response["id"],
                    "author": response["author"]["displayName"],
                    "created": response["created"],
                    "updated": response["updated"]
                }
            }
        except Exception as e:
            logger.error(f"Failed to add comment: {e}")
            return {"error": str(e)}

    async def get_issue_transitions(self, issue_key: str) -> dict[str, Any]:
        """Get available transitions for an issue."""
        try:
            response = await self._make_request("GET", f"/rest/api/3/issue/{issue_key}/transitions")

            return {
                "transitions": [
                    {
                        "id": transition["id"],
                        "name": transition["name"],
                        "to_status": transition["to"]["name"]
                    }
                    for transition in response["transitions"]
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get transitions: {e}")
            return {"transitions": [], "error": str(e)}

    async def transition_issue(self, issue_key: str, transition_id: str) -> dict[str, Any]:
        """Transition an issue to a new status."""
        try:
            data = {
                "transition": {"id": transition_id}
            }

            await self._make_request("POST", f"/rest/api/3/issue/{issue_key}/transitions", data=data)

            return {
                "issue": {
                    "key": issue_key,
                    "transitioned": True,
                    "transition_id": transition_id
                }
            }
        except Exception as e:
            logger.error(f"Failed to transition issue: {e}")
            return {"error": str(e)}

    async def search_issues(self, jql: str, max_results: int = 50, start_at: int = 0) -> dict[str, Any]:
        """Search issues using JQL."""
        try:
            params = {
                "jql": jql,
                "maxResults": max_results,
                "startAt": start_at,
                "fields": "summary,status,priority,assignee,created,updated,issuetype"
            }

            response = await self._make_request("GET", "/rest/api/3/search", params=params)

            return {
                "issues": [
                    {
                        "id": issue["id"],
                        "key": issue["key"],
                        "summary": issue["fields"]["summary"],
                        "status": issue["fields"]["status"]["name"],
                        "priority": issue["fields"]["priority"]["name"] if issue["fields"]["priority"] else None,
                        "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else None,
                        "issue_type": issue["fields"]["issuetype"]["name"],
                        "created": issue["fields"]["created"],
                        "updated": issue["fields"]["updated"],
                        "url": f"{self._get_base_url()}/browse/{issue['key']}"
                    }
                    for issue in response["issues"]
                ],
                "total": response["total"],
                "start_at": response["startAt"],
                "max_results": response["maxResults"]
            }
        except Exception as e:
            logger.error(f"Failed to search issues: {e}")
            return {"issues": [], "error": str(e)}

    async def create_webhook(self, webhook_url: str, events: list[str]) -> dict[str, Any]:
        """Create a webhook for Jira events."""
        try:
            data = {
                "name": "SDLC Agents Webhook",
                "url": webhook_url,
                "events": events,
                "filters": {},
                "excludeBody": False
            }

            response = await self._make_request("POST", "/rest/webhooks/1.0/webhook", data=data)

            return {
                "webhook": {
                    "id": response.get("id"),
                    "name": response.get("name"),
                    "url": response.get("url"),
                    "events": response.get("events")
                }
            }
        except Exception as e:
            logger.error(f"Failed to create webhook: {e}")
            return {"error": str(e)}
