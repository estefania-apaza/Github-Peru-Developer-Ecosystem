from collections import Counter

class EcosystemMetricsCalculator:
    def calculate_all_metrics(self, users: list[dict], repos: list[dict], user_metrics: list[dict], classifications: list[dict]) -> dict:
        """
        Calculate aggregated metrics for the entire ecosystem.
        """
        metrics = {}
        
        metrics["total_developers"] = len(users)
        metrics["total_repositories"] = len(repos)
        metrics["total_stars"] = sum(r.get("stargazers_count", 0) for r in repos)
        metrics["avg_repos_per_user"] = (
            metrics["total_repositories"] / metrics["total_developers"] 
            if metrics["total_developers"] > 0 else 0
        )
        
        # Most popular languages overall
        languages = [r.get("language") for r in repos if r.get("language")]
        lang_counts = Counter(languages).most_common(10)
        metrics["most_popular_languages"] = [{"language": l, "count": c} for l, c in lang_counts]
        
        # Industry distribution
        industry_names = [c.get("industry_name") for c in classifications if c.get("industry_name")]
        ind_counts = Counter(industry_names).most_common()
        metrics["industry_distribution"] = [{"industry": i, "count": c} for i, c in ind_counts]
        
        # Active developers %
        active_count = sum(1 for um in user_metrics if um.get("is_active", False))
        metrics["active_developer_pct"] = (
            (active_count / metrics["total_developers"]) * 100
            if metrics["total_developers"] > 0 else 0
        )
        
        # Average account age
        total_age = sum(um.get("account_age_days", 0) for um in user_metrics)
        metrics["avg_account_age_days"] = (
            total_age / metrics["total_developers"]
            if metrics["total_developers"] > 0 else 0
        )
        
        return metrics
