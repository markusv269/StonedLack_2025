import streamlit as st
import requests
import pandas as pd
import urllib.parse

# --------------------------------------------------
# Team Mapping: Kürzel → Name + Farbe
# --------------------------------------------------
TEAM_INFO = {
    "ARI": {"name": "Arizona Cardinals", "color": "#97233F"},
    "ATL": {"name": "Atlanta Falcons", "color": "#A71930"},
    "BAL": {"name": "Baltimore Ravens", "color": "#241773"},
    "BUF": {"name": "Buffalo Bills", "color": "#00338D"},
    "CAR": {"name": "Carolina Panthers", "color": "#0085CA"},
    "CHI": {"name": "Chicago Bears", "color": "#0B162A"},
    "CIN": {"name": "Cincinnati Bengals", "color": "#FB4F14"},
    "CLE": {"name": "Cleveland Browns", "color": "#311D00"},
    "DAL": {"name": "Dallas Cowboys", "color": "#041E42"},
    "DEN": {"name": "Denver Broncos", "color": "#FB4F14"},
    "DET": {"name": "Detroit Lions", "color": "#0076B6"},
    "GB":  {"name": "Green Bay Packers", "color": "#203731"},
    "HOU": {"name": "Houston Texans", "color": "#03202F"},
    "IND": {"name": "Indianapolis Colts", "color": "#002C5F"},
    "JAX": {"name": "Jacksonville Jaguars", "color": "#006778"},
    "KC":  {"name": "Kansas City Chiefs", "color": "#E31837"},
    "LV":  {"name": "Las Vegas Raiders", "color": "#000000"},
    "LAC": {"name": "Los Angeles Chargers", "color": "#002A5E"},
    "LAR": {"name": "Los Angeles Rams", "color": "#003594"},
    "MIA": {"name": "Miami Dolphins", "color": "#008E97"},
    "MIN": {"name": "Minnesota Vikings", "color": "#4F2683"},
    "NE":  {"name": "New England Patriots", "color": "#002244"},
    "NO":  {"name": "New Orleans Saints", "color": "#D3BC8D"},
    "NYG": {"name": "New York Giants", "color": "#0B2265"},
    "NYJ": {"name": "New York Jets", "color": "#125740"},
    "PHI": {"name": "Philadelphia Eagles", "color": "#004C54"},
    "PIT": {"name": "Pittsburgh Steelers", "color": "#FFB612"},
    "SEA": {"name": "Seattle Seahawks", "color": "#002244"},
    "SF":  {"name": "San Francisco 49ers", "color": "#AA0000"},
    "TB":  {"name": "Tampa Bay Buccaneers", "color": "#D50A0A"},
    "TEN": {"name": "Tennessee Titans", "color": "#0C2340"},
    "WAS": {"name": "Washington Commanders", "color": "#5A1414"},
}

# --------------------------------------------------
# Caching: Logos und API
# --------------------------------------------------
@st.cache_data
def get_team_logo(team: str) -> str:
    return f"https://static.www.nfl.com/t_q-best/league/api/clubs/logos/{team}.svg" if team in TEAM_INFO else "https://www.thesportsdb.com/images/media/league/badge/g85fqz1662057187.png"

@st.cache_data
def get_league_info(league_id):
    return requests.get(f"https://api.sleeper.app/v1/league/{league_id}").json()

@st.cache_data
def get_rosters(league_id):
    return requests.get(f"https://api.sleeper.app/v1/league/{league_id}/rosters").json()

@st.cache_data
def get_users(league_id):
    return requests.get(f"https://api.sleeper.app/v1/league/{league_id}/users").json()

@st.cache_data
def get_players():
    return requests.get("https://api.sleeper.app/v1/players/nfl").json()

# --------------------------------------------------
# Layout & Einstellungen
# --------------------------------------------------
st.title("🏈 Fantasy League Übersicht")
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        font-size: 12px;
    }
    div[data-testid="metric-container"] > label {
        font-size: 4px;
    }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
param_league_id = params.get("league_id")
param_roster_id = params.get("roster_id")

league_id = st.text_input("Gib die League ID ein", value=param_league_id or "")

if league_id:
    league = get_league_info(league_id)
    if not league:
        st.error("❌ Keine Liga gefunden.")
        st.stop()

    st.subheader("🔧 Ligaeinstellungen")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Name", league.get("name"), border=True)
    with col2:
        def typ_to_word(typ):
            return {0: "Redraft", 1: "Keeper", 2: "Dynasty"}.get(typ, "Unbekannt")
        st.metric("Typ", typ_to_word(league.get("settings", {}).get("type")), border=True)
    with col3:
        st.metric("Teams", league.get("settings", {}).get("num_teams", "n/a"), border=True)

    rosters = get_rosters(league_id)
    users = get_users(league_id)
    user_map = {u["user_id"]: u.get("display_name", "Unbekannt") for u in users}
    options = {
        r["roster_id"]: user_map.get(r.get("owner_id"), f"Roster {r['roster_id']}")
        for r in rosters
    }

    selected_roster = st.selectbox("Wähle ein Team", options.keys(), format_func=lambda x: options[x], index=0 if not param_roster_id else list(options.keys()).index(int(param_roster_id)))
    selected = next((r for r in rosters if r["roster_id"] == selected_roster), None)

    if selected:
        players_data = get_players()
        starters = selected.get("starters", [])
        bench = [p for p in selected.get("players", []) if p and p not in starters]

        def format_player(p_id):
            p = players_data.get(p_id, {})
            team = p.get("team")
            return {
                "Name": p.get("full_name", p_id),
                "Pos": p.get("position", "—"),
                "Team": TEAM_INFO.get(team, {}).get("name", team),
                "Logo": get_team_logo(team),
                "Headshot": f"https://sleepercdn.com/content/nfl/players/{p_id}.jpg"
            }

        with st.expander("📋 Roster-Details", expanded=False):
            st.markdown("### 🔥 Starter")
            for row in [format_player(pid) for pid in starters if pid]:
                cols = st.columns([1,1,1,1,5])
                cols[0].image(row["Headshot"], width=50)
                cols[1].image(row["Logo"], width=30)
                cols[2].markdown(f"**{row['Name']}**")
                cols[3].markdown(row["Pos"])

            st.markdown("### 🧊 Bench")

            # 1. Positions-Reihenfolge definieren
            position_order = ["QB", "RB", "WR", "TE", "K", "DEF", "LB", "DB", "DL"]

            # 2. Formatierte Bench-Spieler holen und sortieren
            formatted_bench = [format_player(pid) for pid in bench if pid]
            formatted_bench.sort(key=lambda x: position_order.index(x["Pos"]) if x["Pos"] in position_order else 99)

            # 3. Darstellung
            for row in formatted_bench:
                cols = st.columns([1,1,1,1,5])
                cols[0].image(row["Headshot"], width=50)
                cols[1].image(row["Logo"], width=30)
                cols[2].markdown(f"**{row['Name']}**")
                cols[3].markdown(row["Pos"])

        st.markdown("---")
        st.markdown("### 📤 Teilbarer Link")
        share_url = f"https://stonedlack-2025.streamlit.app/showleague?{urllib.parse.urlencode({'league_id': league_id, 'roster_id': selected_roster})}"
        st.text_input("🔗 Link", value=share_url)



# import streamlit as st
# import streamlit.components.v1 as components
# import requests
# import pandas as pd
# import urllib.parse

# # --------------------------------------------------
# # Team Mapping: Kürzel → Name + Farbe
# # --------------------------------------------------
# TEAM_INFO = {
#     "ARI": {"name": "Arizona Cardinals", "color": "#97233F"},
#     "ATL": {"name": "Atlanta Falcons", "color": "#A71930"},
#     "BAL": {"name": "Baltimore Ravens", "color": "#241773"},
#     "BUF": {"name": "Buffalo Bills", "color": "#00338D"},
#     "CAR": {"name": "Carolina Panthers", "color": "#0085CA"},
#     "CHI": {"name": "Chicago Bears", "color": "#0B162A"},
#     "CIN": {"name": "Cincinnati Bengals", "color": "#FB4F14"},
#     "CLE": {"name": "Cleveland Browns", "color": "#311D00"},
#     "DAL": {"name": "Dallas Cowboys", "color": "#041E42"},
#     "DEN": {"name": "Denver Broncos", "color": "#FB4F14"},
#     "DET": {"name": "Detroit Lions", "color": "#0076B6"},
#     "GB":  {"name": "Green Bay Packers", "color": "#203731"},
#     "HOU": {"name": "Houston Texans", "color": "#03202F"},
#     "IND": {"name": "Indianapolis Colts", "color": "#002C5F"},
#     "JAX": {"name": "Jacksonville Jaguars", "color": "#006778"},
#     "KC":  {"name": "Kansas City Chiefs", "color": "#E31837"},
#     "LV":  {"name": "Las Vegas Raiders", "color": "#000000"},
#     "LAC": {"name": "Los Angeles Chargers", "color": "#002A5E"},
#     "LAR": {"name": "Los Angeles Rams", "color": "#003594"},
#     "MIA": {"name": "Miami Dolphins", "color": "#008E97"},
#     "MIN": {"name": "Minnesota Vikings", "color": "#4F2683"},
#     "NE":  {"name": "New England Patriots", "color": "#002244"},
#     "NO":  {"name": "New Orleans Saints", "color": "#D3BC8D"},
#     "NYG": {"name": "New York Giants", "color": "#0B2265"},
#     "NYJ": {"name": "New York Jets", "color": "#125740"},
#     "PHI": {"name": "Philadelphia Eagles", "color": "#004C54"},
#     "PIT": {"name": "Pittsburgh Steelers", "color": "#FFB612"},
#     "SEA": {"name": "Seattle Seahawks", "color": "#002244"},
#     "SF":  {"name": "San Francisco 49ers", "color": "#AA0000"},
#     "TB":  {"name": "Tampa Bay Buccaneers", "color": "#D50A0A"},
#     "TEN": {"name": "Tennessee Titans", "color": "#0C2340"},
#     "WAS": {"name": "Washington Commanders", "color": "#5A1414"},
# }

# # --------------------------------------------------
# # Caching: Logos
# # --------------------------------------------------
# @st.cache_data
# def get_team_logo(team: str) -> str:
#     if team in TEAM_INFO:
#         return f"https://static.www.nfl.com/t_q-best/league/api/clubs/logos/{team}.svg"
#     else:
#         return "https://www.thesportsdb.com/images/media/league/badge/g85fqz1662057187.png"

# # --------------------------------------------------
# # API Funktionen
# # --------------------------------------------------
# @st.cache_data
# def get_league_info(league_id):
#     url = f"https://api.sleeper.app/v1/league/{league_id}"
#     return requests.get(url).json()

# @st.cache_data
# def get_rosters(league_id):
#     url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
#     return requests.get(url).json()

# @st.cache_data
# def get_players():
#     url = "https://api.sleeper.app/v1/players/nfl"
#     return requests.get(url).json()

# # --------------------------------------------------
# # Streamlit Layout
# # --------------------------------------------------
# # st.set_page_config(layout="wide")
# st.title("🏈 Fantasy League Übersicht")
# st.markdown("""
#     <style>
#     div[data-testid="metric-container"] {
#         font-size: 12px;
#     }
#     div[data-testid="metric-container"] > label {
#         font-size: 4px;
#     }
#     </style>
# """, unsafe_allow_html=True)
# # Eingabe
# params = st.query_params
# param_league_id = params.get("league_id")
# param_roster_id = params.get("roster_id")

# if not params:# Eingabe für League ID
#     league_id = st.text_input("Gib die League ID ein")
# else:
#     league_id = param_league_id

# if league_id:
#     # Liga-Daten laden
#     league = get_league_info(league_id)
#     st.subheader("🔧 Ligaeinstellungen")
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.metric("Name", league.get("name"), border=True)
#     with col2:
#         def typ_to_word(typ):
#             return "Redraft" if typ == 0 else "Dynasty" if typ == 2 else "Keeper" if typ == 1 else "kA"
#         st.metric("Typ", typ_to_word(league.get("settings", {}).get("type", "Standard")), border=True)
#         # st.metric("Typ", league.get("settings", {}).get("type", "Standard"), border=True)
#     with col3:
#         st.metric("Teams", league.get("settings", {}).get("num_teams", "n/a"), border=True)

#     # Dropdown für Teamwahl
#     rosters = get_rosters(league_id)
#     options = {r["roster_id"]: f"Roster {r['roster_id']}" for r in rosters}
#     if not params:
#         selected_roster = st.selectbox("Wähle ein Roster", options.keys(), format_func=lambda x: options[x])
#     else:
#         selected_roster = param_roster_id

#     if selected_roster:
#         selected = next((r for r in rosters if r["roster_id"] == selected_roster), None)

#         if selected:
#             starters = selected.get("starters", [])
#             bench = [p for p in selected.get("players", []) if p not in starters]

#             def format_player(p_id):
#                 players = get_players()
#                 p = players.get(p_id, {})
#                 team = p.get("team")
#                 return {
#                     "Name": p.get("full_name", p_id),
#                     "Pos": p.get("position", "—"),
#                     "Team": TEAM_INFO.get(team, {}).get("name", team),
#                     "Logo": f"https://static.www.nfl.com/t_q-best/league/api/clubs/logos/{team}.svg",
#                     "Headshot": f"https://sleepercdn.com/content/nfl/players/{p_id}.jpg"
#                 }

#             roster_expander = st.expander("Roster-Details", expanded=False)
#             with roster_expander:
#                 st.markdown("### Starter")
#                 starter_data = [format_player(pid) for pid in starters if pid]
#                 df_start = pd.DataFrame(starter_data)
#                 for _, row in df_start.iterrows():
#                     cols = st.columns([1, 1, 3, 1])
#                     cols[0].image(row["Headshot"], width=80)     # 🧑‍🦱 Headshot
#                     cols[1].image(row["Logo"], width=50)         # 🏈 Teamlogo
#                     cols[2].markdown(f"**{row['Name']}**")       # 📛 Name
#                     cols[3].markdown(row["Pos"])                 # 📌 Position

#                 st.markdown("### Bench")
#                 bench_data = [format_player(pid) for pid in bench if pid]
#                 df_bench = pd.DataFrame(bench_data)
#                 for _, row in df_bench.iterrows():
#                     cols = st.columns([1, 1, 3, 1])
#                     cols[0].image(row["Headshot"], width=80)     # 🧑‍🦱 Headshot
#                     cols[1].image(row["Logo"], width=50)         # 🏈 Teamlogo
#                     cols[2].markdown(f"**{row['Name']}**")       # 📛 Name
#                     cols[3].markdown(row["Pos"])                 # 📌 Position
            
#             # st.markdown("### Picks")
#             # draft_id = league.get("draft_id")
#             # if draft_id:
#             #     draft_picks = f"https://api.sleeper.app/v1/draft/{draft_id}/picks"
#             #     traded=picks = f"https://api.sleeper.app/v1/draft/{draft_id}/traded_picks"

#             #     picks = requests.get(draft_picks).json()
#             #     pick_data = []
#             #     for pick in picks.values():
#             #         if pick["owner_id"] == selected_roster:
#             #             player_id = pick.get("player_id")
#             #             player_name = players.get(player_id, {}).get("full_name", "N/A")
#             #             pick_data.append({
#             #                 "Round": pick["round"],
#             #                 "Pick": pick["pick"],
#             #                 "Player": player_name
#             #             })
#             #     df_picks = pd.DataFrame(pick_data)
#             #     st.dataframe(df_picks, use_container_width=True)

#         share_page = st.button("Teilen")
#         if share_page:
#             # URL-Parameter kodieren
#             params = {
#                 "league_id": league_id,
#                 "roster_id": selected_roster if selected_roster else ""
#             }
#             st.markdown(f"https://stonedlack-2025.streamlit.app/showleague?{urllib.parse.urlencode(params)}")

#             share_url = f"https://stonedlack-2025.streamlit.app/showleague?{urllib.parse.urlencode(params)}"
#             st.text_input("🔗 Teilbarer Link", value=share_url)
