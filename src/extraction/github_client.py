import os
import time
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

class GitHubClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def check_rate_limit(self) -> dict:
        """Check current rate limit status."""
        response = requests.get(
            f"{self.base_url}/rate_limit",
            headers=self.headers
        )
        return response.json()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60)
    )
    def make_request(self, endpoint: str, params: dict = None) -> dict | list:
        """Make a rate-limit-aware request to GitHub API."""
        response = requests.get(
            f"{self.base_url}/{endpoint}",
            headers=self.headers,
            params=params
        )

        # Check rate limit
        if "X-RateLimit-Remaining" in response.headers:
            remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
            if remaining < 10:
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                sleep_time = max(reset_time - time.time(), 0) + 5
                print(f"Rate limit approaching. Sleeping for {sleep_time} seconds...")
                time.sleep(sleep_time)

        # Handle 404 (e.g. for readme) by returning an empty dict or similar
        if response.status_code == 404:
            return {}

        response.raise_for_status()
        
        # Some endpoints return content with no json
        if response.status_code == 204:
            return {}
            
        return response.json()
