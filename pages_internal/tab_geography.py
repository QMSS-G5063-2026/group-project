"""
Tab -- Geography
Owner: Team Member C (Zhicheng Jiang)

Question: Does AI's geographic shape match past trends?

Deliverables:
- Main chart: Bay Area concentration over time -- AI line vs non-AI line
- Map: top-20 cities, toggle between 2018 and 2024
- 3 metric cards
- Finding callout + caveat note

Available from utils:
- utils.compute_bay_area_concentration(df) -> DataFrame
    index=year, cols=['AI in Bay Area %', 'Non-AI in Bay Area %', 'Gap']
    (values are already 0-100, not 0-1)
- utils.compute_city_stats(df, year, top_n) -> DataFrame
    cols=['City', 'Country', 'n_companies', 'ai_pct']  (ai_pct is 0-100)
- utils.COLORS
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


# ---------------------------------------------------------------------------
# Hardcoded city coordinates for top startup hubs
# ---------------------------------------------------------------------------
CITY_COORDS = {
    'San Francisco':     (37.7749, -122.4194),
    'Mountain View':     (37.3861, -122.0839),
    'Palo Alto':         (37.4419, -122.1430),
    'Menlo Park':        (37.4529, -122.1817),
    'Redwood City':      (37.4852, -122.2364),
    'San Mateo':         (37.5630, -122.3255),
    'Berkeley':          (37.8715, -122.2730),
    'Oakland':           (37.8044, -122.2712),
    'San Jose':          (37.3382, -121.8863),
    'Santa Clara':       (37.3541, -121.9552),
    'Sunnyvale':         (37.3688, -122.0363),
    'South San Francisco': (37.6547, -122.4077),
    'Los Angeles':       (34.0522, -118.2437),
    'New York':          (40.7128,  -74.0060),
    'Brooklyn':          (40.6782,  -73.9442),
    'Boston':            (42.3601,  -71.0589),
    'Seattle':           (47.6062, -122.3321),
    'Austin':            (30.2672,  -97.7431),
    'Chicago':           (41.8781,  -87.6298),
    'Miami':             (25.7617,  -80.1918),
    'Denver':            (39.7392, -104.9903),
    'Toronto':           (43.6532,  -79.3832),
    'Vancouver':         (49.2827, -123.1207),
    'London':            (51.5072,   -0.1276),
    'Paris':             (48.8566,    2.3522),
    'Berlin':            (52.5200,   13.4050),
    'Amsterdam':         (52.3676,    4.9041),
    'Zurich':            (47.3769,    8.5417),
    'Tel Aviv':          (32.0853,   34.7818),
    'Singapore':         ( 1.3521,  103.8198),
    'Bengaluru':         (12.9716,   77.5946),
    'Bangalore':         (12.9716,   77.5946),
    'Delhi':             (28.6139,   77.2090),
    'Mumbai':            (19.0760,   72.8777),
    'Sydney':            (-33.8688, 151.2093),
    'Lagos':             (  6.5244,   3.3792),
    'Nairobi':           ( -1.2921,  36.8219),
}


def _color_for_ai_pct(pct):
    """Folium marker color keyed to AI share percentage (0-100)."""
    if pct >= 60:
        return '#E6550D'  # orange -- very high AI share
    if pct >= 35:
        return '#F28E2B'  # amber
    if pct >= 15:
        return '#59A14F'  # green
    return '#4E79A7'       # blue -- low AI share


def render(df):
    # -- Compute -----------------------------------------------------------------
    bay = utils.compute_bay_area_concentration(df)

    last_year = int(bay.index.max())
    ai_bay    = bay.loc[last_year, 'AI in Bay Area %']
    nonai_bay = bay.loc[last_year, 'Non-AI in Bay Area %']
    gap       = bay.loc[last_year, 'Gap']

    # -- Metric cards ------------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric(f'AI companies in Bay Area ({last_year})',     f'{ai_bay:.0f}%')
    col2.metric(f'Non-AI companies in Bay Area ({last_year})', f'{nonai_bay:.0f}%')
    col3.metric('AI vs Non-AI gap', f'+{gap:.0f} pts',
                'AI more concentrated')

    # -- Main chart: Bay Area concentration over time ---------------------------
    st.markdown(
        '<div style="font-size:17px; font-weight:600; color:#111; margin-bottom:4px;">'
        'Bay Area share over time: AI vs. non-AI companies</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        'Shaded area = the growing gap between AI and non-AI Bay Area concentration. '
        'Both groups are drawn from the same YC-selected sample.'
    )

    fig = go.Figure()

    # Non-AI line first so fill='tonexty' on the AI line shades the gap region
    fig.add_trace(go.Scatter(
        x=bay.index,
        y=bay['Non-AI in Bay Area %'],
        name='Non-AI companies',
        mode='lines+markers',
        line=dict(color='#969696', width=2, dash='dot'),
        marker=dict(size=6),
        hovertemplate='%{x}: %{y:.1f}%<extra>Non-AI</extra>',
    ))

    # AI line -- shaded fill down to the Non-AI line
    fig.add_trace(go.Scatter(
        x=bay.index,
        y=bay['AI in Bay Area %'],
        name='AI companies',
        mode='lines+markers',
        line=dict(color=utils.COLORS['AI'], width=3),
        marker=dict(size=7),
        fill='tonexty',
        fillcolor='rgba(230,85,13,0.08)',
        hovertemplate='%{x}: %{y:.1f}%<extra>AI</extra>',
    ))

    # Annotate the gap at the last year
    fig.add_annotation(
        x=last_year, y=ai_bay,
        text=f'+{gap:.0f} pts gap',
        showarrow=True, arrowhead=2, ax=50, ay=-25,
        font=dict(size=11, color=utils.COLORS['AI']),
        arrowcolor=utils.COLORS['AI'],
    )

    fig.update_layout(
        height=430,
        yaxis=dict(
            title='Share in Bay Area',
            range=[0, 100],
            ticksuffix='%',
            gridcolor='#F0F0F0',
        ),
        xaxis=dict(title='YC batch year', dtick=1),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=20),
        hovermode='x unified',
    )

    st.plotly_chart(fig, width="stretch")

    # -- Map: top-20 cities -----------------------------------------------------
    st.markdown('<div style="margin-top:32px;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:17px; font-weight:600; color:#111; margin-bottom:4px;">'
        'Where are YC companies based?</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        'Top 20 cities by company count. Marker size = number of companies. '
        'Marker color = share of companies in that city also tagged AI.'
    )

    # Build year options dynamically -- pick an early comparison year and the latest year
    available_years = sorted(df['year'].dropna().unique().astype(int).tolist())
    early_year = 2018 if 2018 in available_years else available_years[len(available_years) // 2]
    latest_map_year = available_years[-1]
    map_year_options = sorted(set([early_year, latest_map_year]))

    map_year = st.radio(
        'Year',
        map_year_options,
        horizontal=True,
        key='geo_year',
    )

    city_stats = utils.compute_city_stats(df, year=map_year, top_n=20)

    if not HAS_FOLIUM:
        st.warning(
            'Install folium and streamlit-folium to see the interactive map: '
            '`pip install folium streamlit-folium`'
        )
        st.dataframe(city_stats, width="stretch", hide_index=True)

    elif city_stats.empty:
        st.info('No city data available for this year.')

    else:
        fmap = folium.Map(location=[32, -30], zoom_start=2, tiles='cartodbpositron')
        max_count = max(float(city_stats['n_companies'].max()), 1.0)

        for _, row in city_stats.iterrows():
            coords = CITY_COORDS.get(str(row['City']))
            if coords is None:
                continue  # skip cities not in our coords dict

            lat, lon = coords
            radius = 5 + 24 * math.sqrt(float(row['n_companies']) / max_count)
            color  = _color_for_ai_pct(float(row['ai_pct']))
            popup  = (
                f"<b>{row['City']}</b><br>"
                f"{row.get('Country', '')}<br>"
                f"Companies: {int(row['n_companies'])}<br>"
                f"AI share: {row['ai_pct']:.0f}%"
            )
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.72,
                weight=2,
                popup=folium.Popup(popup, max_width=260),
                tooltip=f"{row['City']} ({map_year})",
            ).add_to(fmap)

        # Color legend caption
        st.caption(
            'Marker color: orange = >60% AI share, amber = 35-60%, '
            'green = 15-35%, blue = <15%. Size = number of companies.'
        )
        st_folium(fmap, width="stretch", height=450)

    # -- Finding -----------------------------------------------------------------
    utils.finding_box(
        f'<strong>Remote work was expected to flatten startup geography. '
        f'For AI companies, the opposite happened.</strong><br>'
        f'In {last_year}, <strong>{ai_bay:.0f}%</strong> of AI companies were based '
        f'in the Bay Area, versus <strong>{nonai_bay:.0f}%</strong> of non-AI companies -- '
        f'a gap of <strong>+{gap:.0f} points</strong>. '
        f'While non-AI startups have gradually dispersed to other US cities and internationally, '
        f'AI startups have re-concentrated in the Bay Area. '
        f'Proximity to AI talent, infrastructure, and capital appears to outweigh '
        f'the freedom remote work provided.'
    )

    st.caption(
        '**Caveat:** YC has a known preference for Bay Area founders. However, '
        'the *gap* between AI and non-AI Bay Area concentration -- and its growth '
        'over time -- cannot be attributed to YC\'s general preference, since both '
        'groups are subject to the same selection process.'
    )
