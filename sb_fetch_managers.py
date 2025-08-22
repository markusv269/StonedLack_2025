from supabase import create_client, Client
import requests
import streamlit as st

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

def fetch_and_store_managers(league_id: str):
    # Roster-Daten
    rosters_url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    users_url = f"https://api.sleeper.app/v1/league/{league_id}/users"

    rosters_res = requests.get(rosters_url).json()
    users_res = requests.get(users_url).json()

    # User-Dict nach user_id
    user_map = {u["user_id"]: u for u in users_res}

    for roster in rosters_res:
        user_id = roster.get("owner_id")
        roster_id = roster.get("roster_id")

        if not user_id:
            print(f"⚠️ Roster {roster_id} in Liga {league_id} hat keinen Besitzer, übersprungen.")
            continue

        user = user_map.get(user_id, {})
        display_name = user.get("display_name")
        team_name = user.get("metadata", {}).get("team_name")

        record = {
            "league_id": league_id,
            "roster_id": roster_id,
            "user_id": user_id,
            "display_name": display_name,
            "team_name": team_name,
        }

        supabase.table("managers").upsert(record).execute()
        print(f"✅ Manager {display_name} ({team_name}) für Liga {league_id} gespeichert.")


# --- league_ids aus Supabase laden ---
leagues = supabase.table("leagues").select("league_id").execute()
league_ids = [l["league_id"] for l in leagues.data]

# Für jede League Manager-Daten abholen
for league_id in league_ids:
    fetch_and_store_managers(league_id)
