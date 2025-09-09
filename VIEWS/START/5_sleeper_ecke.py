import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.subheader("sleeper.com trending Players")
# Setze den Titel der App
col1, col2 = st.columns(2)
with col1:
    hours = st.slider("Zeitraum angeben (h)", min_value=6, step=6, max_value=7*24)
with col2:
    player = st.slider("Anzahl der angezeigten Spieler", min_value=5, max_value=25)

# Einbetten des Sleeper-Widgets mit einem IFrame
sleeper_url = "https://sleeper.app/embed/players/nfl/trending/{}?lookback_hours={}&limit={}"
add_url = sleeper_url.format("add", hours, player)
drop_url = sleeper_url.format("drop", hours, player)
col1, col2 = st.columns(2)
with col1:
    st.components.v1.iframe(add_url, width=300, height=20+player*50, scrolling=False)
with col2:
    st.components.v1.iframe(drop_url, width=300, height=20+player*50, scrolling=False)

st.write("---")
st.subheader("NFL State")
state_url = "https://api.sleeper.app/v1/state/nfl"
response = requests.get(state_url)
sleeper_state = response.json() if response.status_code == 200 else {}
col1, col2 = st.columns(2)
with col1:
    st.write('''
    Saison  
    Saisonstatus   
    Woche''')
with col2:
    st.write(f'''
    {sleeper_state["season"]}  
    {sleeper_state["season_type"]}  
    {sleeper_state["week"]}''')
    # st.write(sleeper_state)

# st.write("### Bekannte sleeper API Endpoints")
# def endpoint(desc, url):
#     col1, col2 = st.columns([1,2])
#     with col1:
#         st.write(desc)
#     with col2:
#         st.write(url)
#     # st.write("---")
# st.write("#### Liga-API")
# endpoint("League Info", "https://api.sleeper.app/v1/league/{league_id}")
# endpoint("League Roster", "https://api.sleeper.app/v1/league/{league_id}/rosters")
# endpoint("League Users", "https://api.sleeper.app/v1/league/{league_id}/users")
# endpoint("League Settings", "https://api.sleeper.app/v1/league/{league_id}/settings")
# endpoint("League Transactions", "https://api.sleeper.app/v1/league/{league_id}/transactions")
# endpoint("League Matchups", "https://api.sleeper.app/v1/league/{league_id}/matchups")
# endpoint("League Drafts", "https://api.sleeper.app/v1/league/{league_id}/drafts")
# endpoint("League Drafts Picks", "https://api.sleeper.app/v1/league/{league_id}/drafts/{draft_id}/picks")

# st.write("#### NFL")
# endpoint("NFL Status", "https://api.sleeper.app/v1/state/nfl")
# endpoint("NFL Players", "https://api.sleeper.app/v1/players/nfl")
# endpoint("NFL Player Info", "https://api.sleeper.com/players/nfl/{player_id}")
# endpoint("NFL Player Headshots", "https://sleepercdn.com/content/nfl/players/thumb/{player_id}.jpg")
# endpoint("NFL Schedule", "https://api.sleeper.com/schedule/nfl/{season_type}/{season}")
# endpoint("Teams Depth Charts", "https://api.sleeper.com/players/nfl/{team}/depth_chart")
# endpoint("NFL Team Logos", "https://sleepercdn.com/images/team_logos/nfl/{team}.png")

# st.write("#### NFL Player Stats und Projections")
# endpoint("Player Stats", "https://api.sleeper.app/v1/stats/nfl/{season}/{season_type}/{player_id}")
# endpoint("Player Projections", "https://api.sleeper.app/v1/projections/nfl/{season}/{season_type}/{player_id}")

# st.write("### Trending Players")
# endpoint("Trending up","https://api.sleeper.app/v1/players/nfl/trending/add")
# endpoint("Trending down", "https://api.sleeper.app/v1/players/nfl/trending/drop")
# endpoint("Trending up mit Zeitangabe und Spielerlimit", "https://api.sleeper.app/v1/players/nfl/trending/add?lookback_hours={hours}&limit={limit}")
# endpoint("Trending down mit Zeitangabe und Spielerlimit", "https://api.sleeper.app/v1/players/nfl/trending/drop?lookback_hours={hours}&limit={limit}")

st.write("---")
st.subheader("Fantasy Points Allowed")

teams = [
    "ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL","DEN","DET","GB",
    "HOU","IND","JAX","KC","LV","LAC","LAR","MIA","MIN","NE","NO","NYG","NYJ",
    "PHI","PIT","SF","SEA","TB","TEN","WAS"
]

base_url = "https://api.sleeper.com/stats/nfl/player/{team}?season_type=regular&season={season}&grouping={grouping}"

@st.cache_data
def load_data(season, grouping, week=None):
    records = []
    for team in teams:
        url = base_url.format(team=team, season=season, grouping=grouping.lower())
        r = requests.get(url)
        data = {}   # <-- hier Standardwert setzen

        if r.status_code == 200:
            data = r.json()

        # Stats holen
        if grouping.lower() == "week" and week is not None:
            stats = (data.get(str(week), {}) or {}).get("stats", {})
        else:
            stats = (data or {}).get("stats", {})

        fan_pts_allow = {k: v for k, v in stats.items() if k.startswith("fan_pts_allow")}
        record = {"team": team}
        record.update(fan_pts_allow)
        records.append(record)

    df = pd.DataFrame(records)
    positions = [
        "fan_pts_allow_qb", "fan_pts_allow_rb", "fan_pts_allow_wr",
        "fan_pts_allow_te", "fan_pts_allow_k", "fan_pts_allow_def"
    ]
    for p in positions:
        if p not in df.columns:
            df[p] = 0.0
    df_plot = df[["team"] + positions].set_index("team").fillna(0.0)
    df_plot["total"] = df_plot[positions].sum(axis=1)
    return df_plot, positions

df_plot, positions = load_data(season=2025, grouping="Season")

# ---------------- UI ----------------
st.write("#### Einstellungen")
col1, col2 = st.columns(2)
with col1:
    select_season = st.selectbox("Saison", [2025, 2024, 2023, 2022, 2021, 2020], index=0)
with col2:
    grouping = st.selectbox("Gruppierung", ["Season", "Week"], index=0)
    if grouping == "Week":
        week = st.slider("Woche", min_value=1, max_value=18, value=1, step=1)
    else:
        week = None 
col3, col4 = st.columns(2)
with col3:
    sort_by = st.selectbox(
        "Sortieren nach",
        ["total"] + positions,
        format_func=lambda x: "Gesamt" if x == "total" else x.split("_")[-1].upper()
    )

col3, col4 = st.columns(2)
with col3:
    order_label = st.radio("Reihenfolge", ["Absteigend", "Aufsteigend"], horizontal=False)
    ascending = (order_label == "Aufsteigend")

with col4:
    chart_type = st.radio(
    "Diagramm-Typ",
    ["Gestapelt (alle Positionen)", "Einzelne Position"]
)
col5, col6 = st.columns(2)
with col5:
    st.write("**Datenquelle: sleeper.com API**")
# ---------------- Sortierung anwenden ----------------
if st.button("Daten neu laden"):
        load_data.clear()
        df_plot, positions = load_data(season=select_season, grouping=grouping, week=week)

df_sorted = df_plot.sort_values(by=sort_by, ascending=ascending).copy()

# WICHTIG: Teams als kategorischen Index in genau dieser Reihenfolge,
# damit st.bar_chart die gewünschte Sortierung übernimmt.
ordered_teams = list(df_sorted.index)
df_sorted.index = pd.Categorical(df_sorted.index, categories=ordered_teams, ordered=True)

# if 
# ---------------- Charts ----------------
if chart_type == "Gestapelt (alle Positionen)":
    # Optional: nur die Positionsspalten anzeigen
    st.bar_chart(
        df_sorted[positions],
        stack=True,
        height=600,
        use_container_width=True
    )
else:
    pos_choice = st.selectbox(
        "Position auswählen",
        positions,
        format_func=lambda x: x.split("_")[-1].upper()
    )
    # Für die Einzelansicht ggf. nach der gewählten Position neu sortieren:
    df_pos = df_plot.sort_values(by=pos_choice, ascending=ascending).copy()
    ordered_teams_pos = list(df_pos.index)
    df_pos.index = pd.Categorical(df_pos.index, categories=ordered_teams_pos, ordered=True)

    st.bar_chart(
        df_pos[[pos_choice]],
        stack=False,
        height=600,
        use_container_width=True
    )