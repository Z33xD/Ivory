import pandas as pd

# Read the CSV file
df = pd.read_csv('financial_behavior.csv')

# Print basic information
print("CSV Structure:")
print("=" * 30)
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")
print("\nColumn names:")
for col in df.columns:
    print(f"- {col}")

# Print first few rows
print("\nFirst 3 rows:")
print(df.head(3).to_string())

# Basic statistics
print("\nBasic statistics for numerical columns:")
print(df.describe()) 