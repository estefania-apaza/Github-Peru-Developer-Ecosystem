from src.extraction.github_client import GitHubClient

class UserExtractor:
    def __init__(self, client: GitHubClient):
        self.client = client

    def search_users_by_location(
        self,
        location: str,
        max_users: int = 1000
    ) -> list[dict]:
        """
        Search for users by location.

        Args:
            location: Location string (e.g., "Peru", "Lima")
            max_users: Maximum number of users to retrieve

        Returns:
            List of user dictionaries
        """
        users = []
        page = 1
        per_page = 100  # Max allowed by GitHub

        while len(users) < max_users:
            result = self.client.make_request(
                "search/users",
                params={
                    "q": f"location:{location}",
                    "per_page": per_page,
                    "page": page,
                    "sort": "followers",  # Get most influential first
                    "order": "desc"
                }
            )

            # Safety check if empty response
            if not result or not isinstance(result, dict) or not result.get("items"):
                break

            users.extend(result["items"])
            page += 1

            # GitHub search API limits to 1000 results
            if page * per_page >= 1000:
                break
            
            # Stop if we hit max needed early
            if len(users) >= max_users:
                break

        return users[:max_users]

    def get_user_details(self, username: str) -> dict:
        """Get detailed information for a specific user."""
        return self.client.make_request(f"users/{username}")

    def get_user_repos(self, username: str) -> list[dict]:
        """Get all repositories for a user."""
        repos = []
        page = 1
        max_pages = 2  # limit to 2 pages (200 repos) to speed up extraction

        while page <= max_pages:
            result = self.client.make_request(
                f"users/{username}/repos",
                params={
                    "per_page": 100,
                    "page": page,
                    "sort": "updated",
                    "type": "owner"  # Only owned repos, not forks
                }
            )

            if not result or not isinstance(result, list):
                break

            repos.extend(result)
            page += 1

        return repos
