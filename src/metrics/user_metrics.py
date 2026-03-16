from datetime import datetime
from collections import Counter
import ast

class UserMetricsCalculator:
    def __init__(self):
        self.today = datetime.now()

    def calculate_all_metrics(
        self,
        user: dict,
        repos: list[dict],
        classifications: list[dict]
    ) -> dict:
        """
        Calculate all user-level metrics.
        """
        metrics = {}
        metrics["login"] = user["login"]
        metrics["name"] = user.get("name", "")

        # Activity Metrics
        metrics["total_repos"] = len(repos)
        metrics["total_stars_received"] = sum(r.get("stargazers_count", 0) for r in repos)
        metrics["total_forks_received"] = sum(r.get("forks_count", 0) for r in repos)
        metrics["avg_stars_per_repo"] = (
            metrics["total_stars_received"] / metrics["total_repos"]
            if metrics["total_repos"] > 0 else 0
        )

        created_at_str = str(user.get("created_at", self.today.isoformat()))
        created_at = datetime.fromisoformat(created_at_str.replace("Z", ""))
        metrics["account_age_days"] = (self.today - created_at).days
        metrics["repos_per_year"] = (
            metrics["total_repos"] / (metrics["account_age_days"] / 365)
            if metrics["account_age_days"] > 0 else 0
        )

        # Influence Metrics
        metrics["followers"] = user.get("followers", 0)
        metrics["following"] = user.get("following", 0)
        metrics["follower_ratio"] = (
            metrics["followers"] / metrics["following"]
            if metrics["following"] > 0 else float(metrics["followers"])
        )
        metrics["h_index"] = self._calculate_h_index(repos)
        metrics["impact_score"] = (
            metrics["total_stars_received"] +
            (metrics["total_forks_received"] * 2) +
            metrics["followers"]
        )

        # Technical Metrics
        languages = [r.get("language") for r in repos if r.get("language")]
        lang_counts = Counter(languages)
        top_langs = [l for l, _ in lang_counts.most_common(3)]
        
        metrics["primary_language_1"] = top_langs[0] if len(top_langs) > 0 else None
        metrics["primary_language_2"] = top_langs[1] if len(top_langs) > 1 else None
        metrics["primary_language_3"] = top_langs[2] if len(top_langs) > 2 else None
        
        metrics["language_diversity"] = len(set(languages))

        industry_codes = [c.get("industry_code") for c in classifications if c.get("industry_code")]
        metrics["industries_served"] = len(set(industry_codes))
        metrics["primary_industry"] = Counter(industry_codes).most_common(1)[0][0] if industry_codes else None

        # Documentation quality
        repos_with_readme = sum(1 for r in repos if bool(r.get("readme")))
        repos_with_license = sum(1 for r in repos if r.get("license"))
        metrics["has_readme_pct"] = repos_with_readme / len(repos) if repos else 0
        metrics["has_license_pct"] = repos_with_license / len(repos) if repos else 0

        # Engagement Metrics
        metrics["total_open_issues"] = sum(r.get("open_issues_count", 0) for r in repos)

        if repos:
            # Handle potential None or missing 'pushed_at'
            valid_pushes = [r["pushed_at"].replace("Z", "") for r in repos if r.get("pushed_at")]
            if valid_pushes:
                last_push = max(datetime.fromisoformat(r) for r in valid_pushes)
                metrics["days_since_last_push"] = (self.today - last_push).days
                metrics["is_active"] = metrics["days_since_last_push"] < 90
                
                # contribution_consistency: percentage of repos pushed to in the last year
                recent_repos = sum(1 for r in valid_pushes if (self.today - datetime.fromisoformat(r)).days <= 365)
                metrics["contribution_consistency"] = recent_repos / len(repos)
            else:
                metrics["days_since_last_push"] = None
                metrics["is_active"] = False
                metrics["contribution_consistency"] = 0.0
        else:
            metrics["days_since_last_push"] = None
            metrics["is_active"] = False
            metrics["contribution_consistency"] = 0.0

        return metrics

    def _calculate_h_index(self, repos: list[dict]) -> int:
        """
        Calculate h-index based on repository stars.
        h-index = h if h repos have at least h stars each.
        """
        stars = sorted([r.get("stargazers_count", 0) for r in repos], reverse=True)
        h = 0
        for i, s in enumerate(stars):
            if s >= i + 1:
                h = i + 1
            else:
                break
        return h
