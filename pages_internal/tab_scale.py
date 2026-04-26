"""
Tab 1 — Scale
Owner: 组员 A

Question: Does AI's scale fit the historical range of YC waves?

Required deliverables:
- Main chart: 4 waves' yearly share comparison (similar to P1 but more interactive)
- 3 metric cards: AI peak, past max, multiple
- Finding text below

Available utils:
- utils.compute_wave_share_yearly(df) → DataFrame
- utils.compute_wave_peaks(df) → DataFrame
- utils.COLORS, utils.WAVE_NAMES, utils.PAST_WAVES
- utils.finding_box(text) → renders styled box

Style rules:
- AI uses utils.COLORS['AI'] (the orange-red)
- Past waves use utils.COLORS[wave_name] (gray variants)
- Use plotly, not matplotlib
- No more than 2 interactive controls
- Don't reload data — use the df argument
"""

import streamlit as st
import plotly.graph_objects as go
import utils


def render(df):
    st.markdown("### Scale: Is AI within the historical range?")

    # ===== Compute =====
    wave_share = utils.compute_wave_share_yearly(df)
    peaks = utils.compute_wave_peaks(df)

    ai_peak = peaks.loc['AI', 'peak_pct']
    past_max = peaks.loc[utils.PAST_WAVES, 'peak_pct'].max()
    past_max_wave = peaks.loc[utils.PAST_WAVES, 'peak_pct'].idxmax()
    past_max_year = peaks.loc[past_max_wave, 'peak_year']
    multiple = ai_peak / past_max

    # ===== Metric cards =====
    col1, col2, col3 = st.columns(3)
    col1.metric("AI peak (2025)", f"{ai_peak:.1f}%")
    col2.metric("Highest past wave peak", f"{past_max:.1f}%",
                f"{past_max_wave}, {past_max_year}")
    col3.metric("Multiple", f"{multiple:.1f}×")

    # ===== Main chart =====
    # TODO 组员 A:
    # 画一张 4 wave 占比时间序列图，要求：
    # 1. AI 用粗红线 (width=4)，past waves 用细虚线 (width=2, dash='dot')
    # 2. Y 轴 0-75%，X 轴年份
    # 3. hover 显示具体百分比
    # 4. 在 AI peak 和 past peak 处加注释
    # 5. 用 utils.COLORS 配色
    #
    # 提示：参考 page1_question.py 里的图，但你可以加交互
    # 比如让用户 toggle 显示哪些 wave，或切换 Y 轴最大值

    st.info("👉 组员 A: 在这里画主图")

    # ===== Finding =====
    utils.finding_box(
        f"<strong>AI's scale is not within the historical range of YC waves.</strong><br>"
        f"It exceeds the previous maximum ({past_max_wave}, {past_max:.0f}%) by {multiple:.1f}×, "
        f"and shows no peak."
    )
