"""
Tab 3 — Geography
Owner: 组员 C

Question: Does AI's geographic distribution match past waves?

Required deliverables:
- Main chart: Bay Area concentration over time (AI vs Non-AI, two lines)
- Sub-chart: Map showing top cities (toggle 2018 vs 2024)
- 3 metric cards
- Finding text + caveat

Available utils:
- utils.compute_bay_area_concentration(df) → DataFrame
- utils.compute_city_stats(df, year, top_n) → DataFrame
- utils.COLORS

Required libraries:
- plotly (line chart)
- folium + streamlit-folium (map)
  → both in requirements.txt

Style rules:
- AI line: utils.COLORS['AI'] (red), thick
- Non-AI line: gray, dashed
- Map: circle radius ∝ company count, color ∝ AI %
- Don't reload data
"""

import streamlit as st
import plotly.graph_objects as go
import utils


def render(df):
    st.markdown("### Geography: Did AI flatten the map, or re-concentrate it?")

    # ===== Compute =====
    bay = utils.compute_bay_area_concentration(df)

    # ===== Metrics =====
    ai_bay_2024 = bay.loc[2024, 'AI in Bay Area %']
    nonai_bay_2024 = bay.loc[2024, 'Non-AI in Bay Area %']
    gap_2024 = bay.loc[2024, 'Gap']

    col1, col2, col3 = st.columns(3)
    col1.metric("AI in Bay Area (2024)", f"{ai_bay_2024:.0f}%")
    col2.metric("Non-AI in Bay Area (2024)", f"{nonai_bay_2024:.0f}%")
    col3.metric("Concentration gap", f"+{gap_2024:.0f} pts", "and growing")

    # ===== Main chart =====
    # TODO 组员 C:
    # 画两线图：AI vs 非 AI 公司在 Bay Area 的占比
    # 1. X 轴 year, Y 轴 0-100%
    # 2. 红线 = AI, 灰线 = Non-AI
    # 3. 用 fill='tonexty' 把两条线之间的差距区域填色（强化"差距扩大"的视觉）

    st.info("👉 组员 C: 在这里画 Bay Area 集中度对比图")

    # ===== Map (left/right layout) =====
    st.markdown("---")
    st.markdown("#### Where YC companies are based")

    map_year = st.radio(
        "Year",
        [2018, 2024],
        horizontal=True,
        key='geo_year',
    )

    city_stats = utils.compute_city_stats(df, year=map_year, top_n=20)

    # TODO 组员 C:
    # 用 folium 画地图
    # 1. 每个城市一个 CircleMarker
    # 2. 半径 ∝ city_stats['n_companies']
    # 3. 颜色 ∝ city_stats['ai_pct']（用 colormap，红到灰）
    # 4. tooltip 显示城市名、公司数、AI%
    # 5. 用 streamlit_folium.st_folium() 渲染
    #
    # 注意：城市坐标需要 geocoding。可以：
    # (a) 用 geopy 实时 geocode（慢但准）
    # (b) 维护一个 city → (lat, lng) 字典（快但有限）
    # 推荐 (b)，因为 top 20 城市基本固定

    st.info(f"👉 组员 C: 这里画 {map_year} 年的地图（top 20 城市）")
    st.dataframe(city_stats, use_container_width=True, hide_index=True)

    # ===== Finding =====
    utils.finding_box(
        f"<strong>Remote work was expected to flatten startup geography.</strong><br>"
        f"Among AI companies, the opposite happened. Bay Area's share among AI "
        f"companies grew, while non-AI companies dispersed more broadly. "
        f"The gap reached +{gap_2024:.0f} points in 2024 and continues to widen."
    )

    # ===== Caveat =====
    st.caption(
        "**Caveat**: YC has a known preference for Bay Area founders. However, "
        "the *gap* between AI and non-AI Bay Area concentration — and its growth "
        "over time — cannot be explained by YC's general preference, since both "
        "groups are subject to the same selection."
    )
