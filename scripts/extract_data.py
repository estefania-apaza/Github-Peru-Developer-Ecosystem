import sys
import os
import json
import pandas as pd
from loguru import logger
from tqdm import tqdm
import concurrent.futures

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extraction.github_client import GitHubClient
from src.extraction.user_extractor import UserExtractor
from src.extraction.repo_extractor import RepoExtractor

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_all():
    logger.info("Starting Optimized GitHub Peru Analytics data extraction...")
    
    client = GitHubClient()
    user_extractor = UserExtractor(client)
    repo_extractor = RepoExtractor(client)
    
    rl = client.check_rate_limit()
    logger.info(f"Initial Rate Limit: {rl['resources']['core']['remaining']}/{rl['resources']['core']['limit']}")

    os.makedirs("data/raw/users", exist_ok=True)
    os.makedirs("data/raw/repos", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    # 1. Search for users in Peru
    existing_user_files = [f for f in os.listdir("data/raw/users") if f.endswith('.json')]
    detailed_users = []
    
    if len(existing_user_files) < 300:
        logger.info("Searching for users in Peru...")
        peru_users = user_extractor.search_users_by_location("Peru", max_users=300)
        lima_users = user_extractor.search_users_by_location("Lima", max_users=300)
        all_users_dict = {u['login']: u for u in peru_users + lima_users}
        all_users = list(all_users_dict.values())
        logger.info(f"Found {len(all_users)} unique users.")

        logger.info("Fetching detailed user profiles concurrently...")
        def fetch_user(u):
            login = u["login"]
            fpath = f"data/raw/users/{login}.json"
            if os.path.exists(fpath):
                return load_json(fpath)
            try:
                details = user_extractor.get_user_details(login)
                if details:
                    save_json(details, fpath)
                    return details
            except Exception as e:
                logger.error(f"Error fetching user {login}: {e}")
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(tqdm(executor.map(fetch_user, all_users), total=len(all_users)))
            detailed_users = [r for r in results if r]
    else:
        logger.info(f"Loading {len(existing_user_files)} existing users from raw data...")
        for f in existing_user_files:
            detailed_users.append(load_json(os.path.join("data/raw/users", f)))

    # 2. Extract repositories
    all_repos = []
    
    logger.info("Extracting repositories for users concurrently...")
    def fetch_repos(u):
        login = u["login"]
        user_repos = []
        try:
            repos = user_extractor.get_user_repos(login)
            for r in repos:
                fpath = f"data/raw/repos/{r['id']}.json"
                if not os.path.exists(fpath):
                    save_json(r, fpath)
                user_repos.append(r)
        except Exception as e:
            logger.error(f"Error fetching repos for {login}: {e}")
        return user_repos

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(tqdm(executor.map(fetch_repos, detailed_users), total=len(detailed_users)))
        for r_list in results:
            all_repos.extend(r_list)
            
    logger.info(f"Collected total of {len(all_repos)} repositories initially.")
    
    # 3. Filter top repositories by stars
    all_repos.sort(key=lambda x: x.get("stargazers_count", 0), reverse=True)
    top_repos = all_repos[:1200]
    logger.info(f"Selected Top {len(top_repos)} repositories by stars for detailed extraction.")

    # 4. Enhance selected repos with README and Languages
    logger.info("Fetching READMEs and Languages concurrently...")
    
    def enhance_repo(r):
        owner = r["owner"]["login"] if isinstance(r.get("owner"), dict) else r.get("owner_login", "")
        name = r["name"]
        try:
            readme = repo_extractor.get_repo_readme(owner, name)
            r["readme"] = readme
            r["has_readme"] = bool(readme)
            
            languages = repo_extractor.get_repo_languages(owner, name)
            r["languages_dict"] = languages
        except Exception as e:
            logger.error(f"Error enhancing repo {owner}/{name}: {e}")
            r["readme"] = ""
            r["has_readme"] = False
            r["languages_dict"] = {}
        return r

    enhanced_repos = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        enhanced_repos = list(tqdm(executor.map(enhance_repo, top_repos), total=len(top_repos)))

    # 5. Save final CSV files
    logger.info("Converting data and saving to CSV...")
    
    # Save Users CSV
    users_df = pd.DataFrame(detailed_users)
    users_csv_path = "data/processed/users.csv"
    users_df.to_csv(users_csv_path, index=False, encoding='utf-8')
    logger.info(f"Saved {len(detailed_users)} users to {users_csv_path}")

    # Save Repos CSV
    repos_df = pd.DataFrame(enhanced_repos)
    if "owner" in repos_df.columns:
        repos_df["owner_login"] = repos_df["owner"].apply(lambda x: x["login"] if isinstance(x, dict) else x)
    
    repos_csv_path = "data/processed/repositories.csv"
    repos_df.to_csv(repos_csv_path, index=False, encoding='utf-8')
    logger.info(f"Saved {len(enhanced_repos)} repositories to {repos_csv_path}")

    logger.info("Data extraction completed successfully!")

if __name__ == "__main__":
    extract_all()
