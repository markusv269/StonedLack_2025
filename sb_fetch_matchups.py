from supabase import create_client, Client
import requests
import streamlit as st
from datetime import datetime, timezone
import json

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# Alle league_ids aus der leagues-Tabelle holen
leagues_response = supabase.table("leagues").select("league_id").execute()
league_ids = [l["league_id"] for l in leagues_response.data]

week = 1
SLEEPER_URL_TEMPLATE = "https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"

BATCH_SIZE = 500

for league_id in league_ids:
    url = SLEEPER_URL_TEMPLATE.format(league_id=league_id, week=week)
    resp = requests.get(url)
    
    if resp.status_code != 200:
        print(f"Fehler beim Abrufen von Liga {league_id}: {resp.status_code}")
        continue
    
    matchups = resp.json()
    
    batch = []
    for idx, matchup in enumerate(matchups, start=1):
        batch.append({
            "league_id": league_id,
            "matchup_id": matchup.get("matchup_id"),
            "roster_id": str(matchup["roster_id"]),
            "points": matchup.get("points", 0),
            "json_data": json.dumps(matchup),
            "week": week
        })
        
        if len(batch) == BATCH_SIZE or idx == len(matchups):
            try:
                supabase.table("matchup_week_stats").upsert(batch).execute()
                print(f"Batch von {len(batch)} Matchups Liga {league_id} Woche {week} gespeichert.")
            except Exception as e:
                print(f"Fehler beim Batch Speichern Liga {league_id} Woche {week}: {e}")
            batch = []