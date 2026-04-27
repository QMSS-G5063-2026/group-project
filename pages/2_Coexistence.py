"""
Page 2 -- Coexistence
Owner: Team Member B (Xiang Fan)

Question: Does AI exist alongside other trends, or inside them?
"""

import streamlit as st
import plotly.graph_objects as go
import utils

st.set_page_config(
    page_title="Coexistence -- YC AI Trends",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

utils.apply_global_style()

df = utils.load_data()

st.markdown("""
<div class="section-eyebrow">Measurement 02 &mdash; Coexistence</div>
<div class="section-title">AI grows inside other trends, not beside them</div>
<div class="section-sub">
  Vertical sectors tend to stay in their own lanes — a Fintech company is primarily
  a Fintech company. A horizontal platform behaves differently: it shows up inside
  every sector it touches. We measure cross-sector penetration to see which pattern AI follows.
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Compute coexistence over time
# ---------------------------------------------------------------------------
coexistence = utils.compute_ai_coexistence(df)
last_year   = int(coexistence.index.max())
earliest    = int(coexistence.index.min())

saas_latest     = coexistence.loc[last_year, 'AI in Enterprise SaaS']
fintech_latest  = coexistence.loc[last_year, 'AI in Fintech']
devtools_latest = coexistence.loc[last_year, 'AI in Developer Tools']
saas_earliest   = coexistence.loc[earliest,  'AI in Enterprise SaaS']

# ---------------------------------------------------------------------------
# Metric cards
# ---------------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric(f'AI share of Enterprise SaaS ({last_year})', f'{saas_latest:.0f}%',
          f'+{saas_latest - saas_earliest:.0f} pts since {earliest}')
c2.metric(f'AI share of Fintech ({last_year})',          f'{fintech_latest:.0f}%')
c3.metric(f'AI share of Developer Tools ({last_year})',  f'{devtools_latest:.0f}%')

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# ===========================================================================
# SECTION A: AI coexistence rate over time
# ===========================================================================
st.markdown("""
<div style="font-size:20px; font-weight:700; color:#111; margin-bottom:6px;">
  AI's share inside each reference trend, by year
</div>
<div style="font-size:14px; color:#666; margin-bottom:16px;">
  Each line shows what percentage of that trend's cohort is also tagged AI.
  A rising line means AI is absorbing the sector from within.
</div>
""", unsafe_allow_html=True)

_LINE_COLORS = {
    'AI in Enterprise SaaS': utils.COLORS['Enterprise SaaS'],
    'AI in Fintech':          utils.COLORS['Fintech'],
    'AI in Developer Tools':  utils.COLORS['Developer Tools'],
}

fig_time = go.Figure()
for col_name, color in _LINE_COLORS.items():
    fig_time.add_trace(go.Scatter(
        x=coexistence.index,
        y=coexistence[col_name],
        mode='lines+markers',
        name=col_name,
        line=dict(width=3, color=color),
        marker=dict(size=7),
        hovertemplate='%{x}: %{y:.1f}%<extra>' + col_name + '</extra>',
    ))

fig_time.add_vline(x=2022, line_dash='dash', line_color='#CCCCCC', opacity=0.8)
fig_time.add_annotation(
    x=2022, y=95, text='ChatGPT launched', showarrow=False,
    font=dict(size=10, color='#aaa'), xanchor='left', xshift=6,
)
fig_time.update_layout(
    xaxis_title=None,
    yaxis=dict(title='Share of trend cohort also tagged AI',
               range=[0, 100], ticksuffix='%', gridcolor='#F0F0F0'),
    hovermode='x unified',
    height=420,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                title_text=None),
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=20),
)
st.plotly_chart(fig_time, width='stretch')

st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

# ===========================================================================
# SECTION B: Cross-penetration heatmap (all 4 trends)
# ===========================================================================
trends = utils.TREND_NAMES  # ['AI', 'Enterprise SaaS', 'Fintech', 'Developer Tools']

st.markdown("""
<div style="font-size:20px; font-weight:700; color:#111; margin-bottom:6px;">
  Full cross-penetration matrix
</div>
<div style="font-size:14px; color:#666; margin-bottom:16px;">
  Each cell = % of the <strong>row</strong> trend's companies that are also tagged
  as the <strong>column</strong> trend. Read down the <strong>AI column</strong>
  to see that AI intersects with every other sector simultaneously at high rates.
</div>
""", unsafe_allow_html=True)

matrix_data = []
for t1 in trends:
    col1 = utils.trend_col(t1)
    n_t1 = int(df[col1].sum())
    row  = []
    for t2 in trends:
        col2  = utils.trend_col(t2)
        n_both = int((df[col1] & df[col2]).sum())
        row.append(round(n_both / max(n_t1, 1) * 100, 1))
    matrix_data.append(row)

short = ['AI', 'SaaS', 'Fintech', 'DevTools']
fig_heat = go.Figure(go.Heatmap(
    z=matrix_data,
    x=short,
    y=short,
    colorscale='Oranges',
    zmin=0, zmax=100,
    text=[[f'{v:.0f}%' for v in row] for row in matrix_data],
    texttemplate='%{text}',
    textfont=dict(size=14, color='black'),
    hovertemplate='%{y} → %{x}: %{z:.1f}%<extra></extra>',
    showscale=True,
    colorbar=dict(title='%', thickness=14),
))
fig_heat.update_layout(
    height=360,
    xaxis=dict(title='Also tagged as…', side='bottom'),
    yaxis=dict(title='Base trend', autorange='reversed'),
    margin=dict(l=80, r=20, t=20, b=60),
    plot_bgcolor='white', paper_bgcolor='white',
)
st.plotly_chart(fig_heat, width='stretch')
st.caption(
    'Diagonal = 100% (a trend overlaps with itself). '
    'Read each row as: "X% of [row] companies are also tagged [column]."'
)

# ===========================================================================
# Finding
# ===========================================================================

utils.finding_box(
    f'<strong>AI is the only trend that penetrates every other sector simultaneously.</strong><br>'
    f'In {last_year}, {saas_latest:.0f}% of Enterprise SaaS companies, '
    f'{fintech_latest:.0f}% of Fintech companies, and {devtools_latest:.0f}% of '
    f'Developer Tools companies are also tagged AI — a uniform, broad presence across '
    f'all three sectors at once. Reference trends do overlap with one another to varying '
    f'degrees, but no single non-AI trend shows this same pattern of simultaneous '
    f'high penetration across the whole portfolio. '
    f'The coexistence chart above shows this share has been rising steadily — '
    f'AI is not a sector that grew beside the others, but one that has spread through all of them.'
)
