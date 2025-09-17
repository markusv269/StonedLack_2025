import streamlit as st
from config import CSS_PATH

def load_css():
    """Custom CSS laden"""
    with open(CSS_PATH) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)