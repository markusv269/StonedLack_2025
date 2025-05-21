import streamlit as st
import pandas as pd
import json
from sleeper_wrapper import Players
import requests

@st.cache_data(ttl=3600*48, show_spinner=True)
def get_sleeper_players():
    with open("nflplayer.json", "r") as f:
        players = json.load(f)
        active_players = {k: v for k, v in players.items() if v.get("active") is True and v.get("position") in ["RB", "WR", "TE", "QB", "K", "DL", "LB", "DB"] and v.get("team") is not None}

        for pid, player in active_players.items():
            projection_url = f"https://api.sleeper.com/projections/nfl/player/{pid}?season_type=regular&season=2025"
            try:
                # Daten von der URL abrufen
                response = requests.get(projection_url)
                response.raise_for_status()  # wirft Fehler bei HTTP-Fehlern

                # JSON-Daten direkt in Python-Dict
                projection_data = response.json()

                # Optional: In DataFrame umwandeln, dann in Dict – wenn nötig
                if isinstance(projection_data, list) and projection_data:
                    df = pd.DataFrame(projection_data)
                    player["projection"] = df.to_dict(orient="records")
                else:
                    player["projection"] = projection_data
            except Exception as e:
                player["projection"] = {"error": str(e)}
        adp_keys = [
            "adp_2qb", "adp_dynasty", "adp_dynasty_2qb", "adp_dynasty_half_ppr",
            "adp_dynasty_ppr", "adp_dynasty_std", "adp_half_ppr", "adp_idp",
            "adp_ppr", "adp_std"
        ]
        filtered_players = {
            pid: player for pid, player in active_players.items()
            if "stats" in player and all(
                float(player["stats"].get(key, 9999)) < 100 for key in adp_keys
            )
        }
    return filtered_players

player_data = get_sleeper_players()


subset = dict(list(player_data.items())[:10])
st.json(subset)