import streamlit as st
from VIEWS.START._8_def import scoring_settings, showleague_info
import urllib.parse

league_info = {}

# Neue API verwenden
params = st.query_params
league_id = params.get("league_id")
roster_id = params.get("roster_id")

# Anzeige oder Eingabe
if league_id and roster_id:
    # st.success(f"Liga: {league_id}, Roster: {roster_id}")
    showleague_info(league_id, roster_id)
else:
    league_id_input = st.text_input("League ID")
    roster_id_input = st.text_input("Roster ID")
    if st.button("Lade Roster"):
        if league_id_input and roster_id_input:
            # Query-Parameter setzen (Seite wird neu geladen)
            st.query_params.league_id = league_id_input
            st.query_params.roster_id = roster_id_input
            showleague_info(league_id_input, roster_id_input)
        else:
            st.error("Bitte beide Felder ausfüllen.")

        query_string = urllib.parse.urlencode({
            "league_id": league_id_input,
            "roster_id": roster_id_input
        })
        share_url = f"https://stonedlack-2025.streamlit.app/showleague?{query_string}"
        st.success(f"Teile diese Seite: {share_url}")