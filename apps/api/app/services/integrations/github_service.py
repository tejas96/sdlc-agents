"""GitHub integration service."""

from typing import Any, Optional

from loguru import logger

from app.services.integrations.base_service import BaseIntegrationService


class GitHubService(BaseIntegrationService):
    """GitHub API integration service."""

    def _get_default_api_url(self) -> str:
        """Get the default GitHub API URL."""
        return "https://api.github.com"

    def _get_api_token(self) -> Optional[str]:
        """Get GitHub API token from credentials."""
        credentials = self._decrypt_credentials()
        return credentials.get("github_token")

    async def test_connection(self) -> dict[str, Any]:
        """Test GitHub API connection."""
        try:
            response = await self._make_request("GET", "/user")
            return {
                "status": "success",
                "message": "GitHub connection successful",
                "user": response.get("login"),
                "rate_limit": response.get("rate_limit", {})
            }
        except Exception as e:
            logger.error(f"GitHub connection test failed: {e}")
            return {
                "status": "error",
                "message": f"GitHub connection failed: {e!s}"
            }

    async def get_service_info(self) -> dict[str, Any]:
        """Get GitHub service information."""
        try:
            user_response = await self._make_request("GET", "/user")
            rate_limit_response = await self._make_request("GET", "/rate_limit")

            return {
                "service": "github",
                "user": user_response.get("login"),
                "user_id": user_response.get("id"),
                "plan": user_response.get("plan", {}).get("name", "free"),
                "rate_limit": rate_limit_response.get("rate", {}),
                "api_version": "v3",
                "capabilities": [
                    "repositories",
                    "pull_requests",
                    "issues",
                    "webhooks",
                    "actions",
                    "releases"
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get GitHub service info: {e}")
            return {"service": "github", "error": str(e)}

    async def get_repositories(self, org: Optional[str] = None, page: int = 1, per_page: int = 30) -> dict[str, Any]:
        """Get user or organization repositories."""
        try:
            if org:
                endpoint = f"/orgs/{org}/repos"
            else:
                endpoint = "/user/repos"

            params = {"page": page, "per_page": per_page, "sort": "updated"}
            response = await self._make_request("GET", endpoint, params=params)

            return {
                "repositories": [
                    {
                        "id": repo["id"],
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "description": repo.get("description"),
                        "language": repo.get("language"),
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "private": repo["private"],
                        "clone_url": repo["clone_url"],
                        "updated_at": repo["updated_at"]
                    }
                    for repo in response
                ],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "has_more": len(response) == per_page
                }
            }
        except Exception as e:
            logger.error(f"Failed to get repositories: {e}")
            return {"repositories": [], "error": str(e)}

    async def get_pull_requests(self, repo_owner: str, repo_name: str, state: str = "open") -> dict[str, Any]:
        """Get pull requests for a repository."""
        try:
            endpoint = f"/repos/{repo_owner}/{repo_name}/pulls"
            params = {"state": state, "sort": "updated", "direction": "desc"}
            response = await self._make_request("GET", endpoint, params=params)

            return {
                "pull_requests": [
                    {
                        "id": pr["id"],
                        "number": pr["number"],
                        "title": pr["title"],
                        "state": pr["state"],
                        "author": pr["user"]["login"],
                        "created_at": pr["created_at"],
                        "updated_at": pr["updated_at"],
                        "base_branch": pr["base"]["ref"],
                        "head_branch": pr["head"]["ref"],
                        "additions": pr.get("additions", 0),
                        "deletions": pr.get("deletions", 0),
                        "changed_files": pr.get("changed_files", 0),
                        "url": pr["html_url"]
                    }
                    for pr in response
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get pull requests: {e}")
            return {"pull_requests": [], "error": str(e)}

    async def get_pull_request_diff(self, repo_owner: str, repo_name: str, pr_number: int) -> dict[str, Any]:
        """Get pull request diff and file changes."""
        try:
            # Get PR details
            pr_endpoint = f"/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
            pr_response = await self._make_request("GET", pr_endpoint)

            # Get PR files
            files_endpoint = f"/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
            files_response = await self._make_request("GET", files_endpoint)

            return {
                "pull_request": {
                    "number": pr_response["number"],
                    "title": pr_response["title"],
                    "description": pr_response.get("body", ""),
                    "author": pr_response["user"]["login"],
                    "state": pr_response["state"]
                },
                "changes": {
                    "additions": pr_response.get("additions", 0),
                    "deletions": pr_response.get("deletions", 0),
                    "changed_files": pr_response.get("changed_files", 0)
                },
                "files": [
                    {
                        "filename": file["filename"],
                        "status": file["status"],
                        "additions": file["additions"],
                        "deletions": file["deletions"],
                        "patch": file.get("patch", ""),
                        "blob_url": file.get("blob_url")
                    }
                    for file in files_response
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get PR diff: {e}")
            return {"files": [], "error": str(e)}

    async def create_issue(self, repo_owner: str, repo_name: str, title: str, body: str, labels: Optional[list[str]] = None) -> dict[str, Any]:
        """Create a new GitHub issue."""
        try:
            endpoint = f"/repos/{repo_owner}/{repo_name}/issues"
            data = {
                "title": title,
                "body": body
            }

            if labels:
                data["labels"] = labels

            response = await self._make_request("POST", endpoint, data=data)

            return {
                "issue": {
                    "id": response["id"],
                    "number": response["number"],
                    "title": response["title"],
                    "body": response["body"],
                    "state": response["state"],
                    "url": response["html_url"],
                    "created_at": response["created_at"]
                }
            }
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            return {"error": str(e)}

    async def create_pull_request_comment(self, repo_owner: str, repo_name: str, pr_number: int, body: str) -> dict[str, Any]:
        """Add a comment to a pull request."""
        try:
            endpoint = f"/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
            data = {"body": body}

            response = await self._make_request("POST", endpoint, data=data)

            return {
                "comment": {
                    "id": response["id"],
                    "body": response["body"],
                    "author": response["user"]["login"],
                    "created_at": response["created_at"],
                    "url": response["html_url"]
                }
            }
        except Exception as e:
            logger.error(f"Failed to create PR comment: {e}")
            return {"error": str(e)}

    async def get_repository_content(self, repo_owner: str, repo_name: str, path: str = "", ref: str = "main") -> dict[str, Any]:
        """Get repository content (files and directories)."""
        try:
            endpoint = f"/repos/{repo_owner}/{repo_name}/contents/{path}"
            params = {"ref": ref}

            response = await self._make_request("GET", endpoint, params=params)

            # Handle single file vs directory
            if isinstance(response, dict):
                # Single file
                return {
                    "type": "file",
                    "name": response["name"],
                    "path": response["path"],
                    "size": response.get("size", 0),
                    "download_url": response.get("download_url"),
                    "content": response.get("content")  # Base64 encoded
                }
            else:
                # Directory listing
                return {
                    "type": "directory",
                    "path": path,
                    "contents": [
                        {
                            "name": item["name"],
                            "path": item["path"],
                            "type": item["type"],
                            "size": item.get("size", 0),
                            "download_url": item.get("download_url")
                        }
                        for item in response
                    ]
                }
        except Exception as e:
            logger.error(f"Failed to get repository content: {e}")
            return {"error": str(e)}

    async def create_webhook(self, repo_owner: str, repo_name: str, webhook_url: str, events: list[str]) -> dict[str, Any]:
        """Create a webhook for repository events."""
        try:
            endpoint = f"/repos/{repo_owner}/{repo_name}/hooks"
            data = {
                "name": "web",
                "active": True,
                "events": events,
                "config": {
                    "url": webhook_url,
                    "content_type": "json",
                    "secret": self.integration.webhook_secret or ""
                }
            }

            response = await self._make_request("POST", endpoint, data=data)

            return {
                "webhook": {
                    "id": response["id"],
                    "url": response["config"]["url"],
                    "events": response["events"],
                    "active": response["active"],
                    "created_at": response["created_at"]
                }
            }
        except Exception as e:
            logger.error(f"Failed to create webhook: {e}")
            return {"error": str(e)}
