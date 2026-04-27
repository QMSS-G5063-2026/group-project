"""
Page 0 -- Overview (shown as "Overview" in the sidebar)
"""

import streamlit as st
import plotly.graph_objects as go
import utils

st.set_page_config(
    page_title="Does AI's trend look like the trends that came before it?",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

utils.apply_global_style()

df          = utils.load_data()
trend_share = utils.compute_trend_share_yearly(df)
peaks       = utils.compute_trend_peaks(df)
n_companies = len(df)
n_batches   = df['Batch'].nunique()
year_min    = int(df['year'].min())
year_max    = int(df['year'].max())

ai_peak_val   = peaks.loc['AI',              'peak_pct']
ai_peak_year  = int(peaks.loc['AI',              'peak_year'])
saas_peak_val = peaks.loc['Enterprise SaaS', 'peak_pct']
saas_peak_yr  = int(peaks.loc['Enterprise SaaS', 'peak_year'])

# ============================================================================
# HERO
# ============================================================================
st.markdown("""
<div class="hero">
  <h1 class="hero-title">Does the AI trend follow the patterns<br>of earlier YC trends?</h1>
  <p class="hero-sub">
    A comparison of AI with three reference trends in Y Combinator's portfolio (2011–2025).
    Use the sidebar to explore three independent ways of measuring this difference.
  </p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Companies analyzed", f"{n_companies:,}")
c2.metric("Batches covered",    f"{n_batches}")
c3.metric("Year range",         f"{year_min}-{year_max}")

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# ============================================================================
# OVERVIEW CHART
# ============================================================================
st.markdown("""
<div class="section-eyebrow">The Trend</div>
<div class="section-title">Four trends. One looks different.</div>
<div class="section-sub">
  YC's portfolio has seen several dominant trends since 2005. Each produced a recognizable
  cluster of companies with a shared vocabulary, a shared market, and a recognizable arc.
  We use Enterprise SaaS, Fintech, and Developer Tools as reference trends — three
  well-defined vertical sectors with sufficient scale in the data and clear market boundaries
  — and ask whether AI follows the same pattern.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<table style="width:100%; border-collapse:collapse; font-size:13px;
              margin-bottom:28px; color:#333;">
  <thead>
    <tr style="border-bottom:2px solid #E8E8E8; text-align:left;">
      <th style="padding:8px 12px; color:#888; font-weight:600;
                 letter-spacing:1px; text-transform:uppercase; font-size:11px;">Period</th>
      <th style="padding:8px 12px; color:#888; font-weight:600;
                 letter-spacing:1px; text-transform:uppercase; font-size:11px;">Wave</th>
      <th style="padding:8px 12px; color:#888; font-weight:600;
                 letter-spacing:1px; text-transform:uppercase; font-size:11px;">Representative keywords</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom:1px solid #F0F0F0;">
      <td style="padding:8px 12px; color:#999;">2005–2010</td>
      <td style="padding:8px 12px;">Web 2.0 &amp; early consumer internet</td>
      <td style="padding:8px 12px; color:#666;">community, content, lightweight tools</td>
    </tr>
    <tr style="border-bottom:1px solid #F0F0F0;">
      <td style="padding:8px 12px; color:#999;">2010–2016</td>
      <td style="padding:8px 12px;">Mobile &amp; consumer marketplaces</td>
      <td style="padding:8px 12px; color:#666;">Airbnb, DoorDash, Instacart model</td>
    </tr>
    <tr style="border-bottom:1px solid #F0F0F0; background:#F9F9F9;">
      <td style="padding:8px 12px; color:#999;">2012–2020</td>
      <td style="padding:8px 12px; font-weight:600;">B2B SaaS · Fintech · Developer Tools ✦</td>
      <td style="padding:8px 12px; color:#666;">Stripe, enterprise SaaS, developer infrastructure</td>
    </tr>
    <tr style="border-bottom:1px solid #F0F0F0;">
      <td style="padding:8px 12px; color:#999;">2017–2022</td>
      <td style="padding:8px 12px;">Crypto / Web3 &amp; remote collaboration</td>
      <td style="padding:8px 12px; color:#666;">DeFi, NFT, DAO, remote-first tooling</td>
    </tr>
    <tr style="background:#FFF8F3;">
      <td style="padding:8px 12px; color:#999;">2020–present</td>
      <td style="padding:8px 12px; font-weight:600; color:#E6550D;">AI / GenAI / Agentic &amp; deep tech</td>
      <td style="padding:8px 12px; color:#666;">LLM, RAG, Agent, multi-sector AI</td>
    </tr>
  </tbody>
</table>
<div style="font-size:13px; color:#999; margin-bottom:24px;">
  ✦ Reference group: three well-defined vertical-sector trends with clear market focus
  and sufficient representation in the YC dataset — used as benchmarks throughout this analysis.
</div>
""", unsafe_allow_html=True)

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
    font=dict(size=11, color='#999'), arrowcolor='#ccc',
)
fig.add_vline(x=2022, line_dash='dash', line_color='#CCCCCC', opacity=0.8)
fig.add_annotation(
    x=2022, y=ai_peak_val * 0.92,
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
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=20),
    hovermode='x unified',
)

st.plotly_chart(fig, width="stretch")
st.caption(
    "Lines may sum to >100% -- companies can belong to multiple trends "
    "(e.g., a fintech company that is also an AI company)."
)

ai_latest_pct = trend_share.loc[year_max, 'AI']

utils.finding_box(
    f"<strong>Past trends peaked and plateaued. AI has not.</strong><br>"
    f"Enterprise SaaS peaked at {saas_peak_val:.0f}% of YC batches in {saas_peak_yr}. "
    f"AI reached {ai_peak_val:.0f}% in {ai_peak_year} and still accounts for "
    f"{ai_latest_pct:.0f}% of companies in {year_max} — with no sign of plateauing. "
    f"But the growth curve alone doesn't explain why. "
    f"Three measurements test whether AI is simply a bigger version of past trends, "
    f"or something structurally different:<br>"
    f"<strong>01 Text</strong> — AI vocabulary has spread into every other sector's descriptions.<br>"
    f"<strong>02 Coexistence</strong> — AI grows <em>inside</em> other sectors, not beside them.<br>"
    f"<strong>03 Geography</strong> — AI re-concentrated in the Bay Area while other trends dispersed."
)

# ============================================================================
# ABOUT
# ============================================================================
st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
with st.expander("About this project"):
    st.markdown(f"""
**Course:** Columbia University QMSS GR5063 — Data Visualization

**Team:** Jiahao Huang (jh5140), Xiang Fan (xf2300), Zhicheng Jiang (zj2433), Yehua Huang (yh3932)

**Data source:** Y Combinator company dataset via Hugging Face ({year_min}–{year_max}).
{n_companies:,} companies across {n_batches} batches.
""")
