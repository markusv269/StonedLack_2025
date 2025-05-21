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
# st.title("🏈 Fantasy League Übersicht")
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
        position_order = ["QB", "RB", "WR", "TE", "K", "DEF", "LB", "DB", "DL"]

        # Spieler formatieren
        def format_player(pid):
            p = players_data.get(pid, {})
            team = p.get("team", "")
            return {
                "Name": p.get("full_name", pid),
                "Pos": p.get("position", "—"),
                "Team": TEAM_INFO.get(team, {}).get("name", team),
                "Logo": f"https://static.www.nfl.com/t_q-best/league/api/clubs/logos/{team}.svg",
                "Headshot": f"https://sleepercdn.com/content/nfl/players/{pid}.jpg"
            }

        # Tabellenrendering als Funktion
        def render_table(title, player_ids, sorting=True):
            st.markdown(f"### {title}")
            player_data = [format_player(pid) for pid in player_ids if pid]
            if sorting == True:
                player_data.sort(key=lambda x: position_order.index(x["Pos"]) if x["Pos"] in position_order else 99)

            html = """
            <table style="width:100%; border-collapse: collapse;">
            <thead>
                <tr style="text-align: left; border-bottom: 1px solid #ddd;">
                <th style="padding: 8px;">Headshot</th>
                <th style="padding: 8px;">Teamlogo</th>
                <th style="padding: 8px;">Name</th>
                <th style="padding: 8px;">Position</th>
                </tr>
            </thead>
            <tbody>
            """
            for player in player_data:
                html += f"""
                <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 8px;"><img src="{player['Headshot']}" style="height:50px; border-radius:6px;"></td>
                <td style="padding: 8px;"><img src="{player['Logo']}" style="height:40px;"></td>
                <td style="padding: 8px;">{player['Name']}</td>
                <td style="padding: 8px;">{player['Pos']}</td>
                </tr>
                """
            html += "</tbody></table>"
            st.html(html)

        # Ausgabe 
        render_table("🔥 Starter", starters, sorting=False)
        render_table("🧊 Bench", bench)
       