import streamlit as st
from sleeper_wrapper import League, User, Drafts
import urllib.parse
# Query-Parameter auslesen
query_params = st.query_params
league_id = query_params.get("league_id")
roster_id = query_params.get("roster_id")

def showleague_info(league_id, roster_id):
    try:
        league = League(league_id)
        league_data = league.get_league()
    except Exception as e:
        st.error(f"Fehler beim Laden der Liga: {e}")
        return

    try:
        rosters = league.get_rosters()
        roster_info = next((r for r in rosters if str(r['roster_id']) == str(roster_id)), None)
    except Exception as e:
        st.error(f"Fehler beim Laden der Roster: {e}")
        return

    if roster_info:
        st.write(f"#### League Info: {league_data.get('name')} ({league_data.get('season')})")
        st.write(f"**Roster ID {roster_id} Details:**")
        st.json(roster_info)
    else:
        st.warning("Roster nicht gefunden.")

# Neue API verwenden
params = st.query_params
league_id = params.get("league_id")
roster_id = params.get("roster_id")

# Titel
st.title("Sleeper League Roster Viewer")

# Anzeige oder Eingabe
if league_id and roster_id:
    st.success(f"Liga: {league_id}, Roster: {roster_id}")
    showleague_info(league_id, roster_id)
else:
    league_id_input = st.text_input("League ID")
    roster_id_input = st.text_input("Roster ID")
    if st.button("Lade Roster"):
        if league_id_input and roster_id_input:
            # Query-Parameter setzen (Seite wird neu geladen)
            st.query_params.league_id = league_id_input
            st.query_params.roster_id = roster_id_input
        else:
            st.error("Bitte beide Felder ausfüllen.")

# Teilen-Link generieren
if league_id and roster_id:
    query_string = urllib.parse.urlencode({
        "league_id": league_id,
        "roster_id": roster_id
    })
    share_url = f"https://stonedlack-2025.streamlit.app/{query_string}"
    if st.button("Share Link"):
        st.text_input("Teilen-Link", value=share_url, label_visibility="collapsed")
        st.success("Link zum Teilen generiert.")