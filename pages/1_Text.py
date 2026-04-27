"""
Page 1 -- Text Analysis
Owner: Team Member A (Yehua Huang)

Question: Has AI vocabulary crossed into other sectors, and when did it happen?
"""

import re
from collections import Counter

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import utils

try:
    from wordcloud import WordCloud, STOPWORDS as WC_STOPWORDS
    import matplotlib.pyplot as plt
    HAS_WORDCLOUD = True
except ImportError:
    HAS_WORDCLOUD = False

st.set_page_config(
    page_title="Text Analysis -- YC AI Trends",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

utils.apply_global_style()

df = utils.load_data()

st.markdown("""
<div class="section-eyebrow">Measurement 01 &mdash; Text</div>
<div class="section-title">AI vocabulary has crossed into every other sector</div>
<div class="section-sub">
  If AI were just another vertical sector, its vocabulary would stay inside its own lane —
  the way Fintech vocabulary stays in Fintech. We look at whether AI-associated terms
  appear in the most common words used by other trends, and when that pattern emerged.
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_STOPWORDS = {
    'the', 'and', 'for', 'with', 'that', 'this', 'from', 'into', 'about',
    'your', 'you', 'are', 'our', 'their', 'using', 'use', 'build', 'built',
    'helps', 'help', 'platform', 'company', 'companies', 'startup', 'startups',
    'make', 'makes', 'making', 'create', 'creates', 'creating', 'turn',
    'provide', 'provides', 'solution', 'solutions', 'data', 'software',
    'tool', 'tools', 'product', 'products', 'business', 'businesses',
    'customer', 'customers', 'new', 'can', 'has', 'have', 'its', 'will',
    'get', 'manage', 'allow', 'allows', 'enable', 'enables',
    'give', 'gives', 'more', 'all', 'any', 'one', 'lets', 'let',
    'way', 'ways', 'across', 'based', 'driven', 'first', 'next',
}

# Terms commonly associated with AI-era products.
# Used for visual highlighting and frequency tracking — not a definitive taxonomy.
AI_NATIVE_TERMS = {
    'ai', 'agent', 'agents', 'llm', 'llms', 'gpt',
    'automation', 'automate', 'automated',
    'powered', 'intelligence', 'model', 'models',
    'ml', 'native', 'generative', 'assistant',
    'copilot', 'autonomous', 'workflow', 'workflows',
    'cursor',
}


def _clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def _top_keywords(texts, top_n=50):
    counter = Counter()
    for text in texts:
        words = re.findall(r'\b[a-zA-Z][a-zA-Z-]{2,}\b', _clean_text(text))
        for w in words:
            if w not in _STOPWORDS:
                counter[w] += 1
    return counter.most_common(top_n)


def _get_texts(trend):
    return (df[df[utils.trend_col(trend)]]['One Liner']
            .dropna().astype(str).tolist())


# ---------------------------------------------------------------------------
# Metric cards
# ---------------------------------------------------------------------------
n_ai   = int(df['is_AI'].sum())
n_pre  = int((df['is_AI'] & (df['year'] <  2022)).sum())
n_post = int((df['is_AI'] & (df['year'] >= 2022)).sum())

c1, c2, c3 = st.columns(3)
c1.metric('AI companies analyzed',      f'{n_ai:,}')
c2.metric('Before ChatGPT (pre-2022)',  f'{n_pre:,}')
c3.metric('After ChatGPT (2022+)',      f'{n_post:,}',
          f'{n_post / max(n_pre, 1):.1f}× the pre-2022 cohort')

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# ===========================================================================
# SECTION A: Word clouds
# ===========================================================================
st.markdown("""
<div style="font-size:20px; font-weight:700; color:#111; margin-bottom:6px;">
  Word clouds: AI terms appear across every trend
</div>
<div style="font-size:14px; color:#666; margin-bottom:16px;">
  Words sized by frequency in each trend's company one-liners.
  Compare the AI panel with the other three: AI-associated terms visible in the AI cloud
  also tend to appear in SaaS, Fintech, and Developer Tools — suggesting shared vocabulary
  rather than language that stays within a single sector.
</div>
""", unsafe_allow_html=True)

if HAS_WORDCLOUD:
    wc_stopwords = set(WC_STOPWORDS)
    wc_stopwords.update([
        'company', 'companies', 'startup', 'startups',
        'platform', 'helps', 'help', 'build', 'building',
        'use', 'using', 'users', 'customer', 'customers',
        'business', 'businesses', 'data', 'software',
        'tool', 'tools', 'product', 'products',
    ])

    fig_wc, axes = plt.subplots(2, 2, figsize=(18, 10))
    axes = axes.flatten()
    for ax, trend in zip(axes, utils.TREND_NAMES):
        texts     = _get_texts(trend)
        full_text = ' '.join([_clean_text(t) for t in texts])
        if full_text.strip():
            wc = WordCloud(
                width=1000, height=600,
                background_color='white',
                stopwords=wc_stopwords,
                max_words=130,
                colormap='tab10',
                collocations=False,
                prefer_horizontal=0.85,
                random_state=42,
            ).generate(full_text)
            ax.imshow(wc, interpolation='bilinear')
        else:
            ax.text(0.5, 0.5, 'No text available',
                    ha='center', va='center', fontsize=14)
        ax.set_title(trend, fontsize=20, fontweight='bold')
        ax.axis('off')
    plt.suptitle('Word Clouds by Trend', fontsize=26, fontweight='bold', y=1.02)
    plt.tight_layout()
    st.pyplot(fig_wc)
    plt.close(fig_wc)
else:
    st.info('Install `wordcloud` to see the 4-panel word cloud: `pip install wordcloud`')

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# ===========================================================================
# SECTION B: Top keywords by trend (tabs)
# ===========================================================================
st.markdown("""
<div style="font-size:20px; font-weight:700; color:#111; margin-bottom:6px;">
  Top 20 words in each trend — and where AI terms rank
</div>
<div style="font-size:14px; color:#666; margin-bottom:16px;">
  Switch tabs to see the top-20 terms for each trend's one-liners.
  Bars highlighted in orange are AI-associated terms. Each trend's bucket includes
  companies that are also tagged AI, so their presence in non-AI word lists partly
  reflects overlap between categories. The key question is how prominently they rank.
</div>
""", unsafe_allow_html=True)

inner_tabs = st.tabs(utils.TREND_NAMES)
for tab, trend in zip(inner_tabs, utils.TREND_NAMES):
    with tab:
        texts    = _get_texts(trend)
        kw_pairs = _top_keywords(texts, top_n=20)
        if kw_pairs:
            kw_df = pd.DataFrame(kw_pairs, columns=['Term', 'Count'])
            kw_df['AI-native'] = kw_df['Term'].isin(AI_NATIVE_TERMS)
            kw_df = kw_df.sort_values('Count')

            colors = [
                utils.COLORS['AI'] if is_ai else utils.COLORS[trend]
                for is_ai in kw_df['AI-native']
            ]

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=kw_df['Count'],
                y=kw_df['Term'],
                orientation='h',
                marker_color=colors,
                hovertemplate='<b>%{y}</b><br>%{x} mentions<extra></extra>',
            ))
            fig_bar.update_layout(
                template='plotly_white',
                xaxis_title='Mentions in one-liners',
                yaxis=dict(title=None, automargin=True),
                showlegend=False,
                plot_bgcolor='white', paper_bgcolor='white',
                margin=dict(l=10, r=30, t=20, b=10),
                height=480,
            )
            st.plotly_chart(fig_bar, width='stretch')

            ai_terms_in_top = kw_df[kw_df['AI-native']]['Term'].tolist()
            n_ai_terms      = len(ai_terms_in_top)
            if trend == 'AI':
                st.caption(
                    f'Based on {len(texts):,} {trend} company one-liners. '
                    f'{n_ai_terms} of the top 20 terms are AI-associated '
                    f'(highlighted in orange) — as expected for the AI category.'
                )
            else:
                if n_ai_terms > 0:
                    ai_list = ', '.join(f'"{t}"' for t in ai_terms_in_top)
                    st.caption(
                        f'Based on {len(texts):,} {trend} company one-liners. '
                        f'{n_ai_terms} AI-associated term(s) in the top 20: '
                        f'{ai_list} (highlighted in orange).'
                    )
                else:
                    st.caption(
                        f'Based on {len(texts):,} {trend} company one-liners. '
                        f'No AI-associated terms in the top 20.'
                    )
        else:
            st.info(f'No one-liner data available for {trend}.')

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# ===========================================================================
# SECTION C: When did AI vocabulary enter other sectors? (over time)
# ===========================================================================
st.markdown("""
<div style="font-size:20px; font-weight:700; color:#111; margin-bottom:6px;">
  When did AI vocabulary enter other sectors?
</div>
<div style="font-size:14px; color:#666; margin-bottom:16px;">
  Each line shows what share of that trend's company descriptions contained
  at least one AI-associated term in a given year.
  A rising line after 2022 would suggest that AI framing spread across sectors
  around the time of ChatGPT's launch.
</div>
""", unsafe_allow_html=True)

_years   = sorted(df['year'].dropna().unique().astype(int).tolist())
_MIN_N   = 8  # omit year/trend combinations with too few companies

_pen     = {t: [] for t in utils.REFERENCE_TRENDS}
_pen_yrs = []

for yr in _years:
    _pen_yrs.append(yr)
    for trend in utils.REFERENCE_TRENDS:
        texts_yr = (df[df[utils.trend_col(trend)] & (df['year'] == yr)]
                    ['One Liner'].dropna().astype(str).tolist())
        if len(texts_yr) < _MIN_N:
            _pen[trend].append(None)
        else:
            has_ai = sum(
                1 for t in texts_yr
                if any(w in AI_NATIVE_TERMS
                       for w in re.findall(r'\b[a-zA-Z][a-zA-Z-]{2,}\b', _clean_text(t)))
            )
            _pen[trend].append(round(has_ai / len(texts_yr) * 100, 1))

fig_pen = go.Figure()
for trend in utils.REFERENCE_TRENDS:
    fig_pen.add_trace(go.Scatter(
        x=_pen_yrs,
        y=_pen[trend],
        name=trend,
        mode='lines+markers',
        line=dict(color=utils.COLORS[trend], width=2.5),
        marker=dict(size=6),
        connectgaps=True,
        hovertemplate='%{x}: %{y:.1f}%<extra>' + trend + '</extra>',
    ))

fig_pen.add_vline(x=2022, line_dash='dash', line_color='#CCCCCC', opacity=0.8)
fig_pen.add_annotation(
    x=2022, y=95, text='ChatGPT launched', showarrow=False,
    font=dict(size=10, color='#aaa'), xanchor='left', xshift=6,
)
fig_pen.update_layout(
    height=420,
    yaxis=dict(title='% of descriptions mentioning an AI-associated term',
               range=[0, 100], ticksuffix='%', gridcolor='#F0F0F0'),
    xaxis=dict(title=None, dtick=1),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=20),
    hovermode='x unified',
)
st.plotly_chart(fig_pen, width='stretch')
st.caption(
    'Year/trend combinations with fewer than 8 companies are omitted; '
    'lines connect across gaps.'
)

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# ===========================================================================
# SECTION D: Words that emerged after ChatGPT (pre vs post grouped bar)
# ===========================================================================
st.markdown("""
<div style="font-size:20px; font-weight:700; color:#111; margin-bottom:6px;">
  New vocabulary that entered the entire YC portfolio after ChatGPT
</div>
<div style="font-size:14px; color:#666; margin-bottom:16px;">
  Terms that went from near-zero to high frequency across <strong>all YC companies</strong>
  — not just AI-tagged ones — after 2022. If the words that spread portfolio-wide are
  AI terms, it means AI vocabulary entered the general startup lexicon, not just the
  AI bucket. Filtered to words with &lt;0.3 mentions per 100 companies before 2022
  and &ge;0.8 mentions per 100 companies from 2022 onward, sorted by growth multiplier.
  Hover over any bar to see the exact before/after values and growth ratio.
</div>
""", unsafe_allow_html=True)

pre_texts  = df[df['year'] <  2022]['One Liner'].dropna().astype(str).tolist()
post_texts = df[df['year'] >= 2022]['One Liner'].dropna().astype(str).tolist()

n_pre_c  = max(len(pre_texts),  1)
n_post_c = max(len(post_texts), 1)

pre_raw  = Counter(dict(_top_keywords(pre_texts,  top_n=1000)))
post_raw = Counter(dict(_top_keywords(post_texts, top_n=1000)))

pre_norm  = {k: v / n_pre_c  * 100 for k, v in pre_raw.items()}
post_norm = {k: v / n_post_c * 100 for k, v in post_raw.items()}

new_words = {
    word: post_norm[word]
    for word in post_norm
    if post_norm.get(word, 0) >= 0.8 and pre_norm.get(word, 0) <= 0.3
}
top_new = sorted(
    new_words.items(),
    key=lambda x: -x[1] / max(pre_norm.get(x[0], 0.01), 0.01),
)[:15]

ai_in_new     = []
non_ai_in_new = []

if top_new:
    new_df = pd.DataFrame(top_new, columns=['Term', 'Post-2022'])
    new_df['Pre-2022']   = new_df['Term'].map(lambda w: round(pre_norm.get(w, 0), 3))
    new_df['is_ai']      = new_df['Term'].isin(AI_NATIVE_TERMS)
    new_df['Multiplier'] = new_df.apply(
        lambda r: round(r['Post-2022'] / max(r['Pre-2022'], 0.01), 1), axis=1
    )
    new_df = new_df.sort_values('Post-2022')

    ai_in_new     = new_df[new_df['is_ai']]['Term'].tolist()
    non_ai_in_new = new_df[~new_df['is_ai']]['Term'].tolist()
    colors = [utils.COLORS['AI'] if v else '#AAAAAA' for v in new_df['is_ai']]

    fig_new = go.Figure()
    fig_new.add_trace(go.Bar(
        y=new_df['Term'],
        x=new_df['Pre-2022'],
        name='Before 2022',
        orientation='h',
        marker_color='#DDDDDD',
        hovertemplate='<b>%{y}</b><br>Before 2022: %{x:.3f} per 100<extra></extra>',
    ))
    fig_new.add_trace(go.Bar(
        y=new_df['Term'],
        x=new_df['Post-2022'],
        name='2022 onward',
        orientation='h',
        marker_color=colors,
        customdata=new_df[['Pre-2022', 'Multiplier']].values,
        hovertemplate=(
            '<b>%{y}</b><br>'
            '2022 onward: %{x:.2f} per 100<br>'
            'Before 2022: %{customdata[0]:.3f} per 100<br>'
            'Growth: %{customdata[1]:.0f}×'
            '<extra></extra>'
        ),
    ))
    fig_new.update_layout(
        barmode='overlay',
        template='plotly_white',
        xaxis=dict(title='Mentions per 100 company descriptions (all YC)', automargin=True),
        yaxis=dict(title=None, automargin=True),
        height=500,
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=40, t=20, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    )
    st.plotly_chart(fig_new, width='stretch')

    caption_parts = []
    if ai_in_new:
        caption_parts.append(
            f'{len(ai_in_new)} of the {len(new_df)} words are AI-associated (orange): '
            f'{", ".join(ai_in_new)}.'
        )
    if non_ai_in_new:
        caption_parts.append(
            f'Non-AI-associated words also in the list: {", ".join(non_ai_in_new)}.'
        )
    if caption_parts:
        st.caption(' '.join(caption_parts))

# ===========================================================================
# Finding
# ===========================================================================
ref_ai_counts = []
for trend in utils.REFERENCE_TRENDS:
    kw     = _top_keywords(_get_texts(trend), top_n=20)
    n_term = sum(1 for w, _ in kw if w in AI_NATIVE_TERMS)
    ref_ai_counts.append((trend, n_term))

total_ai_in_ref = sum(n for _, n in ref_ai_counts)
n_new = len(top_new) if top_new else 0

_vocab_sentence = ''
if ai_in_new and len(ai_in_new) > len(non_ai_in_new):
    _vocab_sentence = (
        f'The portfolio-wide new vocabulary chart reinforces this: '
        f'{len(ai_in_new)} of the {len(top_new)} words that spread across all YC companies '
        f'after 2022 are AI-associated ({", ".join(ai_in_new[:4])}'
        f'{"…" if len(ai_in_new) > 4 else ""}), '
        f'suggesting the vocabulary shift reached beyond AI-tagged companies.'
    )
elif top_new:
    _vocab_sentence = (
        f'The portfolio-wide new vocabulary chart shows {len(top_new)} terms that grew '
        f'from near-zero to frequent across all YC companies after 2022.'
    )

utils.finding_box(
    f'<strong>AI-associated vocabulary appears across every reference sector — '
    f'and its presence has grown in more recent batches.</strong><br>'
    f'AI-associated terms appear {total_ai_in_ref} times across the top-20 word lists '
    f'of Enterprise SaaS, Fintech, and Developer Tools — ranking alongside each sector\'s '
    f'core vocabulary. Note that each trend\'s bucket includes AI-tagged companies, '
    f'so some overlap is expected; the notable finding is how consistently and highly '
    f'these terms rank. The temporal chart tracks when this share rose across each sector. '
    + (_vocab_sentence if _vocab_sentence else '')
)
