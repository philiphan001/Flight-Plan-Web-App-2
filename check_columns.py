import pandas as pd

# Read the CSV file
df = pd.read_csv('attached_assets/Updated_Most-Recent-Cohorts-Institution.csv')

# Print total number of columns
print(f"\nTotal number of columns: {len(df.columns)}")

# Print the last 20 columns specifically
print("\nLast 20 columns:")
for col in df.columns[-20:]:
    print(col)

# Print a specific column value check
if 'us_news_ranking' in df.columns:
    print("\nUS News Ranking column found!")
else:
    print("\nUS News Ranking column NOT found. Available similar columns:")
    # Print any columns that might contain 'rank' or 'news'
    similar_cols = [col for col in df.columns if 'rank' in col.lower() or 'news' in col.lower()]
    for col in similar_cols:
        print(col)