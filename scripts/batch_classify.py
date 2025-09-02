# scripts/batch_classify.py
import pandas as pd
import requests
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://localhost:8000/classify"
API_KEY = "your-secret-api-key-here-keep-it-safe"  # Must match .env
INPUT_FILE = "data.csv"
OUTPUT_FILE = "classified_results.csv"

# Add headers
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}


def classify_ticket(subject: str, description: str) -> dict:
    """Call the FastAPI /classify endpoint."""
    payload = {
        "subject": subject,
        "description": description
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API Error {response.status_code}: {response.text}")
            return {
                "priority": "ERROR",
                "priority_confidence": 0.0,
                "category": "ERROR",
                "category_confidence": 0.0,
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return {
            "priority": "ERROR",
            "priority_confidence": 0.0,
            "category": "ERROR",
            "category_confidence": 0.0,
            "error": str(e)
        }


def main():
    # Check if API is reachable
    try:
        health = requests.get("http://localhost:8000/health")
        if health.status_code != 200:
            logger.error("API is not healthy")
            return
    except:
        logger.error("❌ Could not connect to FastAPI. Is it running?")
        return

    # Load data
    if not Path(INPUT_FILE).exists():
        logger.error(f"{INPUT_FILE} not found in project root")
        return

    df = pd.read_csv(INPUT_FILE)
    logger.info(f"Loaded {len(df)} tickets from {INPUT_FILE}")

    # Add new columns for predictions
    df["predicted_priority"] = ""
    df["predicted_priority_confidence"] = 0.0
    df["predicted_category"] = ""
    df["predicted_category_confidence"] = 0.0
    df["error"] = ""

    # Classify each ticket
    for idx, row in df.head(25).iterrows():
        logger.info(f"[{idx+1}/{len(df)}] Classifying: {row['subject'][:50]}...")

        result = classify_ticket(row["subject"], row["description"])

        df.at[idx, "predicted_priority"] = result.get("priority", "ERROR")
        df.at[idx, "predicted_priority_confidence"] = result.get("priority_confidence", 0.0)
        df.at[idx, "predicted_category"] = result.get("category", "ERROR")
        df.at[idx, "predicted_category_confidence"] = result.get("category_confidence", 0.0)
        df.at[idx, "error"] = result.get("error", "")

        # Rate limiting: 10/min → wait 6 seconds between calls
        time.sleep(0.6)

    # Save results
    df.to_csv(OUTPUT_FILE, index=False)
    logger.info(f"✅ Classification complete! Results saved to {OUTPUT_FILE}")

    # Print summary
    print("\n📊 Prediction Summary:")
    print(f"Priority: \n{df['predicted_priority'].value_counts().to_dict()}")
    print(f"Category: \n{df['predicted_category'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()