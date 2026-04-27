"""
prep_data.py -- Data cleaning pipeline: raw CSV -> companies_clean.parquet

Usage:  python prep_data.py
Input:  data/yc-companies.csv   (raw Hugging Face dataset)
Output: data/companies_clean.parquet
"""

import pandas as pd
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

INPUT_PATH = Path("data/yc-companies.csv")
OUTPUT_PATH = Path("data/companies_clean.parquet")
MIN_BATCH_SIZE = 100  # drop years with fewer than this many companies


# -- Wave tag definitions ----------------------------------------------------

AI_TAGS = {
    'ai', 'artificial-intelligence', 'generative-ai', 'machine-learning',
    'ai-assistant', 'computer-vision', 'aiops', 'deep-learning',
    'ai-enhanced-learning', 'conversational-ai', 'ai-powered-drug-discovery',
    'nlp', 'chatbot', 'chatbots', 'speech-recognition', 'recommendation-system',
}

# Reference trends — column suffix must match utils.trend_col() convention:
# 'Enterprise SaaS' -> 'is_Enterprise_SaaS', etc.
REFERENCE_TREND_TAGS = {
    'Enterprise_SaaS': {'saas', 'b2b'},
    'Fintech':         {'fintech'},
    'Developer_Tools': {'developer-tools'},
}


# -- Geographic classification -----------------------------------------------

BAY_AREA_CITIES = {
    'San Francisco', 'Mountain View', 'Palo Alto', 'Berkeley',
    'Oakland', 'San Jose', 'Redwood City', 'San Mateo',
    'Sunnyvale', 'Menlo Park', 'Santa Clara', 'Cupertino',
    'Burlingame', 'Foster City', 'South San Francisco',
    'Daly City', 'San Bruno', 'Belmont', 'Hayward',
    'Fremont', 'Emeryville', 'Brisbane', 'Alameda',
}

NYC_CITIES = {'New York', 'Brooklyn', 'Manhattan', 'Queens'}


# -- Columns to retain -------------------------------------------------------

COLS_TO_KEEP = [
    'Company ID', 'Company Name', 'Slug',
    'One Liner', 'Long Description',
    'Website', 'Location', 'City', 'Country', 'Regions',
    'Team Size', 'Year Founded',
    'Batch',
    'Industry', 'Subindustry', 'Industries', 'Tags',
    'Founders Count',
]


# ============================================================
# Helper functions
# ============================================================

def parse_batch(batch):
    """Parse 'Summer 2023' / 'Winter 2024' -> (season, year)."""
    if pd.isna(batch):
        return None, None
    parts = str(batch).split(' ')
    if len(parts) != 2:
        return None, None
    season, year = parts
    try:
        return season, int(year)
    except ValueError:
        return None, None


def parse_tags(tags_str):
    if pd.isna(tags_str):
        return []
    return [t.strip().lower() for t in str(tags_str).split(';') if t.strip()]


def classify_region(city, country):
    if pd.isna(country):
        return 'Unknown'
    if country != 'US':
        return 'International'
    if pd.notna(city) and city in BAY_AREA_CITIES:
        return 'Bay Area'
    if pd.notna(city) and city in NYC_CITIES:
        return 'NYC'
    return 'Other US'


# ============================================================
# Main pipeline
# ============================================================

def main():
    print(f"Reading {INPUT_PATH}...")
    df = pd.read_csv(INPUT_PATH).dropna(how='all').copy()
    print(f"  Raw rows: {len(df)}")

    print("Selecting columns...")
    keep = [c for c in COLS_TO_KEEP if c in df.columns]
    df = df[keep].copy()

    print("Parsing batch...")
    parsed = df['Batch'].apply(parse_batch)
    df['season'] = parsed.apply(lambda x: x[0])
    df['year'] = parsed.apply(lambda x: x[1])
    print(f"  Year parse success rate: {df['year'].notna().mean():.1%}")

    print("Parsing tags...")
    df['Tags'] = df['Tags'].fillna('').str.lower()
    df['tag_list'] = df['Tags'].apply(parse_tags)
    df['n_tags'] = df['tag_list'].apply(len)

    print("Labeling trend membership...")
    df['is_AI'] = df['tag_list'].apply(
        lambda tags: any(t in AI_TAGS for t in tags)
    )
    for trend_name, trend_tags in REFERENCE_TREND_TAGS.items():
        col = f'is_{trend_name}'
        df[col] = df['tag_list'].apply(
            lambda tags: any(t in trend_tags for t in tags)
        )

    trend_cols = ['is_AI'] + [f'is_{t}' for t in REFERENCE_TREND_TAGS]
    df['n_trends'] = df[trend_cols].sum(axis=1)

    print("Classifying regions...")
    df['region'] = df.apply(
        lambda row: classify_region(row['City'], row['Country']),
        axis=1,
    )

    print("Filtering small-batch years...")
    yearly = df.groupby('year').size()
    valid_years = yearly[yearly >= MIN_BATCH_SIZE].index
    df = df[df['year'].isin(valid_years)].copy()
    print(f"  Years retained: {sorted(valid_years.tolist())}")
    print(f"  Rows retained: {len(df)}")

    print(f"Saving to {OUTPUT_PATH}...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)

    # Summary
    print("\n" + "=" * 60)
    print("Done.")
    print("=" * 60)
    print(f"\nTotal companies: {len(df)}")
    print(f"Year range: {df['year'].min()}-{df['year'].max()} ({df['year'].nunique()} years)")

    print("\nTrend distribution:")
    for c in trend_cols:
        print(f"  {c:25s}: {df[c].sum():>5d}")

    print("\nTrend membership count distribution:")
    print(df['n_trends'].value_counts().sort_index().to_string())

    print("\nRegion distribution:")
    print(df['region'].value_counts().to_string())

    print("\nAI penetration rate by region:")
    print(df.groupby('region')['is_AI'].mean().round(3).to_string())

    print("\nAI penetration rate by region x year (2018-2025):")
    pivot = (
        df[df['year'] >= 2018]
        .groupby(['year', 'region'])['is_AI']
        .mean()
        .unstack()
        .round(3)
    )
    print(pivot.to_string())

    print(f"\nColumn overview ({len(df.columns)} columns):")
    print(df.dtypes.to_string())


if __name__ == '__main__':
    main()
