"""
page3_answer.py -- Conclusion section rendered at the bottom of the single-page app.
"""

import streamlit as st
import utils


def render_conclusion(df):
    trend_share  = utils.compute_trend_share_yearly(df)
    ai_peak      = trend_share['AI'].max()
    past_max     = trend_share[utils.REFERENCE_TRENDS].max().max()
    multiple     = ai_peak / past_max

    coexistence  = utils.compute_ai_coexistence(df)
    saas_2025    = coexistence.loc[2025, 'AI in Enterprise SaaS']

    bay          = utils.compute_bay_area_concentration(df)
    bay_gap_2025 = bay.loc[2025, 'Gap']

    orange = utils.COLORS['AI']

    # -- Three finding cards -------------------------------------------------
    def card(label, value, desc):
        return (
            f"<div style='border-top:3px solid {orange};padding-top:14px;'>"
            f"<div style='font-size:11px;color:#888;letter-spacing:1.5px;"
            f"text-transform:uppercase;margin-bottom:6px;'>{label}</div>"
            f"<div style='font-size:34px;font-weight:700;color:#111;"
            f"margin-bottom:8px;'>{value}</div>"
            f"<div style='font-size:14px;color:#555;line-height:1.55;'>{desc}</div>"
            f"</div>"
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(card(
            "Magnitude", f"{multiple:.1f}x",
            f"AI exceeded every reference trend by {multiple:.1f}x "
            f"and has not plateaued."
        ), unsafe_allow_html=True)

    with c2:
        st.markdown(card(
            "Coexistence", f"{saas_2025:.0f}%",
            f"of Enterprise SaaS companies in 2025 are also AI companies -- "
            "up from 4% in 2014."
        ), unsafe_allow_html=True)

    with c3:
        st.markdown(card(
            "Geography", f"+{bay_gap_2025:.0f} pts",
            "Bay Area concentration gap between AI and non-AI companies in 2025, "
            "growing year over year."
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -- Question recall -----------------------------------------------------
    st.markdown(f"""
    <div style='font-size:18px;font-weight:500;color:#111;line-height:1.5;
                padding:24px 0;border-top:1px solid #E8E8E8;
                border-bottom:1px solid #E8E8E8;margin:8px 0 32px;'>
      Does AI's trend look like the trends that came before it?
    </div>
    """, unsafe_allow_html=True)

    # -- Answer block --------------------------------------------------------
    st.markdown(f"""
    <div style='border-left:3px solid {orange};padding:28px 36px;
                background:#FFF8F3;border-radius:2px;margin:0 0 32px;'>
      <p style='font-size:16px;line-height:1.8;color:#111;margin:0 0 16px;'>
        Past trends rose, sustained, and made room for the next.
      </p>
      <p style='font-size:16px;line-height:1.8;color:#111;margin:0;'>
        AI's trend is doing something different.<br>
        It does not replace past trends &mdash;
        <strong style='color:{orange};'>it appears inside them.</strong><br>
        It does not disperse &mdash;
        <strong style='color:{orange};'>it concentrates.</strong><br>
        It has not plateaued.
      </p>
      <p style='font-size:16px;line-height:1.8;color:#111;margin:16px 0 0;
                border-top:1px solid #FAD5C0;padding-top:16px;'>
        AI's trend reshapes other trends.<br>
        Past trends did not.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # -- Methodology (collapsed) ---------------------------------------------
    with st.expander("Methodology & caveats"):
        st.markdown("""
**Data**
HuggingFace `datahiveai/ycombinator-companies`, 5,080 companies, 2011-2025.
Filtered to years with >= 100 companies per batch.

**Trend selection criteria**
Each reference trend meets:
- >= 200 cumulative companies
- Peak >= 10%, sustained >= 5% for >= 3 years
- Has ended its growth phase

Selected reference trends: Enterprise SaaS (saas + b2b, Jaccard 0.33), Fintech, Developer Tools.

**Excluded from comparison**
- Consumer / Mobile (2005-2016): predates dataset coverage
- Crypto / Web3: fewer than 80 YC companies, insufficient scale
- Marketplace: peak 11.4% only in 2011, did not recur

**Methodological notes**
- No outcome data (funding, exits). This study measures concentration, not impact.
- Reference trends are not strictly orthogonal -- they reflect different facets of YC's tag
  taxonomy. Treated as historical references, not a mutually exclusive classification.
- YC's labeling is inconsistent: `ai` vs `artificial-intelligence` Jaccard = 0.09.
  We performed concept-level merging across 16 AI sub-tags.
- 2024-2025 companies have fewer tags on average (likely data lag), which may
  underestimate coexistence rates.
- YC has a known Bay Area preference; geographic findings should be understood
  as trends within YC's selection, not the broader ecosystem.
""")
