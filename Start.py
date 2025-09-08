import streamlit as st
st.set_page_config(layout="wide")

def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")
# Load custom CSS
load_css("assets/styles.css")

# Streamlit UI
st.image("Pictures/SL_logo.png", width=150)
st.sidebar.write("by GoKingsGo, 2025")

pg = st.navigation(
    {
        "Start": [
            st.Page(page="VIEWS/START/0_start.py", title="Startseite", icon=":material/home:", default=True),
            # st.Page(page="VIEWS/START/1_hottakes.py", title="Hot Takes-Sammlung", icon=":material/whatshot:"),
            st.Page(page="VIEWS/START/4_universe.py", title="Das StonedLack Universum", icon=":material/planet:"),
            st.Page(page="VIEWS/START/5_sleeper_ecke.py", title="sleeper.com-Ecke", icon=":material/bedtime:"),
   ],
        "Redraft allgemein": [
            st.Page(page="VIEWS/REDRAFT/RED_info.py", title="Die Redraftligen", icon=":material/home:"),
            st.Page(page="VIEWS/REDRAFT/RED_Manager.py", title="Manager", icon=":material/groups:"),
        ],
        "SLR Ligen 2025" :[
            st.Page(page="VIEWS/REDRAFT/RED_drafts.py", title="Drafts", icon=":material/target:"),
            st.Page(page="VIEWS/REDRAFT/RED_adp_board.py", title="ADP Draftboard", icon=":material/table:"),
            st.Page(page="VIEWS/REDRAFT/RED_Matchups.py", title="Matchups", icon=":material/sports_football:"),
            st.Page(page="VIEWS/REDRAFT/RED_Wochenstatistiken.py", title="Wochenstatistiken", icon=":material/calendar_month:"),
        ],
        "SL Dynastys": [
            # st.Page(page="VIEWS/DYNASTY/DYN_info.py", title="Dynasty", icon=":material/construction:"),
            st.Page(page="VIEWS/DYNASTY/DYN_drafts.py", title="Drafts 2025", icon=":material/target:"),
            st.Page(page="VIEWS/DYNASTY/DYN_adp_board.py", title="Dynasty Draftboard 2025", icon=":material/table:"),
            # st.Page(page="VIEWS/DYNASTY/DYN_waitingroom.py", title="Dynasty Waiting Room", icon=":material/groups:"),
        ]
    }
)
pg.run()