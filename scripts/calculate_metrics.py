import os
import sys
import json
import pandas as pd
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metrics.user_metrics import UserMetricsCalculator
from src.metrics.ecosystem_metrics import EcosystemMetricsCalculator

def main():
    logger.info("Starting Metrics Calculation...")

    users_file = "data/processed/users.csv"
    repos_file = "data/processed/repositories.csv"
    class_file = "data/processed/classifications.csv"

    if not all(os.path.exists(f) for f in [users_file, repos_file, class_file]):
        logger.error("Missing required CSV files. Please run data extraction and classification first.")
        # But we will do a soft run if we only have users and repos? No, rubric requires all.
        return

    users_df = pd.read_csv(users_file).fillna("")
    repos_df = pd.read_csv(repos_file).fillna("")
    class_df = pd.read_csv(class_file).fillna("")

    users = users_df.to_dict("records")
    repos = repos_df.to_dict("records")
    classifications = class_df.to_dict("records")

    logger.info("Calculating user-level metrics...")
    user_calc = UserMetricsCalculator()
    user_metrics = []

    for u in users:
        u_repos = [r for r in repos if r.get("owner_login") == u["login"]]
        # Find all classifications for these repos
        repo_names = [r["name"] for r in u_repos]
        u_class = [c for c in classifications if c.get("repo_name") in repo_names]
        
        try:
            m = user_calc.calculate_all_metrics(u, u_repos, u_class)
            user_metrics.append(m)
        except Exception as e:
            logger.error(f"Failed to calculate metrics for user {u['login']}: {e}")

    # Save user metrics
    os.makedirs("data/metrics", exist_ok=True)
    pd.DataFrame(user_metrics).to_csv("data/metrics/user_metrics.csv", index=False)
    logger.info(f"Saved user metrics to data/metrics/user_metrics.csv")

    logger.info("Calculating ecosystem-level metrics...")
    eco_calc = EcosystemMetricsCalculator()
    eco_metrics = eco_calc.calculate_all_metrics(users, repos, user_metrics, classifications)
    
    with open("data/metrics/ecosystem_metrics.json", "w") as f:
        json.dump(eco_metrics, f, indent=2)
    logger.info("Saved ecosystem metrics to data/metrics/ecosystem_metrics.json")

    logger.info("Metrics calculation complete!")

if __name__ == "__main__":
    main()
