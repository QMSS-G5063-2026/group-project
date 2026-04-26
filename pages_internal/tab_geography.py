"""
Tab -- Geography
Owner: Team Member C

Question: Does AI's geographic shape match past trends?

Deliverables:
- Main chart: Bay Area concentration over time -- AI line vs non-AI line
- Map: top-20 cities, toggle between 2018 and 2024
- 3 metric cards
- Finding callout + caveat note

Available from utils:
- utils.compute_bay_area_concentration(df) -> DataFrame
    index=year, cols=['AI in Bay Area %', 'Non-AI in Bay Area %', 'Gap']
- utils.compute_city_stats(df, year, top_n) -> DataFrame
    cols=['City', 'Country', 'n_companies', 'ai_pct']
- utils.COLORS

Required libraries (already in requirements.txt):
- plotly (line chart)
- folium + streamlit-folium (map)

Style rules:
- AI line: utils.COLORS['AI'] (#E6550D), width=3, solid
- Non-AI line: '#969696', width=2, dash='dot'
- Add fill='tonexty' between the two lines to emphasize the widening gap
- Map: CircleMarker per city; radius proportional to n_companies;
  color proportional to ai_pct (orange = high AI share)
- Use the df argument -- do not reload data

Tip for map geocoding:
  Maintain a hardcoded city -> (lat, lng) dict for the top-20 cities.
  This is faster and more reliable than live geocoding since top cities are stable.
"""

import streamlit as st
import plotly.graph_objects as go
import utils


def render(df):
    # -- Compute -------------------------------------------------------------
    bay = utils.compute_bay_area_concentration(df)

    ai_bay_2024    = bay.loc[2024, 'AI in Bay Area %']
    nonai_bay_2024 = bay.loc[2024, 'Non-AI in Bay Area %']
    gap_2024       = bay.loc[2024, 'Gap']

    # -- Metric cards --------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("AI companies in Bay Area (2024)", f"{ai_bay_2024:.0f}%")
    col2.metric("Non-AI companies in Bay Area (2024)", f"{nonai_bay_2024:.0f}%")
    col3.metric("Concentration gap", f"+{gap_2024:.0f} pts", "and growing")

    # -- Main chart ----------------------------------------------------------
    # TODO (Team Member C):
    # Draw a two-line Bay Area concentration chart:
    # 1. X-axis: year, Y-axis: 0-100%, ticksuffix='%'
    # 2. AI line: utils.COLORS['AI'], width=3
    # 3. Non-AI line: '#969696', width=2, dash='dot'
    # 4. Use fill='tonexty' to shade the gap region between the two lines
    #    (shade color: light orange at low opacity, e.g. rgba(230,85,13,0.08))
    # 5. Annotate the 2024 gap value (+N pts) at the right edge of the chart
    # 6. Hover: show both percentages and the gap at each year

    st.info("Team Member C: add the Bay Area concentration line chart here.")

    # -- Map -----------------------------------------------------------------
    st.markdown("---")
    st.markdown("#### Where YC companies are based")

    map_year = st.radio(
        "Year",
        [2018, 2024],
        horizontal=True,
        key='geo_year',
    )

    city_stats = utils.compute_city_stats(df, year=map_year, top_n=20)

    # TODO (Team Member C):
    # Draw a folium map of the top-20 cities:
    # 1. One CircleMarker per city
    # 2. Radius proportional to city_stats['n_companies'] (scale: radius = sqrt(n) * 1.5)
    # 3. Color proportional to city_stats['ai_pct']
    #    (use a colormap from gray to utils.COLORS['AI'])
    # 4. Tooltip: city name, n_companies, ai_pct
    # 5. Render with: from streamlit_folium import st_folium; st_folium(m, use_container_width=True)
    #
    # Hardcoded coordinates for the top-20 most common cities:
    # {
    #   'San Francisco': (37.774, -122.419), 'New York': (40.712, -74.006),
    #   'London': (51.507, -0.128), 'Mountain View': (37.386, -122.084),
    #   'Palo Alto': (37.441, -122.143), 'Seattle': (47.606, -122.332),
    #   'Boston': (42.360, -71.059), 'Austin': (30.267, -97.743),
    #   'Los Angeles': (34.052, -118.244), 'Chicago': (41.878, -87.630),
    #   'Toronto': (43.653, -79.383), 'Berlin': (52.520, 13.405),
    #   'Singapore': (1.352, 103.820), 'Bangalore': (12.972, 77.594),
    #   'Tel Aviv': (32.085, 34.781), 'Paris': (48.857, 2.347),
    #   'Mumbai': (19.076, 72.878), 'Sydney': (-33.869, 151.209),
    #   'Toronto': (43.653, -79.383), 'Denver': (39.739, -104.984),
    # }

    st.info(f"Team Member C: render the {map_year} city map (top-20 cities).")
    st.dataframe(city_stats, use_container_width=True, hide_index=True)

    # -- Finding -------------------------------------------------------------
    utils.finding_box(
        f"<strong>Remote work was expected to flatten startup geography.</strong><br>"
        f"Among AI companies, the opposite happened -- Bay Area concentration grew, "
        f"while non-AI companies dispersed more broadly. "
        f"The gap reached +{gap_2024:.0f} points in 2024 and continues to widen."
    )

    st.caption(
        "**Caveat:** YC has a known preference for Bay Area founders. However, "
        "the *gap* between AI and non-AI Bay Area concentration -- and its growth "
        "over time -- cannot be attributed to YC's general preference, since both "
        "groups are subject to the same selection process."
    )
