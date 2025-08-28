# test_models.py
from transformers import pipeline
import os

# Define paths
priority_model_path = "models/artifacts/bert-priority-model"
category_model_path = "models/artifacts/bert-category-model"

# Check if paths exist
if not os.path.exists(priority_model_path):
    raise FileNotFoundError(f"Priority model not found at {priority_model_path}")

if not os.path.exists(category_model_path):
    raise FileNotFoundError(f"Category model not found at {category_model_path}")

print("✅ Model folders found. Loading pipelines...")

# Load models
try:
    priority_classifier = pipeline(
        "text-classification",
        model=priority_model_path,
        tokenizer=priority_model_path,
        return_all_scores=False
    )

    category_classifier = pipeline(
        "text-classification",
        model=category_model_path,
        tokenizer=category_model_path,
        return_all_scores=False
    )
    print("✅ Models loaded successfully!\n")

except Exception as e:
    print(f"❌ Error loading models: {e}")
    raise

# Test ticket
test_ticket = """
Dashboard not loading The reporting module is showing a blank white screen 
No data is loading This is impacting all our users since yesterday at 4 PM UTC
"""

print("🧪 Testing on real ticket:")
print("📝", test_ticket.strip())

# Predict
try:
    priority_result = priority_classifier(test_ticket)[0]
    category_result = category_classifier(test_ticket)[0]

    print("\n🎉 SUCCESS! Predictions:")
    print(f"   Priority:     {priority_result['label']} (confidence: {priority_result['score']:.4f})")
    print(f"   Category:     {category_result['label']} (confidence: {category_result['score']:.4f})")
except Exception as e:
    print(f"❌ Error during prediction: {e}")