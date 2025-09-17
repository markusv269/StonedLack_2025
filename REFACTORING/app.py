import streamlit as st
from ui.styles import load_css
from config import LOGO_PATH

# Seiten-Imports
from views._0_start import _0_start
# from views._1_redraft import ...
# from views._2_dynasty import ...

# ------------------ CONFIG ------------------
st.set_page_config(layout="wide")
load_css()

# Logo + Sidebar
st.image(LOGO_PATH, width=150)
st.sidebar.write("by GoKingsGo, 2025")

# ------------------ NAVIGATION ------------------
pages = {
    "Start": {
        "🏠 Startseite": _0_start,
    },
    "Redraft allgemein": {
        "📊 Die Redraftligen": None,
        "👤 Manager": None,
    },
    "SLR Ligen 2025": {
        "📝 Drafts": None,
        "📈 ADP Draftboard": None,
        "⚡ Matchups": None,
    },
    "SL Dynastys": {
        "📝 Drafts 2025": None,
        "📈 Dynasty Draftboard 2025": None,
    }
}

# Session-State für aktive Seite
if "active_page" not in st.session_state:
    st.session_state.active_page = list(pages["Start"].keys())[0]

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")

for category, subpages in pages.items():
    st.sidebar.markdown(f"### {category}")
    for title, module in subpages.items():
        # Button = klickbar
        if st.sidebar.button(title, key=title):
            st.session_state.active_page = title

# --- CSS Styling ---
st.markdown(
    """
    <style>
    .stButton button {
        width: 100%;
        text-align: left;
        border-radius: 8px;
        margin-bottom: 4px;
    }
    .stButton button:hover {
        background-color: #444 !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Seite rendern ---
for category, subpages in pages.items():
    for title, module in subpages.items():
        if title == st.session_state.active_page and module is not None:
            module.app()
