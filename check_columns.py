import pandas as pd

# Read the CSV file
df = pd.read_csv('attached_assets/Updated_Most-Recent-Cohorts-Institution.csv')

# Print total number of columns
print(f"\nTotal number of columns: {len(df.columns)}")

# Print the last 20 columns specifically
print("\nLast 20 columns:")
for col in df.columns[-20:]:
    print(col)