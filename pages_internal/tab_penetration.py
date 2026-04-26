"""
Tab 2 — Penetration
Owner: 组员 B

Question: Is AI parallel to other waves, or absorbed into them?

Required deliverables:
- Main chart: AI penetration into each past wave, by year (3 lines)
- Sub-chart (in expander): tag co-occurrence network with year slider
- 3 metric cards
- Finding text below

Available utils:
- utils.compute_ai_penetration(df) → DataFrame
- utils.compute_cooccurrence(df, year, top_n, min_count) → (edges, nodes)
- utils.PAST_WAVES, utils.COLORS

Required libraries:
- plotly (main chart)
- networkx + pyvis (or plotly) for network visualization
  → networkx is in requirements.txt

Style rules:
- 3 lines should use distinct but harmonious colors
- Network: AI-related nodes should be visually highlighted (size or color)
- No more than 2 interactive controls in main view; year slider in expander OK
- Don't reload data
"""

import streamlit as st
import plotly.graph_objects as go
import utils


def render(df):
    st.markdown("### Penetration: Is AI parallel, or absorbed?")

    # ===== Compute =====
    penetration = utils.compute_ai_penetration(df)

    # ===== Metrics =====
    saas_2025 = penetration.loc[2025, 'AI in Enterprise SaaS']
    fintech_2025 = penetration.loc[2025, 'AI in Fintech']
    devtools_2025 = penetration.loc[2025, 'AI in Developer Tools']

    col1, col2, col3 = st.columns(3)
    col1.metric("AI in Enterprise SaaS (2025)", f"{saas_2025:.0f}%",
                "vs 4% in 2014")
    col2.metric("AI in Fintech (2025)", f"{fintech_2025:.0f}%")
    col3.metric("AI in Developer Tools (2025)", f"{devtools_2025:.0f}%")

    # ===== Main chart =====
    # TODO 组员 B:
    # 画三线图：AI 在每个 past wave 中的渗透率
    # 1. X 轴 year, Y 轴 0-100%
    # 2. 三条线分别是 'AI in Enterprise SaaS', 'AI in Fintech', 'AI in Developer Tools'
    # 3. 在 2022 年加竖线 "ChatGPT launched"
    # 4. 三条线都应该突出显示（不要任何一条是灰色，因为这一页就是讲渗透）

    st.info("👉 组员 B: 在这里画三线渗透图")

    # ===== Co-occurrence network (in expander) =====
    with st.expander("▾ Tag co-occurrence network (interactive)"):
        st.markdown(
            "Drag the year slider to see how AI's connections to other tags evolved."
        )

        year = st.slider(
            "Year",
            min_value=int(df['year'].min()),
            max_value=int(df['year'].max()),
            value=2025,
            key='penetration_year_slider',
        )

        edges, nodes = utils.compute_cooccurrence(df, year=year, top_n=30, min_count=5)

        # TODO 组员 B:
        # 用 plotly 或 pyvis 画共现网络
        # 1. 节点 = top 30 tags（来自 nodes dict）
        # 2. 节点大小 ∝ nodes[tag]['n_companies']
        # 3. 节点颜色 ∝ nodes[tag]['ai_pct']（红色 = AI 渗透高）
        # 4. 边 = edges 列表，宽度 ∝ edges[i]['count']
        # 5. 用 networkx 算 spring_layout 决定位置

        st.info(f"👉 组员 B: 这里画 {year} 年的共现网络（{len(edges)} 条边，{len(nodes)} 个节点）")

    # ===== Finding =====
    utils.finding_box(
        f"<strong>Past waves were independent sectors. AI is not.</strong><br>"
        f"By 2025, AI is absorbed into {saas_2025:.0f}% of Enterprise SaaS, "
        f"{fintech_2025:.0f}% of Fintech, and {devtools_2025:.0f}% of Developer Tools."
    )
