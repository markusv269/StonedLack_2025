import streamlit as st
st.set_page_config(layout="wide")
from tools.methods import (
    load_matchups, load_players, load_rosters, load_users, get_matchup_results
)
from config import SCORINGSETTINGS

# Session State Initialisierung
@st.cache_data
def initialize_data():
    return {
        "userdf": load_users(),
        "matchupsdf": None,
        "rostersdf": load_rosters(),
        "playersdf": None,
        "playersdict": None,
        "matchesdf": None,
        "scoring": SCORINGSETTINGS,
        "auth": None
    }

if "session_data" not in st.session_state:
    st.session_state["session_data"] = initialize_data()

# Matchups mit Nutzernamen verknüpfen
if st.session_state["session_data"]["matchupsdf"] is None:
    userdf = st.session_state["session_data"]["userdf"]
    matchupsdf = load_matchups().merge(
        userdf[['league_id', 'roster_id', 'display_name', 'league_name']],
        on=['league_id', 'roster_id'],
        how='left'
    )
    st.session_state["session_data"]["matchupsdf"] = matchupsdf

# Spieler laden
if st.session_state["session_data"]["playersdf"] is None:
    playersdf, playersdict = load_players()
    st.session_state["session_data"].update({
        "playersdf": playersdf,
        "playersdict": playersdict
    })

# Matchup-Ergebnisse berechnen
if st.session_state["session_data"]["matchesdf"] is None:
    st.session_state["session_data"]["matchesdf"] = get_matchup_results(
        matchdf=st.session_state["session_data"]["matchupsdf"],
        userdf=st.session_state["session_data"]["userdf"]
    )

# Streamlit UI
st.image("Pictures/SL_logo.png", width=150)
st.sidebar.write("by GoKingsGo, 2025")

if st.session_state["session_data"]["auth"] is None:
    st.session_state["session_data"]["auth"] = False

login_data = st.secrets["login"]["login"]
st.sidebar.subheader("Adminbereich")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password", placeholder=None)
if st.sidebar.button("Login"):
    if username in login_data and login_data[username] == password:
        st.sidebar.success("Login erfolgreich!")
        st.session_state["session_data"]["auth"] = True            
    else:
        st.sidebar.error("Falsche Zugangsdaten!")
if st.sidebar.button("Logout"):
    st.session_state["session_data"]["auth"] = False  

# Navigation
if st.session_state["session_data"]["auth"] == True:
        pg = st.navigation(
        {
            "Start": [
                st.Page(page="VIEWS/START/0_start.py", title="Das StonedLack Universum", icon=":material/home:", default=True),
                st.Page(page="VIEWS/START/1_hottakes.py", title="Hot Takes-Sammlung", icon=":material/whatshot:"),
                st.Page(page="VIEWS/START/2_champofchamps copy.py", title="Champ of Champs", icon=":material/trophy:"),
                st.Page(page="VIEWS/START/3_coc_spiel.py", title="CoC Tippabgabe", icon=":material/casino:"),
                st.Page(page="VIEWS/START/5_sleeper_ecke.py", title="Sleeper Ecke", icon=":material/bedtime:")
            ],
            "Redraft": [
                st.Page(page="VIEWS/REDRAFT/RED_slr2025.py", title="SLR2025 Anmeldung", icon=":material/login:"),
                st.Page(page="VIEWS/REDRAFT/RED_slr2025_status.py", title="SLR2025 Anmeldestatus", icon=":material/download_done:"),
                st.Page(page="VIEWS/REDRAFT/RED_info.py", title="Die Redraftligen", icon=":material/home:"),
                st.Page(page="VIEWS/REDRAFT/RED_uebersicht.py", title="Ligenübersicht", icon=":material/layers:"),
                st.Page(page="VIEWS/REDRAFT/RED_alte_Redrafts.py", title="Send your old SLR", icon=":material/send:"),
                st.Page(page="VIEWS/REDRAFT/RED_Wochenstatistiken.py", title="Wochenstatistiken", icon=":material/calendar_month:"),
                st.Page(page="VIEWS/REDRAFT/RED_Wochenkategorien.py", title="Wochenkategorien", icon=":material/bar_chart:"),
                st.Page(page="VIEWS/REDRAFT/RED_Matchups.py", title="Matchups", icon=":material/sports_football:"),
                st.Page(page="VIEWS/REDRAFT/RED_Manager.py", title="Manager", icon=":material/groups:"),
                st.Page(page="VIEWS/REDRAFT/RED_drafts.py", title="Drafts", icon=":material/target:")
            ],
            "Dynasty": [
                st.Page(page="VIEWS/DYNASTY/DYN_info.py", title="Dynasty", icon=":material/construction:"),
                st.Page(page="VIEWS/DYNASTY/DYN_drafts.py", title="Drafts", icon=":material/target:")
            ]
        }
    )
else:
    pg = st.navigation(
    {
        "Start": [
            st.Page(page="VIEWS/START/0_start.py", title="Das StonedLack Universum", icon=":material/home:", default=True),
            st.Page(page="VIEWS/START/1_hottakes.py", title="Hot Takes-Sammlung", icon=":material/whatshot:"),
            st.Page(page="VIEWS/START/2_champofchamps copy.py", title="Champ of Champs", icon=":material/trophy:"),
            st.Page(page="VIEWS/START/4_universe.py", title="Das Universum", icon=":material/planet:"),
            st.Page(page="VIEWS/START/5_sleeper_ecke.py", title="Sleeper Ecke", icon=":material/bedtime:")
        ],
        "Redraft": [
            st.Page(page="VIEWS/REDRAFT/RED_info.py", title="Die Redraftligen", icon=":material/home:"),
            st.Page(page="VIEWS/REDRAFT/RED_uebersicht.py", title="Ligenübersicht", icon=":material/layers:"),
            st.Page(page="VIEWS/REDRAFT/RED_alte_Redrafts.py", title="Send your old SLR", icon=":material/send:"),
            st.Page(page="VIEWS/REDRAFT/RED_Wochenstatistiken.py", title="Wochenstatistiken", icon=":material/calendar_month:"),
            st.Page(page="VIEWS/REDRAFT/RED_Wochenkategorien.py", title="Wochenkategorien", icon=":material/bar_chart:"),
            st.Page(page="VIEWS/REDRAFT/RED_Matchups.py", title="Matchups", icon=":material/sports_football:"),
            st.Page(page="VIEWS/REDRAFT/RED_Manager.py", title="Manager", icon=":material/groups:"),
            st.Page(page="VIEWS/REDRAFT/RED_drafts.py", title="Drafts", icon=":material/target:")
        ],
        "Dynasty": [
            st.Page(page="VIEWS/DYNASTY/DYN_info.py", title="Dynasty", icon=":material/construction:"),
            st.Page(page="VIEWS/DYNASTY/DYN_drafts.py", title="Drafts", icon=":material/target:")
        ]
    })
pg.run()