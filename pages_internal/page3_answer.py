"""
P3 — The Answer

Goal: Synthesize the three findings. Answer the research question.
"""

import streamlit as st
import utils


def render(df):
    st.markdown(
        '<div class="main-title">The Answer</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtitle">Three measurements. One conclusion.</div>',
        unsafe_allow_html=True,
    )

    # ===== Findings recap =====
    st.markdown("### Three findings")

    wave_share = utils.compute_wave_share_yearly(df)
    ai_peak = wave_share['AI'].max()
    past_max = wave_share[utils.PAST_WAVES].max().max()
    multiple = ai_peak / past_max

    penetration = utils.compute_ai_penetration(df)
    saas_2025 = penetration.loc[2025, 'AI in Enterprise SaaS']

    bay = utils.compute_bay_area_concentration(df)
    bay_gap_2025 = bay.loc[2025, 'Gap']

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"<div style='border-top: 3px solid {utils.COLORS['AI']}; padding-top: 12px;'>"
            f"<div style='font-size: 11px; color: #888; letter-spacing: 1px; "
            f"text-transform: uppercase;'>Scale</div>"
            f"<div style='font-size: 32px; font-weight: 600; margin: 8px 0;'>"
            f"{multiple:.1f}×</div>"
            f"<div style='color: #555; font-size: 14px; line-height: 1.5;'>"
            f"AI peak ({ai_peak:.0f}%) exceeds the highest past wave "
            f"({past_max:.0f}%) by {multiple:.1f}×.</div></div>",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"<div style='border-top: 3px solid {utils.COLORS['AI']}; padding-top: 12px;'>"
            f"<div style='font-size: 11px; color: #888; letter-spacing: 1px; "
            f"text-transform: uppercase;'>Penetration</div>"
            f"<div style='font-size: 32px; font-weight: 600; margin: 8px 0;'>"
            f"{saas_2025:.0f}%</div>"
            f"<div style='color: #555; font-size: 14px; line-height: 1.5;'>"
            f"of Enterprise SaaS companies in 2025 are also AI companies. "
            f"Up from 4% in 2014.</div></div>",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"<div style='border-top: 3px solid {utils.COLORS['AI']}; padding-top: 12px;'>"
            f"<div style='font-size: 11px; color: #888; letter-spacing: 1px; "
            f"text-transform: uppercase;'>Geography</div>"
            f"<div style='font-size: 32px; font-weight: 600; margin: 8px 0;'>"
            f"+{bay_gap_2025:.0f} pts</div>"
            f"<div style='color: #555; font-size: 14px; line-height: 1.5;'>"
            f"Bay Area concentration gap between AI and non-AI companies in 2025. "
            f"Growing year over year.</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ===== Question recall =====
    st.markdown("""
    <div class="question-block">
    Does AI follow the shape of past waves, or does it represent something different?
    </div>
    """, unsafe_allow_html=True)

    # ===== Answer =====
    st.markdown("""
    <div style='background: #FAFAF8; padding: 32px 40px; margin: 32px 0;
                border-radius: 8px; border-left: 4px solid #D85A30;'>
    <p style='font-size: 17px; line-height: 1.7; color: #1A1A1A; margin-bottom: 16px;'>
    Past waves were <strong>sectors</strong> — defined by industry, business model, or function.
    Bounded. Peaking. Eventually fading.
    </p>
    <p style='font-size: 17px; line-height: 1.7; color: #1A1A1A; margin-bottom: 0;'>
    AI is not a sector.<br>
    It is a <strong>dimension</strong> — one that cuts across them all.
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ===== Methodology expander =====
    with st.expander("▾ Methodology & caveats"):
        st.markdown("""
**Data**
HuggingFace `datahiveai/ycombinator-companies`, 5,080 companies, 2011–2025.
Filtered to years with ≥100 companies.

**Wave selection**
Three representative past waves chosen for comparison with AI:
- **Enterprise SaaS** (saas + b2b) — merged via Jaccard similarity (0.33)
- **Fintech** (fintech) — independent
- **Developer Tools** (developer-tools) — independent

Each wave meets three criteria: industry recognition (per YC's own RFS),
≥200 cumulative companies, peak share ≥10% sustained for ≥3 years.

**Excluded from comparison**
- *Consumer / Mobile internet (2005–2016)* — predates dataset coverage.
- *Crypto / Web3* — fewer than 80 companies in YC's portfolio (per YC's own RFS),
  insufficient scale within our data.
- *Marketplace* — peak 11.4% only in 2011, did not recur.

**Methodological limitations**
- We have **no outcome data** (funding, valuation, exits). This study measures
  concentration, not impact.
- The four waves are **not orthogonal** — they reflect different dimensions
  (business model, industry, function, technology) in YC's tag taxonomy.
  This is not noise; it is precisely the structural feature that distinguishes AI.
- YC's labeling is inconsistent: `ai` vs `artificial-intelligence` Jaccard = 0.09.
  We performed concept-level merging across 16 AI sub-tags.
- 2024–2025 companies have fewer tags on average (likely a data lag), which may
  slightly underestimate cross-wave penetration.
- YC has a known Bay Area preference; geographic findings should be understood
  as "trends within YC's selection."
""")
