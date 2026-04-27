"""
utils.py -- Shared utilities: trend definitions, colors, aggregation functions.

All pages import this module. Changes here propagate everywhere.
"""

import pandas as pd
import streamlit as st


# ============================================================
# Trend definitions
# ============================================================

TREND_NAMES      = ['AI', 'Enterprise SaaS', 'Fintech', 'Developer Tools']
REFERENCE_TRENDS = ['Enterprise SaaS', 'Fintech', 'Developer Tools']


def trend_col(trend_name):
    """'Enterprise SaaS' -> 'is_Enterprise_SaaS'"""
    return f'is_{trend_name.replace(" ", "_")}'


# ============================================================
# Color palette  (colorblind-safe, verified via colorbrewer2.org)
# ============================================================

COLORS = {
    'AI':              '#E6550D',  # orange -- primary signal
    'Enterprise SaaS': '#3182BD',  # blue
    'Fintech':         '#31A354',  # green
    'Developer Tools': '#969696',  # gray
    'ref_line':        '#CCCCCC',  # unified gray for reference lines in overview chart
    'background':      '#FFFFFF',
    'text':            '#111111',
    'text_secondary':  '#555555',
    'highlight':       '#E6550D',
}


# ============================================================
# Data loading
# ============================================================

@st.cache_data
def load_data():
    """Load cleaned parquet. Cached so all pages share one copy."""
    return pd.read_parquet('data/companies_clean.parquet')


# ============================================================
# Aggregation -- trend share
# ============================================================

def compute_trend_share_yearly(df):
    """Percentage of each YC batch belonging to each trend, by year.

    Returns:
        DataFrame: index=year, columns=TREND_NAMES, values=pct of batch

    Note:
        Rows can sum to >100% because a company can belong to multiple trends.
    """
    yearly_total = df.groupby('year').size()
    result = pd.DataFrame()
    for trend in TREND_NAMES:
        col = trend_col(trend)
        count = df[df[col]].groupby('year').size()
        result[trend] = (count / yearly_total * 100).fillna(0)
    return result.round(1)


def compute_trend_peaks(df):
    """Peak share and peak year for each trend.

    Returns:
        DataFrame: index=trend_name, columns=['peak_pct', 'peak_year', 'total_companies']
    """
    yearly = compute_trend_share_yearly(df)
    return pd.DataFrame({
        'peak_pct':        yearly.max(),
        'peak_year':       yearly.idxmax(),
        'total_companies': [df[trend_col(t)].sum() for t in TREND_NAMES],
    })


# ============================================================
# Aggregation -- coexistence
# ============================================================

def compute_ai_coexistence(df):
    """Share of each reference-trend cohort that is also tagged AI, by year.

    Returns:
        DataFrame: index=year, columns=['AI in Enterprise SaaS', 'AI in Fintech', ...]
    """
    result = pd.DataFrame()
    for ref_trend in REFERENCE_TRENDS:
        col = trend_col(ref_trend)
        sub = df[df[col]]
        rate = sub.groupby('year')['is_AI'].mean() * 100
        result[f'AI in {ref_trend}'] = rate
    return result.round(1)


# ============================================================
# Aggregation -- geography
# ============================================================

def compute_bay_area_concentration(df, exclude_unknown=True):
    """Bay Area share over time, split by AI vs non-AI.

    Returns:
        DataFrame: index=year,
                   columns=['AI in Bay Area %', 'Non-AI in Bay Area %', 'Gap']
    """
    df_use = df[df['region'] != 'Unknown'] if exclude_unknown else df
    df_use = df_use.assign(in_bay=lambda x: x['region'] == 'Bay Area')

    result = (
        df_use.groupby(['year', 'is_AI'])['in_bay']
        .mean().unstack() * 100
    ).round(1)
    result.columns = ['Non-AI in Bay Area %', 'AI in Bay Area %']
    result['Gap'] = (result['AI in Bay Area %'] - result['Non-AI in Bay Area %']).round(1)
    return result[['AI in Bay Area %', 'Non-AI in Bay Area %', 'Gap']]


def compute_city_stats(df, year=None, top_n=20):
    """Company count and AI share per city (for map rendering).

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
    return grouped.sort_values('n_companies', ascending=False).head(top_n).reset_index(drop=True)


# ============================================================
# Streamlit shared styles
# ============================================================

def apply_global_style():
    """Inject global CSS. Call once at the top of each page."""
    st.markdown("""
        <style>
        /* Hide Streamlit chrome */
        #MainMenu, footer, header { visibility: hidden; }

        /* Page container */
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 5rem !important;
            max-width: 1080px !important;
        }

        /* Hero */
        .hero { padding: 64px 0 36px; }
        .hero-title {
            font-size: 48px;
            font-weight: 700;
            color: #111;
            line-height: 1.12;
            margin: 0 0 20px;
            letter-spacing: -1px;
            max-width: 820px;
        }
        .hero-sub {
            font-size: 17px;
            color: #666;
            line-height: 1.5;
            margin: 0;
        }

        /* Section headers */
        .section-eyebrow {
            font-size: 11px;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            color: #E6550D;
            font-weight: 600;
            margin-bottom: 10px;
            margin-top: 8px;
        }
        .section-title {
            font-size: 28px;
            font-weight: 650;
            color: #111;
            line-height: 1.2;
            margin: 0 0 10px;
            letter-spacing: -0.4px;
        }
        .section-sub {
            font-size: 15px;
            color: #666;
            line-height: 1.6;
            max-width: 680px;
            margin: 0 0 28px;
        }

        /* Section divider */
        .section-rule {
            border-top: 1px solid #E8E8E8;
            margin: 56px 0 48px;
        }

        /* Finding box */
        .finding-box {
            background: #FFF8F3;
            border-left: 3px solid #E6550D;
            padding: 16px 22px;
            margin: 32px 0 8px;
            border-radius: 2px;
            font-size: 15px;
            line-height: 1.65;
            color: #111;
        }
        .finding-box strong { color: #E6550D; font-weight: 600; }

        /* Metric cards */
        [data-testid="metric-container"] {
            background: #F7F7F7;
            border-radius: 6px;
            padding: 18px 20px !important;
        }
        [data-testid="metric-container"] label {
            font-size: 11px !important;
            letter-spacing: 1.5px !important;
            text-transform: uppercase !important;
            color: #888 !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 28px !important;
            font-weight: 650 !important;
            color: #111 !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            border-bottom: 1px solid #E8E8E8;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 13px;
            letter-spacing: 0.5px;
            padding: 10px 20px;
            color: #888;
        }
        .stTabs [aria-selected="true"] {
            color: #111 !important;
            border-bottom: 2px solid #E6550D !important;
        }
        </style>
    """, unsafe_allow_html=True)


def finding_box(text):
    """Render a highlighted finding callout box."""
    st.markdown(f'<div class="finding-box">{text}</div>', unsafe_allow_html=True)
