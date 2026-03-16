import os
import sys
import pandas as pd
from loguru import logger
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.classification.industry_classifier import IndustryClassifier

def classify_all():
    logger.info("Starting Industry Classification...")

    repos_csv = "data/processed/repositories.csv"
    if not os.path.exists(repos_csv):
        logger.error(f"Cannot find {repos_csv}. Has data extraction finished?")
        return

    logger.info(f"Loading repositories from {repos_csv}...")
    repos_df = pd.read_csv(repos_csv)

    # Convert dataframe back to a list of dicts that the classifier expects
    # Ensure NaN values in string fields (like description or readme) become empty strings
    repos_df = repos_df.fillna("")
    repositories = repos_df.to_dict(orient="records")

    logger.info(f"Loaded {len(repositories)} repositories. Preparing classification...")

    classifier = IndustryClassifier()
    
    # Actually classifying 1000 repositories sequentially takes a long time with OpenAI APIs.
    # To speed up, we will just classify them using the batch method.
    classified_results = []
    
    # We will iterate with tqdm for progress visibility
    for i in tqdm(range(0, len(repositories), 10)):
        batch = repositories[i:i+10]
        try:
            results = classifier.batch_classify(batch, batch_size=10)
            classified_results.extend(results)
        except Exception as e:
            logger.error(f"Error classifying batch starting at index {i}: {e}")

    logger.info("Classification completed. Saving to CSV...")
    
    classifications_df = pd.DataFrame(classified_results)
    out_path = "data/processed/classifications.csv"
    classifications_df.to_csv(out_path, index=False, encoding='utf-8')
    logger.info(f"Saved {len(classifications_df)} classifications to {out_path}.")

if __name__ == "__main__":
    classify_all()
