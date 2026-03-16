from openai import OpenAI
import json
import os
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

class IndustryClassifier:
    def __init__(self):
        self.client = OpenAI()
        self.industries = {
            "A": "Agriculture, forestry and fishing",
            "B": "Mining and quarrying",
            "C": "Manufacturing",
            "D": "Electricity, gas, steam supply",
            "E": "Water supply; sewerage",
            "F": "Construction",
            "G": "Wholesale and retail trade",
            "H": "Transportation and storage",
            "I": "Accommodation and food services",
            "J": "Information and communication",
            "K": "Financial and insurance activities",
            "L": "Real estate activities",
            "M": "Professional, scientific activities",
            "N": "Administrative and support activities",
            "O": "Public administration and defense",
            "P": "Education",
            "Q": "Human health and social work",
            "R": "Arts, entertainment and recreation",
            "S": "Other service activities",
            "T": "Activities of households",
            "U": "Extraterritorial organizations"
        }
        self.system_prompt = "You are an expert at classifying software projects by industry. Always respond with valid JSON."

    def _build_prompt(self, repo_data: dict) -> str:
        name = repo_data.get('name', '')
        description = repo_data.get('description', '')
        language = repo_data.get('language', '')
        topics = repo_data.get('topics', [])
        readme = repo_data.get('readme', '')

        return f"""Analyze this GitHub repository and classify it into ONE of the following industry categories based on its potential application or the industry it serves.

REPOSITORY INFORMATION:
- Name: {name}
- Description: {description or 'No description'}
- Primary Language: {language or 'Not specified'}
- Topics: {', '.join(topics) if topics else 'None'}
- README (first 2000 chars): {(readme or '')[:2000] if readme else 'No README'}

INDUSTRY CATEGORIES:
{json.dumps(self.industries, indent=2)}

INSTRUCTIONS:
1. Analyze the repository's purpose, functionality, and potential use cases
2. Consider what industry would most benefit from or use this software
3. If it's a general-purpose tool, classify based on the most likely industry application
4. If truly generic, use "J" (Information and communication)

Respond in JSON format:
{{
    "industry_code": "X",
    "industry_name": "Full industry name",
    "confidence": "high|medium|low",
    "reasoning": "Brief explanation"
}}
"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=20))
    def classify_repository(self, repo_data: dict) -> dict:
        prompt = self._build_prompt(repo_data)
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" },
                temperature=0.1,
            )
            result_str = response.choices[0].message.content
            return json.loads(result_str)
        except Exception as e:
            logger.error(f"Error classifying repository {repo_data.get('name')}: {e}")
            return {
                "industry_code": "J",
                "industry_name": "Information and communication",
                "confidence": "low",
                "reasoning": f"Classification failed due to error: {e}"
            }

    def batch_classify(self, repositories: list[dict], batch_size: int = 10) -> list[dict]:
        import concurrent.futures
        from tqdm import tqdm
        
        results = []
        def process_repo(repo):
            try:
                classification = self.classify_repository(repo)
                return {
                    "repo_id": repo["id"],
                    "repo_name": repo["name"],
                    "owner": repo.get("owner_login", ""),
                    "industry_code": classification.get("industry_code", "J"),
                    "industry_name": classification.get("industry_name", "Information and communication"),
                    "confidence": classification.get("confidence", "low"),
                    "reasoning": classification.get("reasoning", "")
                }
            except Exception as e:
                logger.error(f"Failed repo {repo['name']}: {e}")
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for r in tqdm(executor.map(process_repo, repositories), total=len(repositories), desc="Classifying Repos"):
                if r:
                    results.append(r)
        
        return results
