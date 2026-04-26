"""
Tab -- Coexistence
Owner: Team Member B

Question: Does AI exist alongside other trends, or inside them?

Deliverables:
- Main chart: AI coexistence rate in each reference trend by year (3 lines)
- Expander: tag co-occurrence network with year slider (2011-2025)
- 3 metric cards
- Finding callout below

Available from utils:
- utils.compute_ai_coexistence(df) -> DataFrame
    index=year, cols=['AI in Enterprise SaaS', 'AI in Fintech', 'AI in Developer Tools']
- utils.compute_cooccurrence(df, year, top_n, min_count) -> (edges, nodes)
- utils.REFERENCE_TRENDS, utils.COLORS

Required libraries (already in requirements.txt):
- plotly (main chart)
- networkx for spring_layout; pyvis or plotly for network rendering

Style rules:
- All 3 lines should be visually prominent -- no gray lines; use distinct colors
- Suggested: Enterprise SaaS blue (#3182BD), Fintech green (#31A354), DevTools teal
- Network nodes: size proportional to n_companies, color proportional to ai_pct
  (orange = high AI share)
- Max 2 interactive controls in main view; year slider inside expander is fine
- Use the df argument -- do not reload data
"""

import streamlit as st
import plotly.graph_objects as go
import utils


def render(df):
    # -- Compute -------------------------------------------------------------
    coexistence = utils.compute_ai_coexistence(df)

    saas_2025     = coexistence.loc[2025, 'AI in Enterprise SaaS']
    fintech_2025  = coexistence.loc[2025, 'AI in Fintech']
    devtools_2025 = coexistence.loc[2025, 'AI in Developer Tools']

    # -- Metric cards --------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("AI in Enterprise SaaS (2025)", f"{saas_2025:.0f}%", "vs 4% in 2014")
    col2.metric("AI in Fintech (2025)", f"{fintech_2025:.0f}%")
    col3.metric("AI in Developer Tools (2025)", f"{devtools_2025:.0f}%")

    # -- Main chart ----------------------------------------------------------
    # TODO (Team Member B):
    # Draw a 3-line coexistence chart:
    # 1. X-axis: year, Y-axis: 0-100%, ticksuffix='%'
    # 2. One line per column in the 'coexistence' DataFrame:
    #    'AI in Enterprise SaaS', 'AI in Fintech', 'AI in Developer Tools'
    # 3. Add a vertical line at 2022 labeled "ChatGPT launched"
    # 4. All three lines must be visually distinct (no gray); use utils.COLORS
    # 5. Hover shows exact coexistence % for each trend at each year

    st.info("Team Member B: add the 3-line coexistence chart here.")

    # -- Co-occurrence network (in expander) ---------------------------------
    with st.expander("Tag co-occurrence network (interactive)"):
        st.markdown(
            "Use the year slider to see how AI's tag connections evolved over time. "
            "Node size = number of companies. Node color = share of companies also tagged AI "
            "(orange = high AI coexistence)."
        )

        year = st.slider(
            "Year",
            min_value=int(df['year'].min()),
            max_value=int(df['year'].max()),
            value=2025,
            key='coexistence_year_slider',
        )

        edges, nodes = utils.compute_cooccurrence(df, year=year, top_n=30, min_count=5)

        # TODO (Team Member B):
        # Draw the co-occurrence network using Plotly or pyvis:
        # 1. Nodes = top-30 tags (from 'nodes' dict)
        # 2. Node size proportional to nodes[tag]['n_companies']
        # 3. Node color proportional to nodes[tag]['ai_pct']
        #    (use a sequential colorscale, e.g. Oranges; high = more AI overlap)
        # 4. Edge width proportional to edges[i]['count']
        # 5. Use networkx spring_layout to compute node positions
        # 6. Tooltip: tag name, n_companies, ai_pct

        st.info(
            f"Team Member B: render the {year} co-occurrence network "
            f"({len(edges)} edges, {len(nodes)} nodes)."
        )

    # -- Finding -------------------------------------------------------------
    utils.finding_box(
        f"<strong>Past trends coexisted as parallel sectors. AI does not.</strong><br>"
        f"By 2025, AI appears inside {saas_2025:.0f}% of Enterprise SaaS companies, "
        f"{fintech_2025:.0f}% of Fintech, and {devtools_2025:.0f}% of Developer Tools."
    )
