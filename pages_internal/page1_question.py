"""
P1 — The Question

Goal: Establish baseline. Show the four waves. Raise the research question.
"""

import streamlit as st
import plotly.graph_objects as go
import utils


def render(df):
    # ===== Title =====
    st.markdown(
        '<div class="main-title">YC at 20: Three Waves Before AI</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="subtitle">{len(df):,} companies, {df["year"].nunique()} batches '
        f'({df["year"].min()}–{df["year"].max()})</div>',
        unsafe_allow_html=True,
    )

    # ===== Introduction =====
    st.markdown("""
    Y Combinator is one of the earliest and most consistent sources of early-stage startup data.
    Across YC's two decades, several distinct waves have shaped its portfolio.

    In this study, we focus on **three representative waves** from the 2010s —
    **Enterprise SaaS, Fintech, and Developer Tools** — and compare them against the recent rise of **AI**.

    Our research question:
    """)

    st.markdown("""
    <div class="question-block">
    Does AI follow the shape of past waves, or does it represent a fundamentally different shift?
    </div>
    """, unsafe_allow_html=True)

    # ===== Main chart =====
    st.markdown("### Four waves, one anomaly")

    wave_share = utils.compute_wave_share_yearly(df)

    fig = go.Figure()

    for wave in utils.PAST_WAVES:
        fig.add_trace(go.Scatter(
            x=wave_share.index,
            y=wave_share[wave],
            name=wave,
            line=dict(color=utils.COLORS[wave], width=2, dash='dot'),
            mode='lines+markers',
            marker=dict(size=5),
            hovertemplate='%{x}: %{y:.1f}%<extra>' + wave + '</extra>',
        ))

    fig.add_trace(go.Scatter(
        x=wave_share.index,
        y=wave_share['AI'],
        name='AI',
        line=dict(color=utils.COLORS['AI'], width=4),
        mode='lines+markers',
        marker=dict(size=7),
        hovertemplate='%{x}: %{y:.1f}%<extra>AI</extra>',
    ))

    ai_peak_year = wave_share['AI'].idxmax()
    ai_peak_val = wave_share['AI'].max()
    saas_peak_year = wave_share['Enterprise SaaS'].idxmax()
    saas_peak_val = wave_share['Enterprise SaaS'].max()

    fig.add_annotation(
        x=ai_peak_year, y=ai_peak_val,
        text=f"<b>{ai_peak_val:.0f}%</b>",
        showarrow=False,
        yshift=18,
        font=dict(size=14, color=utils.COLORS['AI']),
    )
    fig.add_annotation(
        x=saas_peak_year, y=saas_peak_val,
        text=f"SaaS peak: {saas_peak_val:.0f}%",
        showarrow=True, arrowhead=2,
        ax=-60, ay=-30,
        font=dict(size=11, color=utils.COLORS['Enterprise SaaS']),
    )
    fig.add_vline(x=2022, line_dash="dash", line_color="gray", opacity=0.4)
    fig.add_annotation(
        x=2022, y=70, text="ChatGPT", showarrow=False,
        font=dict(size=10, color="gray"),
    )

    fig.update_layout(
        height=480,
        yaxis=dict(title="% of YC batch", range=[0, 75], ticksuffix='%'),
        xaxis=dict(title=None),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=40),
        hovermode='x unified',
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Lines may sum to >100% — a single company can belong to multiple waves "
        "(e.g., a fintech company that's also a SaaS company). This overlap is part of "
        "the question, not noise."
    )

    # ===== Closing =====
    utils.finding_box(
        "<strong>Past waves followed a familiar shape — rise, peak, decline.</strong><br>"
        "AI hasn't peaked. It is still climbing.<br><br>"
        "Is AI just a larger wave? Or is it something different?"
    )

    st.markdown(
        '<div style="text-align: right; color: #888; margin-top: 20px;">'
        '→ Continue to <em>The Evidence</em></div>',
        unsafe_allow_html=True,
    )
