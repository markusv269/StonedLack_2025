import streamlit as st
from sleeper_wrapper import League, User
from config import REDLEAGUES
import pandas as pd

red_leagues = REDLEAGUES

league_overview = {}

for league_id in red_leagues:
    user_name = ""
    league = League(league_id)

    try:
        league_data = league.get_league()
        if not isinstance(league_data, dict):
            raise ValueError(f"Ungültige API-Antwort für League ID {league_id}: {league_data}")
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Ligadaten für Liga-ID{league_id}")
        continue

    try:
        roster_data = league.get_rosters()
        if not isinstance(roster_data, list):
            raise ValueError(f"Ungültige Roster-Antwort für League ID {league_id}: {roster_data}")
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Roster-Daten für {league_id}: {e}")
        roster_data = []

    champ = league_data.get("metadata", {}).get("latest_league_winner_roster_id", "--")

    if champ:
        owner_id = next((entry["owner_id"] for entry in roster_data if entry["roster_id"] == int(champ)), None)
        if owner_id:
            user = User(owner_id)
            try:
                user_name = user.get_display_name()
            except Exception as e:
                st.error(f"Fehler beim Abrufen des Usernamens für {owner_id}: {e}")
                user_name = "--"

    if league_data['name'] not in league_overview:
        league_overview[league_data['name']] = [
            league_data['league_id'], 
            league_data.get("avatar", ""), 
            league_data["season"], 
            user_name
        ]

# DataFrame erstellen
league_df = pd.DataFrame(league_overview).T.reset_index(drop=False).rename(
    columns={"index": "Liga", 0: "League-ID", 1: "avatar", 2: "Saison", 3: "Amt. Champion"}
)
league_df["avatar_url"] = "https://sleepercdn.com/avatars/" + league_df["avatar"].astype(str)

# Ausgabe in Streamlit
st.write("### Ligenübersicht")
st.dataframe(
    league_df[["avatar_url", "Liga", "Amt. Champion", "Saison"]],
    column_config={"avatar_url": st.column_config.ImageColumn(" ")},
    hide_index=True
)
