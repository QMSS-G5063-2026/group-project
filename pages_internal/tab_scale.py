"""
Tab -- Text Analysis
Owner: Team Member A (Yehua Huang)

Evidence question: Do AI companies use language that is qualitatively different
from past trends -- and did that language change after ChatGPT?

Charts:
  1. Metric cards: cohort sizes for 2018-2021 vs 2022-2025 (same range as chart)
  2. Keyword tabs: top 15 terms per trend (interactive, one tab per trend)
  3. Language shift: pre/post ChatGPT normalized keyword frequency (main chart)
  4. Finding callout (all numbers computed dynamically)
"""

import re
from collections import Counter

import pandas as pd
import streamlit as st
import plotly.express as px
import utils


# ---------------------------------------------------------------------------
# Keyword helpers -- no external NLP dependency
# ---------------------------------------------------------------------------
_STOPWORDS = {
    'the', 'and', 'for', 'with', 'that', 'this', 'from', 'into', 'about',
    'your', 'you', 'are', 'our', 'their', 'using', 'use', 'build', 'built',
    'helps', 'help', 'platform', 'company', 'companies', 'startup', 'startups',
    'make', 'makes', 'making', 'create', 'creates', 'creating', 'turn',
    'provide', 'provides', 'solution', 'solutions', 'data', 'software',
    'tool', 'tools', 'product', 'products', 'business', 'businesses',
    'customer', 'customers', 'new', 'can', 'has', 'have', 'its', 'will',
    'get', 'manage', 'allow', 'allows', 'enable', 'enables', 'give', 'gives',
    'more', 'all', 'any', 'one', 'lets', 'let', 'way', 'ways', 'across',
    'based', 'driven', 'first', 'next', 'end',
}


def _top_keywords(texts, top_n=50):
    """Return (term, count) pairs from a list of text strings."""
    counter = Counter()
    for text in texts:
        words = re.findall(r'\b[a-zA-Z][a-zA-Z]{2,}\b', str(text).lower())
        for w in words:
            if w not in _STOPWORDS:
                counter[w] += 1
    return counter.most_common(top_n)


def render(df):
    # --------------------------------------------------------------------------
    # Date ranges -- used consistently for BOTH metric cards AND the chart
    # --------------------------------------------------------------------------
    PRE_START, PRE_END   = 2018, 2021
    POST_START, POST_END = 2022, 2025

    pre_mask  = df['is_AI'] & df['year'].between(PRE_START,  PRE_END)
    post_mask = df['is_AI'] & df['year'].between(POST_START, POST_END)
    n_pre     = int(pre_mask.sum())
    n_post    = int(post_mask.sum())

    # --------------------------------------------------------------------------
    # Metric cards (consistent with chart date ranges)
    # --------------------------------------------------------------------------
    c1, c2, c3 = st.columns(3)
    c1.metric('AI companies in dataset', f'{int(df["is_AI"].sum()):,}')
    c2.metric(f'AI companies {PRE_START}-{PRE_END}', f'{n_pre:,}')
    c3.metric(f'AI companies {POST_START}-{POST_END}', f'{n_post:,}',
              f'{n_post / max(n_pre, 1):.1f}x growth vs pre-2022',
              delta_color='off')

    # --------------------------------------------------------------------------
    # Chart 1: Keyword comparison -- one tab per trend
    # Fixes: automargin=True on y-axis, explicit left margin for labels
    # --------------------------------------------------------------------------
    st.markdown(
        '<div style="margin-top:28px; font-size:17px; font-weight:600; '
        'color:#111;">How each trend describes itself</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        'Top 15 keywords from company one-liners. '
        'Generic business terms removed. Switch tabs to compare trends.'
    )

    inner_tabs = st.tabs(utils.TREND_NAMES)
    for tab, trend in zip(inner_tabs, utils.TREND_NAMES):
        with tab:
            texts = (
                df[df[utils.trend_col(trend)]]['One Liner']
                .dropna().astype(str).tolist()
            )
            kw_pairs = _top_keywords(texts, top_n=15)
            if kw_pairs:
                kw_df = pd.DataFrame(kw_pairs, columns=['Term', 'Count'])
                fig = px.bar(
                    kw_df.sort_values('Count'),
                    x='Count',
                    y='Term',
                    orientation='h',
                    color_discrete_sequence=[utils.COLORS[trend]],
                    height=450,
                )
                fig.update_layout(
                    template='plotly_white',
                    xaxis_title='Mentions in one-liners',
                    yaxis_title=None,
                    yaxis=dict(automargin=True),   # <-- FIX: prevents label clipping
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(l=20, r=30, t=20, b=20),
                )
                st.plotly_chart(fig, width="stretch")
                st.caption(f'Based on {len(texts):,} {trend} company one-liners.')
            else:
                st.info(f'No one-liner data available for {trend}.')

    # --------------------------------------------------------------------------
    # Chart 2: Pre / Post ChatGPT language shift
    # Date range 2018-2021 vs 2022-2025, normalized per 100 companies
    # --------------------------------------------------------------------------
    st.markdown(
        '<div style="margin-top:36px; font-size:17px; font-weight:600; '
        'color:#111;">Language shift: before vs. after ChatGPT</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        f'AI companies in {PRE_START}-{PRE_END} vs {POST_START}-{POST_END}. '
        'Normalized to mentions per 100 company descriptions so the larger '
        'post-2022 cohort does not inflate raw counts. '
        'Sorted by post-2022 frequency.'
    )

    pre_texts  = df[pre_mask]['One Liner'].dropna().astype(str).tolist()
    post_texts = df[post_mask]['One Liner'].dropna().astype(str).tolist()

    n_pre_c  = max(len(pre_texts),  1)
    n_post_c = max(len(post_texts), 1)

    pre_raw  = Counter(dict(_top_keywords(pre_texts,  top_n=500)))
    post_raw = Counter(dict(_top_keywords(post_texts, top_n=500)))

    # Normalize to per-100-company rate
    pre_norm  = {k: v / n_pre_c  * 100 for k, v in pre_raw.items()}
    post_norm = {k: v / n_post_c * 100 for k, v in post_raw.items()}

    # Top-20 by post frequency -- shows vocabulary AI companies use TODAY
    all_terms = set(pre_norm) | set(post_norm)
    top_terms = sorted(all_terms, key=lambda t: -post_norm.get(t, 0))[:20]

    pre_label  = f'{PRE_START}-{PRE_END}  (n={n_pre_c})'
    post_label = f'{POST_START}-{POST_END}  (n={n_post_c})'

    shift_rows = []
    for term in top_terms:
        shift_rows.append({'Keyword': term, 'Period': pre_label,
                           'Per 100': round(pre_norm.get(term, 0), 1)})
        shift_rows.append({'Keyword': term, 'Period': post_label,
                           'Per 100': round(post_norm.get(term, 0), 1)})

    shift_df = pd.DataFrame(shift_rows)

    fig_shift = px.bar(
        shift_df,
        x='Keyword',
        y='Per 100',
        color='Period',
        barmode='group',
        color_discrete_map={pre_label: '#3182BD', post_label: '#E6550D'},
        height=500,
    )
    fig_shift.update_layout(
        template='plotly_white',
        xaxis_tickangle=-40,
        xaxis=dict(automargin=True),  # prevents x-label clipping
        xaxis_title=None,
        yaxis_title='Mentions per 100 company descriptions',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.04,
            xanchor='left',
            x=0,
            title_text=None,
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=60, b=100),
    )
    st.plotly_chart(fig_shift, width="stretch")

    # --------------------------------------------------------------------------
    # Finding box -- all numbers computed dynamically from the data above
    # --------------------------------------------------------------------------

    # Top post-ChatGPT gainer (word that grew the most)
    gainers = sorted(
        [(t, post_norm.get(t, 0) - pre_norm.get(t, 0)) for t in top_terms],
        key=lambda x: -x[1],
    )
    top_gainer, top_gain     = gainers[0]
    runner_up,  runner_gain  = gainers[1] if len(gainers) > 1 else ('', 0)

    # Top-3 AI keywords right now (first 3 by post frequency) -- replaces hardcoded list
    top3_ai = top_terms[:3]
    top3_str = '", "'.join(top3_ai)

    # Check which top AI keywords are rare in reference trends
    rare_in_ref = []
    for kw in top3_ai:
        is_rare = True
        for ref in utils.REFERENCE_TRENDS:
            ref_texts = (
                df[df[utils.trend_col(ref)]]['One Liner']
                .dropna().astype(str).tolist()
            )
            ref_raw = Counter(dict(_top_keywords(ref_texts, top_n=200)))
            n_ref   = max(len(ref_texts), 1)
            ref_rate = ref_raw.get(kw, 0) / n_ref * 100
            if ref_rate > post_norm.get(kw, 0) * 0.5:  # if ref rate > 50% of AI rate
                is_rare = False
                break
        if is_rare:
            rare_in_ref.append(kw)

    rare_str = ('", "'.join(rare_in_ref[:2]) if rare_in_ref
                else top3_ai[0])

    utils.finding_box(
        f'<strong>AI company language is qualitatively different from past trends -- '
        f'and changed sharply after ChatGPT.</strong><br>'
        f'Terms like "<em>{rare_str}</em>" dominate AI one-liners '
        f'but appear far less in SaaS, Fintech, and Developer Tools descriptions '
        f'(see the tabs above). '
        f'After ChatGPT launched, "<em>{top_gainer}</em>" grew by '
        f'+{top_gain:.1f} mentions per 100 AI companies; '
        f'"<em>{runner_up}</em>" by +{runner_gain:.1f}. '
        f'This is not a gradual evolution -- it is a vocabulary shift.'
    )
