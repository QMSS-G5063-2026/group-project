"""
Tab -- Magnitude
Owner: Team Member A

Question: Is AI's peak within the historical range of YC trends?

Deliverables:
- Main chart: 4-trend yearly share comparison (larger, interactive, hoverable)
- 3 metric cards: AI peak, highest reference peak, multiple
- Finding callout below chart

Available from utils:
- utils.compute_trend_share_yearly(df) -> DataFrame (index=year, cols=trend names)
- utils.compute_trend_peaks(df) -> DataFrame (index=trend, cols=peak_pct/peak_year/total)
- utils.COLORS, utils.TREND_NAMES, utils.REFERENCE_TRENDS
- utils.finding_box(text) -> renders styled callout

Style rules:
- AI line: utils.COLORS['AI'], width=4, solid
- Reference trend lines: utils.COLORS[trend_name], width=2, dash='dot'
  (unlike the Section 01 overview, this chart uses actual colors per trend)
- Use Plotly only (no matplotlib)
- Max 2 interactive controls
- Use the df argument -- do not reload data
"""

import streamlit as st
import plotly.graph_objects as go
import utils


def render(df):
    # -- Compute -------------------------------------------------------------
    trend_share = utils.compute_trend_share_yearly(df)
    peaks = utils.compute_trend_peaks(df)

    ai_peak       = peaks.loc['AI', 'peak_pct']
    ref_peaks     = peaks.loc[utils.REFERENCE_TRENDS, 'peak_pct']
    past_max      = ref_peaks.max()
    past_max_trend = ref_peaks.idxmax()
    past_max_year  = peaks.loc[past_max_trend, 'peak_year']
    multiple       = ai_peak / past_max

    # -- Metric cards --------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("AI peak (2025)", f"{ai_peak:.1f}%")
    col2.metric("Highest reference peak", f"{past_max:.1f}%",
                f"{past_max_trend}, {int(past_max_year)}")
    col3.metric("Multiple", f"{multiple:.1f}x")

    # -- Main chart ----------------------------------------------------------
    # TODO (Team Member A):
    # Draw an interactive 4-trend share chart. This is the detailed version of
    # the overview chart shown in Section 01 -- make it larger and more interactive.
    #
    # Requirements:
    # 1. AI line: utils.COLORS['AI'], width=4, solid
    # 2. Reference trend lines: utils.COLORS[trend], width=2, dash='dot'
    #    Use actual trend colors (not gray) so each line is identifiable
    # 3. Y-axis: 0-80%, ticksuffix='%'; X-axis: year
    # 4. Hover: show exact percentage for all trends at each year
    # 5. Annotate AI peak value and the highest reference peak
    # 6. Add vertical line at 2022 labeled "ChatGPT"
    # Optional: checkbox to toggle individual reference trends on/off

    st.info("Team Member A: add the interactive Magnitude chart here.")

    # -- Finding -------------------------------------------------------------
    utils.finding_box(
        f"<strong>AI's magnitude is not within the historical range of YC trends.</strong><br>"
        f"It exceeds the highest reference peak ({past_max_trend}, {past_max:.0f}%) "
        f"by {multiple:.1f}x and shows no plateau."
    )
