"""
utils.py — 共用工具：wave 定义、配色、聚合函数

所有页面通过 import utils 调用。改动一处，全站生效。
"""

import pandas as pd
import streamlit as st
from collections import Counter


# ============================================================
# Wave 定义
# ============================================================

WAVE_NAMES = ['AI', 'Enterprise SaaS', 'Fintech', 'Developer Tools']
PAST_WAVES = ['Enterprise SaaS', 'Fintech', 'Developer Tools']


def wave_col(wave_name):
    """'Enterprise SaaS' → 'is_Enterprise_SaaS'"""
    return f'is_{wave_name.replace(" ", "_")}'


# ============================================================
# 配色
# ============================================================

COLORS = {
    'AI':              '#D85A30',
    'Enterprise SaaS': '#5B7B8C',
    'Fintech':         '#A8A8A8',
    'Developer Tools': '#C8B89C',
    'background':      '#FAFAF8',
    'text':            '#1A1A1A',
    'text_secondary':  '#666666',
    'highlight':       '#D85A30',
}


# ============================================================
# 数据加载
# ============================================================

@st.cache_data
def load_data():
    """加载清洗后的数据。所有页面共用。"""
    return pd.read_parquet('data/companies_clean.parquet')


# ============================================================
# 聚合函数 - Wave 分析
# ============================================================

def compute_wave_share_yearly(df):
    """每年每个 wave 占比（%）。

    Returns:
        DataFrame: index=year, columns=4 个 wave, values=占比%

    Note:
        行加和可能 >100%，因为允许公司归属多个 wave。
    """
    yearly_total = df.groupby('year').size()
    result = pd.DataFrame()
    for wave in WAVE_NAMES:
        col = wave_col(wave)
        wave_count = df[df[col]].groupby('year').size()
        result[wave] = (wave_count / yearly_total * 100).fillna(0)
    return result.round(1)


def compute_wave_peaks(df):
    """每个 wave 的 peak 占比和 peak 年份。

    Returns:
        DataFrame: index=wave, columns=['peak_pct', 'peak_year', 'total_companies']
    """
    yearly = compute_wave_share_yearly(df)
    return pd.DataFrame({
        'peak_pct': yearly.max(),
        'peak_year': yearly.idxmax(),
        'total_companies': [df[wave_col(w)].sum() for w in WAVE_NAMES],
    })


def compute_ai_penetration(df):
    """AI 在每个 past wave 中的渗透率（%），按年。

    Returns:
        DataFrame: index=year, columns=['AI in Enterprise SaaS', ...]
    """
    result = pd.DataFrame()
    for past_wave in PAST_WAVES:
        col = wave_col(past_wave)
        sub = df[df[col]]
        penetration = sub.groupby('year')['is_AI'].mean() * 100
        result[f'AI in {past_wave}'] = penetration
    return result.round(1)


def compute_overlap_matrix(df):
    """两两交叉公司数矩阵。"""
    matrix = pd.DataFrame(index=WAVE_NAMES, columns=WAVE_NAMES, dtype=int)
    for w1 in WAVE_NAMES:
        for w2 in WAVE_NAMES:
            matrix.loc[w1, w2] = (df[wave_col(w1)] & df[wave_col(w2)]).sum()
    return matrix


# ============================================================
# 聚合函数 - 共现网络
# ============================================================

def compute_cooccurrence(df, year=None, top_n=30, min_count=5):
    """计算 tag 共现网络数据。

    Args:
        df: 主数据
        year: 指定年份；None 用全部
        top_n: 取共现频次最高的前 N 个 tag 作为节点
        min_count: 共现次数 < min_count 的边丢弃

    Returns:
        edges: list of dicts {'tag1', 'tag2', 'count'}
        nodes: dict, key=tag, value={'n_companies', 'ai_pct'}
    """
    df_use = df[df['year'] == year] if year is not None else df

    tag_counts = df_use.explode('tag_list')['tag_list'].value_counts()
    top_tags = set(tag_counts.head(top_n).index.tolist())

    pair_counter = Counter()
    for tags in df_use['tag_list']:
        if not isinstance(tags, list):
            continue
        relevant = [t for t in tags if t in top_tags]
        for i, t1 in enumerate(relevant):
            for t2 in relevant[i+1:]:
                pair = tuple(sorted([t1, t2]))
                pair_counter[pair] += 1

    edges = [
        {'tag1': p[0], 'tag2': p[1], 'count': c}
        for p, c in pair_counter.items() if c >= min_count
    ]

    nodes = {}
    for tag in top_tags:
        mask = df_use['tag_list'].apply(
            lambda x: tag in x if isinstance(x, list) else False
        )
        sub = df_use[mask]
        n = len(sub)
        ai_pct = sub['is_AI'].mean() * 100 if n > 0 else 0
        nodes[tag] = {
            'n_companies': n,
            'ai_pct': round(ai_pct, 1),
        }

    return edges, nodes


# ============================================================
# 聚合函数 - 地理
# ============================================================

def compute_region_share(df, exclude_unknown=True):
    """每个 region 在 AI 公司 vs 非 AI 公司中的占比，按年。"""
    df_use = df[df['region'] != 'Unknown'] if exclude_unknown else df

    grouped = df_use.groupby(['year', 'is_AI', 'region']).size().reset_index(name='n')
    totals = df_use.groupby(['year', 'is_AI']).size().reset_index(name='total')
    merged = grouped.merge(totals, on=['year', 'is_AI'])
    merged['pct'] = (merged['n'] / merged['total'] * 100).round(1)
    return merged


def compute_bay_area_concentration(df, exclude_unknown=True):
    """Bay Area 集中度时间序列（AI vs 非 AI）。

    Returns:
        DataFrame: index=year, columns=['AI in Bay Area %', 'Non-AI in Bay Area %', 'Gap']
    """
    df_use = df[df['region'] != 'Unknown'] if exclude_unknown else df
    df_use = df_use.assign(in_bay=lambda x: x['region'] == 'Bay Area')

    result = (
        df_use.groupby(['year', 'is_AI'])['in_bay']
        .mean()
        .unstack() * 100
    ).round(1)
    result.columns = ['Non-AI in Bay Area %', 'AI in Bay Area %']
    result['Gap'] = (result['AI in Bay Area %'] - result['Non-AI in Bay Area %']).round(1)
    return result[['AI in Bay Area %', 'Non-AI in Bay Area %', 'Gap']]


def compute_city_stats(df, year=None, top_n=20):
    """每个城市的公司数 + AI 占比（地图用）。

    Returns:
        DataFrame: columns=['City', 'Country', 'n_companies', 'ai_pct']
    """
    df_use = df[df['year'] == year] if year is not None else df
    df_use = df_use.dropna(subset=['City'])

    grouped = df_use.groupby(['City', 'Country']).agg(
        n_companies=('Company ID', 'count'),
        ai_pct=('is_AI', lambda x: x.mean() * 100),
    ).reset_index()

    grouped['ai_pct'] = grouped['ai_pct'].round(1)
    grouped = grouped.sort_values('n_companies', ascending=False).head(top_n)
    return grouped.reset_index(drop=True)


# ============================================================
# Streamlit 通用样式
# ============================================================

def apply_global_style():
    """统一全站样式。app.py 顶部调用一次。"""
    st.markdown("""
        <style>
        .main-title {
            font-size: 38px;
            font-weight: 600;
            margin-bottom: 4px;
            color: #1A1A1A;
        }
        .subtitle {
            font-size: 17px;
            color: #666;
            margin-bottom: 28px;
            font-weight: 400;
        }
        .finding-box {
            background: #FAFAF8;
            border-left: 4px solid #D85A30;
            padding: 18px 24px;
            margin: 28px 0;
            border-radius: 4px;
            font-size: 15px;
            line-height: 1.6;
        }
        .finding-box strong {
            color: #D85A30;
            font-weight: 600;
        }
        .question-block {
            font-size: 18px;
            color: #1A1A1A;
            font-weight: 500;
            margin: 24px 0;
            padding: 16px 0;
            border-top: 1px solid #E0E0E0;
            border-bottom: 1px solid #E0E0E0;
        }
        section[data-testid="stSidebar"] {
            background: #FAFAF8;
        }
        </style>
    """, unsafe_allow_html=True)


def finding_box(text):
    """渲染一个 finding 提示框。"""
    st.markdown(f'<div class="finding-box">{text}</div>', unsafe_allow_html=True)
