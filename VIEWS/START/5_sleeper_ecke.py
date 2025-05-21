import streamlit as st
import requests

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

st.write("### Bekannte sleeper API Endpoints")
def endpoint(desc, url):
    col1, col2 = st.columns(2)
    with col1:
        st.write(desc)
    with col2:
        st.write(url)
    # st.write("---")
st.write("#### Liga-API")
endpoint("League Info", "https://api.sleeper.app/v1/league/{league_id}")
endpoint("League Roster", "https://api.sleeper.app/v1/league/{league_id}/rosters")
endpoint("League Users", "https://api.sleeper.app/v1/league/{league_id}/users")
endpoint("League Settings", "https://api.sleeper.app/v1/league/{league_id}/settings")
endpoint("League Transactions", "https://api.sleeper.app/v1/league/{league_id}/transactions")
endpoint("League Matchups", "https://api.sleeper.app/v1/league/{league_id}/matchups")
endpoint("League Drafts", "https://api.sleeper.app/v1/league/{league_id}/drafts")
endpoint("League Drafts Picks", "https://api.sleeper.app/v1/league/{league_id}/drafts/{draft_id}/picks")

st.write("#### NFL")
endpoint("NFL Status", "https://api.sleeper.app/v1/state/nfl")
endpoint("NFL Players", "https://api.sleeper.app/v1/players/nfl")
endpoint("NFL Player Headshots", "https://sleepercdn.com/content/nfl/players/thumb/{player_id}.jpg")
endpoint("NFL Schedule", "https://api.sleeper.com/schedule/nfl/{season_type}/{season}")
endpoint("Teams Depth Charts", "https://api.sleeper.com/players/nfl/{team}/depth_chart")
endpoint("NFL Team Logos", "https://sleepercdn.com/images/team_logos/nfl/{team}.png")

st.write("#### NFL Player Stats und Projections")
endpoint("Player Stats", "https://api.sleeper.app/v1/stats/nfl/{season}/{season_type}/{player_id}")
endpoint("Player Projections", "https://api.sleeper.app/v1/projections/nfl/{season}/{season_type}/{player_id}")

st.write("### Trending Players")
endpoint("Trending up","https://api.sleeper.app/v1/players/nfl/trending/add")
endpoint("Trending down", "https://api.sleeper.app/v1/players/nfl/trending/drop")
endpoint("Trending up mit Zeitangabe und Spielerlimit", "https://api.sleeper.app/v1/players/nfl/trending/add?lookback_hours=24&limit=10")
endpoint("Trending down mit Zeitangabe und Spielerlimit", "https://api.sleeper.app/v1/players/nfl/trending/drop?lookback_hours=24&limit=10")
