"""
app.py -- entrypoint only. Defines navigation; no content here.

Run: streamlit run app.py
"""

import streamlit as st

pg = st.navigation([
    st.Page("pages/0_Overview.py", title="Overview"),
    st.Page("pages/1_Text.py",     title="01 Text"),
    st.Page("pages/2_Coexistence.py", title="02 Coexistence"),
    st.Page("pages/3_Geography.py",   title="03 Geography"),
])
pg.run()
