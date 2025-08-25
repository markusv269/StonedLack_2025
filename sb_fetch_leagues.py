from supabase import create_client, Client
import requests
from config import REDLEAGUES_2025, DYNLEAGUES_2025  # Importiere deine Ligen-IDs
import streamlit as st
from datetime import datetime, timezone

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

def fetch_and_store_league(league_id: str, league_type: str):
    api_url = f"https://api.sleeper.app/v1/league/{league_id}"
    response = requests.get(api_url)
    if response.status_code != 200:
        print(f"❌ Fehler beim Abruf von League {league_id}")
        return

    league_data = response.json()
    now = datetime.now(timezone.utc).isoformat()

    record = {
        "league_id": league_id,
        "league_name": league_data.get("name"),
        "league_season": int(league_data.get("season")),
        "league_type": league_type,
        "league_scoring": league_data.get("scoring_settings", {}),
        "roster_positions": league_data.get("roster_positions", {}),
        "updated_at": now,
    }

    # Insert oder Update
    # -> Wenn neuer Datensatz: created_at = now
    # -> Wenn existiert: nur updated_at ändern
    supabase.table("leagues").upsert(record, on_conflict=["league_id"]).execute()

    print(f"✅ League {record['league_name']} ({league_id}) gespeichert/aktualisiert.")

# Redraft-Ligen verarbeiten
for league_id in REDLEAGUES_2025.keys():
    fetch_and_store_league(league_id, "redraft")

# Dynasty-Ligen verarbeiten
for league_id in DYNLEAGUES_2025:
    fetch_and_store_league(league_id, "dynasty")
