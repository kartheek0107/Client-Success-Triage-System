# scripts/load_sample_data.py
import sys
import os
import pandas as pd

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load data
df = pd.read_csv("data/sample_tickets.csv")
print("✅ Loaded dataset:")
print(df.head())
print(f"\nTotal tickets: {len(df)}")
print(f"Priorities: {df['priority'].value_counts().to_dict()}")
print(f"Categories: {df['category'].value_counts().to_dict()}")