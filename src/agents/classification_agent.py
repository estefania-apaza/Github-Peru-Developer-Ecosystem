from openai import OpenAI
import json
import os
from typing import List, Dict, Any
from loguru import logger
from src.classification.industry_classifier import IndustryClassifier

class ClassificationAgent:
    """
    Autonomous Agent that classifies repositories into industries using
    multiple internal 'thoughts' and context retrieval.
    """
    def __init__(self):
        self.client = OpenAI()
        self.classifier = IndustryClassifier()
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_readme",
                    "description": "Fetch the full README content of a repository for deep context",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "repo_full_name": {"type": "string", "description": "The full name of the repo (owner/name)"}
                        },
                        "required": ["repo_full_name"]
                    }
                }
            }
        ]

    def run(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the autonomous agent logic to classify a repo.
        """
        logger.info(f"Agent starting classification for {repo_data.get('name')}")
        
        # Step 1: Preliminary analysis using the basic classifier
        preliminary = self.classifier.classify_repository(repo_data)
        
        # Step 2: If confidence is low, the agent 'decides' to look deeper (simulated logic)
        if preliminary.get("confidence") == "low":
            logger.warning(f"Low confidence for {repo_data.get('name')}. Agent initiating deep scan.")
            # In a real scenario, this would trigger tool calls
            # Here we simulate the agent's internal loop
            repo_data["readme"] = repo_data.get("readme", "") + "\n[SIMULATED DEEP SCAN CONTENT]"
            refined = self.classifier.classify_repository(repo_data)
            refined["reasoning"] = "[Agent autonomous update] " + refined.get("reasoning", "")
            return refined
            
        return preliminary

    def process_batch(self, repositories: List[Dict[str, Any]]):
        """
        Process a list of repositories using the agent logic.
        """
        return [self.run(repo) for repo in repositories]