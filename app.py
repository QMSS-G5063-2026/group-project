"""
app.py -- Streamlit entry point (single-page scroll layout).

Run: streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import utils

st.set_page_config(
    page_title="Does AI's trend look like the trends that came before it?",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

utils.apply_global_style()

df = utils.load_data()

# -- Pre-compute shared stats ------------------------------------------------
trend_share = utils.compute_trend_share_yearly(df)
peaks       = utils.compute_trend_peaks(df)
n_companies = len(df)
n_batches   = df['Batch'].nunique()
year_min    = int(df['year'].min())
year_max    = int(df['year'].max())

# -- Hero --------------------------------------------------------------------
st.markdown("""
<div class="hero">
  <h1 class="hero-title">Does AI's trend look like the trends that came before it?</h1>
  <p class="hero-sub">
    Comparing AI to three reference trends in Y Combinator's portfolio, 2011-2025.
  </p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Companies analyzed", f"{n_companies:,}")
c2.metric("Batches covered", f"{n_batches}")
c3.metric("Year range", f"{year_min}-{year_max}")

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# -- Section 01: The Trend ---------------------------------------------------
st.markdown("""
<div class="section-eyebrow">01 -- The Trend</div>
<div class="section-title">Four trends. One looks different.</div>
<div class="section-sub">
  Enterprise SaaS, Fintech, and Developer Tools each followed a recognizable arc --
  rise, sustain, plateau. AI has not followed that arc.
</div>
""", unsafe_allow_html=True)

# Overview chart: 3 gray dashed reference lines + 1 thick AI line
fig = go.Figure()

for ref in utils.REFERENCE_TRENDS:
    fig.add_trace(go.Scatter(
        x=trend_share.index,
        y=trend_share[ref],
        name=ref,
        line=dict(color=utils.COLORS['ref_line'], width=1.5, dash='dot'),
        mode='lines',
        hovertemplate='%{x}: %{y:.1f}%<extra>' + ref + '</extra>',
    ))

fig.add_trace(go.Scatter(
    x=trend_share.index,
    y=trend_share['AI'],
    name='AI',
    line=dict(color=utils.COLORS['AI'], width=4),
    mode='lines+markers',
    marker=dict(size=6),
    hovertemplate='%{x}: %{y:.1f}%<extra>AI</extra>',
))

ai_peak_year = int(peaks.loc['AI', 'peak_year'])
ai_peak_val  = peaks.loc['AI', 'peak_pct']
saas_peak_yr = int(peaks.loc['Enterprise SaaS', 'peak_year'])
saas_peak_val = peaks.loc['Enterprise SaaS', 'peak_pct']

fig.add_annotation(
    x=ai_peak_year, y=ai_peak_val,
    text=f"<b>AI: {ai_peak_val:.0f}%</b>",
    showarrow=False, yshift=16,
    font=dict(size=13, color=utils.COLORS['AI']),
)
fig.add_annotation(
    x=saas_peak_yr, y=saas_peak_val,
    text=f"SaaS peak: {saas_peak_val:.0f}%",
    showarrow=True, arrowhead=2, ax=-60, ay=-30,
    font=dict(size=11, color='#999'),
    arrowcolor='#ccc',
)
fig.add_vline(x=2022, line_dash='dash', line_color='#CCCCCC', opacity=0.8)
fig.add_annotation(
    x=2022, y=ai_peak_val * 0.94,
    text='ChatGPT', showarrow=False,
    font=dict(size=10, color='#aaa'),
    xanchor='left', xshift=6,
)

fig.update_layout(
    height=420,
    yaxis=dict(title='% of YC batch', range=[0, min(ai_peak_val + 12, 95)],
               ticksuffix='%', gridcolor='#F0F0F0'),
    xaxis=dict(title=None, dtick=1),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=20),
    hovermode='x unified',
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Lines may sum to >100% -- companies can belong to multiple trends "
    "(e.g., a fintech company that is also an AI company)."
)

utils.finding_box(
    "<strong>Past trends followed a familiar shape -- rise, sustain, plateau.</strong><br>"
    "AI hasn't plateaued. It is still climbing.<br><br>"
    "Does AI's trend look like the trends that came before it?"
)

st.markdown(
    '<div class="see-evidence">Scroll down to see the evidence &darr;</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# -- Three Measurements intro ------------------------------------------------
st.markdown("""
<div class="section-eyebrow">Three Measurements</div>
<div class="section-title">If AI behaves like past trends, it should resemble them.</div>
<div class="measurements-intro">
  We compare AI to three reference trends along three independent dimensions:
  magnitude, coexistence with other trends, and geographic distribution.
  Each measurement tests the same question from a different angle.
</div>
""", unsafe_allow_html=True)

# -- Section 02: Magnitude ---------------------------------------------------
st.markdown("""
<div class="section-eyebrow">Magnitude</div>
<div class="section-title">Is AI's peak within the historical range?</div>
<div class="section-sub">
  We compare AI's batch share against the peak of each reference trend.
</div>
""", unsafe_allow_html=True)

from pages_internal import tab_scale
tab_scale.render(df)

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# -- Section 03: Coexistence -------------------------------------------------
st.markdown("""
<div class="section-eyebrow">Coexistence</div>
<div class="section-title">Does AI exist alongside other trends, or inside them?</div>
<div class="section-sub">
  Reference trends coexisted as parallel sectors. We test whether AI stays
  separate or appears inside Enterprise SaaS, Fintech, and Developer Tools.
</div>
""", unsafe_allow_html=True)

from pages_internal import tab_penetration
tab_penetration.render(df)

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# -- Section 04: Geography ---------------------------------------------------
st.markdown("""
<div class="section-eyebrow">Geography</div>
<div class="section-title">Does AI's geographic shape match past trends?</div>
<div class="section-sub">
  Remote work was expected to disperse founders globally.
  We check whether AI followed that trend or reversed it.
</div>
""", unsafe_allow_html=True)

from pages_internal import tab_geography
tab_geography.render(df)

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# -- Conclusion --------------------------------------------------------------
st.markdown("""
<div class="section-eyebrow">Conclusion</div>
<div class="section-title">A Different Kind of Trend</div>
<div class="section-sub">Three measurements. One observation.</div>
""", unsafe_allow_html=True)

from pages_internal import page3_answer
page3_answer.render_conclusion(df)

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# -- About -------------------------------------------------------------------
st.markdown("""
<div class="section-eyebrow">About</div>
<div class="section-title">Data, methodology &amp; team</div>
""", unsafe_allow_html=True)

col_a, col_b = st.columns([3, 2])

with col_a:
    st.markdown("""
**Data source**
[YC Companies dataset](https://huggingface.co/datasets/datahiveai/ycombinator-companies)
by DataHive AI on HuggingFace -- 5,080 companies from Y Combinator batches 2011-2025.

**Trend definitions**
- **AI** -- concept-level merge of 16 tags including `ai`, `generative-ai`, `machine-learning`,
  `computer-vision`, `nlp`, `chatbot`, and more.
- **Enterprise SaaS** -- union of `saas` and `b2b` (Jaccard = 0.33)
- **Fintech** -- `fintech`
- **Developer Tools** -- `developer-tools`

**Trends excluded from comparison**
Consumer/Mobile (predates dataset), Crypto/Web3 (insufficient scale), Marketplace
(single-year peak in 2011, did not recur).

**Limitations**
This study measures *concentration*, not impact -- we have no funding, valuation, or exit data.
YC's tag labeling is inconsistent and skews toward Bay Area founders; findings should be
interpreted as trends *within YC's selection*, not the broader startup ecosystem.
""")

with col_b:
    st.markdown("""
**Built with**
- [Streamlit](https://streamlit.io)
- [Plotly](https://plotly.com)
- [Pandas](https://pandas.pydata.org)
- [NetworkX](https://networkx.org)
- [Folium](https://python-visualization.github.io/folium/)

**Course**
QMSS Data Visualization -- Columbia University

**Source code**
[GitHub repository](https://github.com)
""")

st.markdown(
    '<div style="color:#bbb;font-size:12px;padding:32px 0 8px;">'
    'Data: HuggingFace datahiveai/ycombinator-companies &middot; '
    'Visualization: Streamlit + Plotly</div>',
    unsafe_allow_html=True,
)
