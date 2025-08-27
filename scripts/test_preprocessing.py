import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp_pipeline.preprocessing.cleaner import preprocess_text

sample = "Hi, my API is down! Contact admin@test.com or visit https://example.com for help. Call me at 123-456-7890."
result = preprocess_text(sample)
print(f"Original: {sample}")
print(f"Processed: {result}")