import streamlit as st

def metric_box(label, value):
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="label">{label}</div>  
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
)