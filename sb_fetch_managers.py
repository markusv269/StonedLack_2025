from supabase import create_client, Client
import requests
import streamlit as st

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

def fetch_managers_from_league(league_id: str):
    """Hole Manager-Daten einer Liga und gib sie als Liste zurück"""
    rosters_url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    users_url = f"https://api.sleeper.app/v1/league/{league_id}/users"

    rosters_res = requests.get(rosters_url).json()
    users_res = requests.get(users_url).json()

    user_map = {u["user_id"]: u for u in users_res}
    records = []

    for roster in rosters_res:
        user_id = roster.get("owner_id")
        roster_id = roster.get("roster_id")

        if not user_id:
            print(f"⚠️ Roster {roster_id} in Liga {league_id} hat keinen Besitzer, übersprungen.")
            continue

        user = user_map.get(user_id, {})
        display_name = user.get("display_name")
        team_name = user.get("metadata", {}).get("team_name")

        records.append({
            "league_id": league_id,
            "roster_id": roster_id,
            "user_id": user_id,
            "display_name": display_name,
            "team_name": team_name,
        })

    return records


# --- league_ids aus Supabase laden ---
leagues = supabase.table("leagues").select("league_id").execute()
league_ids = [l["league_id"] for l in leagues.data]

# --- Alle Manager aus allen Ligen sammeln ---
all_records = []
for league_id in league_ids:
    all_records.extend(fetch_managers_from_league(league_id))

print(f"📦 Insgesamt {len(all_records)} Manager-Datensätze gesammelt.")

# --- Batchweise in 250er Schritten upserten ---
batch_size = 250
for i in range(0, len(all_records), batch_size):
    batch = all_records[i:i+batch_size]
    supabase.table("managers").upsert(batch).execute()
    print(f"✅ {len(batch)} Manager gespeichert (Batch {i//batch_size + 1}).")
