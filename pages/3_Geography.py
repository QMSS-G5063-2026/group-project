"""
Page 3 -- Geography
Owner: Team Member C (Zhicheng Jiang)

Question: Does AI's geographic shape match past trends?
"""

import math

import streamlit as st
import plotly.graph_objects as go
import utils

try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

st.set_page_config(
    page_title="Geography -- YC AI Trends",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

utils.apply_global_style()

df = utils.load_data()

st.markdown("""
<div class="section-eyebrow">Measurement 03 &mdash; Geography</div>
<div class="section-title">Does AI's geographic shape match past trends?</div>
<div class="section-sub">
  Remote work was expected to flatten startup geography.
  We compare Bay Area concentration for AI companies versus non-AI companies
  across the same YC selection process from 2011 to 2025.
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# City coordinates
# ---------------------------------------------------------------------------
CITY_COORDS = {
    'San Francisco':      (37.7749, -122.4194),
    'Mountain View':      (37.3861, -122.0839),
    'Palo Alto':          (37.4419, -122.1430),
    'Menlo Park':         (37.4529, -122.1817),
    'Redwood City':       (37.4852, -122.2364),
    'San Mateo':          (37.5630, -122.3255),
    'Berkeley':           (37.8715, -122.2730),
    'Oakland':            (37.8044, -122.2712),
    'San Jose':           (37.3382, -121.8863),
    'Santa Clara':        (37.3541, -121.9552),
    'Sunnyvale':          (37.3688, -122.0363),
    'South San Francisco':(37.6547, -122.4077),
    'Los Angeles':        (34.0522, -118.2437),
    'New York':           (40.7128,  -74.0060),
    'Brooklyn':           (40.6782,  -73.9442),
    'Boston':             (42.3601,  -71.0589),
    'Seattle':            (47.6062, -122.3321),
    'Austin':             (30.2672,  -97.7431),
    'Chicago':            (41.8781,  -87.6298),
    'Miami':              (25.7617,  -80.1918),
    'Denver':             (39.7392, -104.9903),
    'Toronto':            (43.6532,  -79.3832),
    'Vancouver':          (49.2827, -123.1207),
    'London':             (51.5072,   -0.1276),
    'Paris':              (48.8566,    2.3522),
    'Berlin':             (52.5200,   13.4050),
    'Amsterdam':          (52.3676,    4.9041),
    'Zurich':             (47.3769,    8.5417),
    'Tel Aviv':           (32.0853,   34.7818),
    'Singapore':          ( 1.3521,  103.8198),
    'Bengaluru':          (12.9716,   77.5946),
    'Bangalore':          (12.9716,   77.5946),
    'Delhi':              (28.6139,   77.2090),
    'Mumbai':             (19.0760,   72.8777),
    'Sydney':             (-33.8688, 151.2093),
    'Lagos':              (  6.5244,   3.3792),
    'Nairobi':            ( -1.2921,  36.8219),
}


def _color_for_ai_pct(pct):
    if pct >= 60:
        return '#E6550D'
    if pct >= 35:
        return '#F28E2B'
    if pct >= 15:
        return '#59A14F'
    return '#4E79A7'


# ---------------------------------------------------------------------------
# Compute
# ---------------------------------------------------------------------------
bay       = utils.compute_bay_area_concentration(df)
last_year = int(bay.index.max())
ai_bay    = bay.loc[last_year, 'AI in Bay Area %']
nonai_bay = bay.loc[last_year, 'Non-AI in Bay Area %']
gap       = bay.loc[last_year, 'Gap']

# ---------------------------------------------------------------------------
# Metric cards
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric(f'AI companies in Bay Area ({last_year})',     f'{ai_bay:.0f}%')
col2.metric(f'Non-AI companies in Bay Area ({last_year})', f'{nonai_bay:.0f}%')
_gap_label = 'AI more concentrated' if gap > 0 else 'Non-AI more concentrated'
col3.metric('Concentration gap', f'{gap:+.0f} pts', _gap_label)

# ---------------------------------------------------------------------------
# Bay Area concentration chart
# ---------------------------------------------------------------------------
fig = go.Figure()

# Non-AI first so fill='tonexty' shades the gap
fig.add_trace(go.Scatter(
    x=bay.index, y=bay['Non-AI in Bay Area %'],
    name='Non-AI companies', mode='lines+markers',
    line=dict(color='#969696', width=2, dash='dot'),
    marker=dict(size=6),
    hovertemplate='%{x}: %{y:.1f}%<extra>Non-AI</extra>',
))

fig.add_trace(go.Scatter(
    x=bay.index, y=bay['AI in Bay Area %'],
    name='AI companies', mode='lines+markers',
    line=dict(color=utils.COLORS['AI'], width=3),
    marker=dict(size=7),
    hovertemplate='%{x}: %{y:.1f}%<extra>AI</extra>',
))

fig.add_vline(x=2022, line_dash='dash', line_color='#CCCCCC', opacity=0.8)
fig.add_annotation(
    x=2022, y=95, text='ChatGPT launched', showarrow=False,
    font=dict(size=10, color='#aaa'), xanchor='left', xshift=6,
)
fig.add_annotation(
    x=last_year, y=ai_bay,
    text=f'{gap:+.0f} pts gap',
    showarrow=True, arrowhead=2, ax=50, ay=-25,
    font=dict(size=11, color=utils.COLORS['AI']),
    arrowcolor=utils.COLORS['AI'],
)

fig.update_layout(
    height=430,
    yaxis=dict(title='Share in Bay Area', range=[0, 100],
               ticksuffix='%', gridcolor='#F0F0F0'),
    xaxis=dict(title='YC batch year', dtick=1),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=20),
    hovermode='x unified',
)
st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------------------
# City map
# ---------------------------------------------------------------------------
st.markdown('---')
st.markdown('#### Where YC companies are based')

available_years = sorted(df['year'].dropna().unique().astype(int).tolist())
early_year = 2018 if 2018 in available_years else available_years[len(available_years) // 2]
map_year = st.radio('Year', [early_year, available_years[-1]], horizontal=True, key='geo_year')

city_stats = utils.compute_city_stats(df, year=map_year, top_n=20)

if not HAS_FOLIUM:
    st.warning('Install folium and streamlit-folium for the interactive map: '
               '`pip install folium streamlit-folium`')
    st.dataframe(city_stats, width="stretch", hide_index=True)
elif city_stats.empty:
    st.info('No city data available for this year.')
else:
    fmap = folium.Map(location=[32, -30], zoom_start=2, tiles='cartodbpositron')
    max_count = max(float(city_stats['n_companies'].max()), 1.0)

    for _, row in city_stats.iterrows():
        coords = CITY_COORDS.get(str(row['City']))
        if coords is None:
            continue
        lat, lon = coords
        radius = 5 + 24 * math.sqrt(float(row['n_companies']) / max_count)
        color  = _color_for_ai_pct(float(row['ai_pct']))
        popup  = (f"<b>{row['City']}</b><br>{row.get('Country', '')}<br>"
                  f"Companies: {int(row['n_companies'])}<br>AI share: {row['ai_pct']:.0f}%")
        folium.CircleMarker(
            location=[lat, lon], radius=radius,
            color=color, fill=True, fill_color=color,
            fill_opacity=0.72, weight=2,
            popup=folium.Popup(popup, max_width=260),
            tooltip=f"{row['City']} ({map_year})",
        ).add_to(fmap)

    st.caption('Orange = >60% AI share, amber = 35-60%, green = 15-35%, blue = <15%. '
               'Size = number of companies.')
    st_folium(fmap, width="stretch", height=450)

# ---------------------------------------------------------------------------
# Finding
# ---------------------------------------------------------------------------
first_year = int(bay.index.min())
ai_first    = bay.loc[first_year, 'AI in Bay Area %']
nonai_first = bay.loc[first_year, 'Non-AI in Bay Area %']
gap_first  = ai_first - nonai_first
gap_change = gap - gap_first
direction  = 'widened' if gap_change > 0 else 'narrowed'

utils.finding_box(
    f'<strong>AI companies are more Bay Area-concentrated than non-AI companies — '
    f'and that gap has {direction} over time.</strong><br>'
    f'In {last_year}, {ai_bay:.0f}% of AI companies were based in the Bay Area, '
    f'versus {nonai_bay:.0f}% of non-AI companies — a gap of +{gap:.0f} points. '
    f'In {first_year}, the same gap was {gap_first:+.0f} points '
    f'({ai_first:.0f}% AI vs {nonai_first:.0f}% non-AI). '
    f'While non-AI startups have gradually dispersed, AI startups have remained '
    f'concentrated in the Bay Area — suggesting that proximity to AI talent, '
    f'infrastructure, and capital still matters, even in the remote-work era.'
)

st.caption(
    '**Caveat:** YC has a known preference for Bay Area founders. However, '
    'the *gap* between AI and non-AI concentration cannot be attributed to '
    "YC's general preference, since both groups face the same selection process."
)
