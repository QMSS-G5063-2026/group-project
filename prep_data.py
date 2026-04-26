"""
prep_data.py
数据清洗脚本：原始 CSV → companies_clean.parquet

用法：python prep_data.py
输入：data/yc-companies.csv
输出：data/companies_clean.parquet
"""

import pandas as pd
from pathlib import Path


# ============================================================
# 配置
# ============================================================

INPUT_PATH = Path("data/yc-companies.csv")
OUTPUT_PATH = Path("data/companies_clean.parquet")
MIN_BATCH_SIZE = 100  # 排除年度公司数 < 100 的年份


# ---------- Wave 定义 ----------

AI_TAGS = {
    'ai', 'artificial-intelligence', 'generative-ai', 'machine-learning',
    'ai-assistant', 'computer-vision', 'aiops', 'deep-learning',
    'ai-enhanced-learning', 'conversational-ai', 'ai-powered-drug-discovery',
    'nlp', 'chatbot', 'chatbots', 'speech-recognition', 'recommendation-system',
}

PAST_WAVES = {
    'Enterprise_SaaS': {'saas', 'b2b'},
    'Fintech':         {'fintech'},
    'Developer_Tools': {'developer-tools'},
}


# ---------- 地理分类 ----------

BAY_AREA_CITIES = {
    'San Francisco', 'Mountain View', 'Palo Alto', 'Berkeley',
    'Oakland', 'San Jose', 'Redwood City', 'San Mateo',
    'Sunnyvale', 'Menlo Park', 'Santa Clara', 'Cupertino',
    'Burlingame', 'Foster City', 'South San Francisco',
    'Daly City', 'San Bruno', 'Belmont', 'Hayward',
    'Fremont', 'Emeryville', 'Brisbane', 'Alameda',
}

NYC_CITIES = {'New York', 'Brooklyn', 'Manhattan', 'Queens'}


# ---------- 保留的字段 ----------

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
# 工具函数
# ============================================================

def parse_batch(batch):
    """Batch 格式固定为 'Summer 2023' / 'Winter 2024'，按空格切分。"""
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
# 主流程
# ============================================================

def main():
    print(f"→ 读取 {INPUT_PATH}...")
    df = pd.read_csv(INPUT_PATH).dropna(how='all').copy()
    print(f"  原始行数: {len(df)}")

    print("→ 保留必要字段...")
    keep = [c for c in COLS_TO_KEEP if c in df.columns]
    df = df[keep].copy()

    print("→ 解析 batch...")
    parsed = df['Batch'].apply(parse_batch)
    df['season'] = parsed.apply(lambda x: x[0])
    df['year'] = parsed.apply(lambda x: x[1])
    print(f"  year 解析成功率: {df['year'].notna().mean():.1%}")

    print("→ 切分 tags...")
    df['Tags'] = df['Tags'].fillna('').str.lower()
    df['tag_list'] = df['Tags'].apply(parse_tags)
    df['n_tags'] = df['tag_list'].apply(len)

    print("→ 标记 wave 归属...")
    df['is_AI'] = df['tag_list'].apply(
        lambda tags: any(t in AI_TAGS for t in tags)
    )
    for wave_name, wave_tags in PAST_WAVES.items():
        col = f'is_{wave_name}'
        df[col] = df['tag_list'].apply(
            lambda tags: any(t in wave_tags for t in tags)
        )

    wave_cols = ['is_AI'] + [f'is_{w}' for w in PAST_WAVES]
    df['n_waves'] = df[wave_cols].sum(axis=1)

    print("→ 分类 region...")
    df['region'] = df.apply(
        lambda row: classify_region(row['City'], row['Country']),
        axis=1,
    )

    print("→ 过滤小样本年份...")
    yearly = df.groupby('year').size()
    valid_years = yearly[yearly >= MIN_BATCH_SIZE].index
    df = df[df['year'].isin(valid_years)].copy()
    print(f"  保留年份: {sorted(valid_years.tolist())}")
    print(f"  保留行数: {len(df)}")

    print(f"→ 保存 {OUTPUT_PATH}...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)

    # ===== 验证摘要 =====
    print("\n" + "=" * 60)
    print("✓ 清洗完成")
    print("=" * 60)
    print(f"\n总公司数: {len(df)}")
    print(f"年份范围: {df['year'].min()}-{df['year'].max()}（{df['year'].nunique()} 年）")

    print(f"\nWave 分布:")
    for c in wave_cols:
        print(f"  {c:25s}: {df[c].sum():>5d}")

    print(f"\n归属 wave 数分布:")
    print(df['n_waves'].value_counts().sort_index().to_string())

    print(f"\nRegion 分布:")
    print(df['region'].value_counts().to_string())

    print(f"\nAI 渗透率（按 region）:")
    print(df.groupby('region')['is_AI'].mean().round(3).to_string())

    print(f"\nAI 渗透率（按 region × 年份，2018-2025）:")
    pivot = (
        df[df['year'] >= 2018]
        .groupby(['year', 'region'])['is_AI']
        .mean()
        .unstack()
        .round(3)
    )
    print(pivot.to_string())

    print(f"\n字段一览（{len(df.columns)} 列）:")
    print(df.dtypes.to_string())


if __name__ == '__main__':
    main()
