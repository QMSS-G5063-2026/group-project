"""
app.py — Streamlit 主入口

运行: streamlit run app.py
"""

import streamlit as st
import utils

st.set_page_config(
    page_title="YC at 20: Three Waves Before AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

utils.apply_global_style()

# ===== 加载数据 =====
df = utils.load_data()

# ===== 顶部导航 =====
page = st.radio(
    "Navigation",
    ["1. The Question", "2. The Evidence", "3. The Answer"],
    horizontal=True,
    label_visibility="collapsed",
)

st.divider()

# ===== 路由 =====
if page == "1. The Question":
    from pages_internal import page1_question
    page1_question.render(df)

elif page == "2. The Evidence":
    st.markdown('<div class="main-title">Three measurements, one answer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">If AI is just a larger wave, it should resemble past waves '
        'across multiple dimensions. We test this on three independent measurements.</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["Scale", "Penetration", "Geography"])

    with tab1:
        from pages_internal import tab_scale
        tab_scale.render(df)

    with tab2:
        from pages_internal import tab_penetration
        tab_penetration.render(df)

    with tab3:
        from pages_internal import tab_geography
        tab_geography.render(df)

elif page == "3. The Answer":
    from pages_internal import page3_answer
    page3_answer.render(df)
