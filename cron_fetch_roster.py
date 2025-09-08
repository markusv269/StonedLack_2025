from supabase import create_client, Client
import requests
from datetime import datetime, timezone
import os

# Supabase Credentials aus Environment Variables
url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 🏈 Aktuelle NFL-Woche über Sleeper abrufen
try:
    state_resp = requests.get("https://api.sleeper.app/v1/state/nfl")
    state_resp.raise_for_status()
    current_week = state_resp.json().get("week")

    if not current_week:
        raise ValueError("Woche konnte aus dem State-Response nicht gelesen werden.")
    print(f"Aktuelle NFL-Woche erkannt: Woche {current_week}")
except Exception as e:
    print(f"❌ Fehler beim Abrufen der aktuellen Woche: {e}")
    current_week = 1  # Fallback
    print("⚠️ Fallback auf Woche 1.")

# Alle league_ids aus der leagues-Tabelle holen
leagues_response = supabase.table("leagues").select("league_id").execute()
league_ids = [l["league_id"] for l in leagues_response.data]

SLEEPER_URL_TEMPLATE = "https://api.sleeper.app/v1/league/{}/rosters"
BATCH_SIZE = 500

for league_id in league_ids:
    url = SLEEPER_URL_TEMPLATE.format(league_id)
    resp = requests.get(url)
    
    if resp.status_code != 200:
        print(f"❌ Fehler beim Abrufen von Liga {league_id}: {resp.status_code}")
        continue
    
    matchups = resp.json()
    
    batch = []
    for idx, matchup in enumerate(matchups, start=1):
        batch.append({
            "league_id": league_id,
            "roster_id": str(matchup["roster_id"]),
            "fpts_for": round(matchup.get("settings", {}).get("fpts", 0) + matchup.get("settings", {}).get("fpts_decimal", 0) / 100,2),
            "fpts_against": round(matchup.get("settings", {}).get("fpts_against", 0) + matchup.get("settings", {}).get("fpts_against_decimal", 0) / 100,2),
            "week": int(current_week - 1),
            "wins": int(matchup.get("settings", {}).get("wins", 0)),
            "losses": int(matchup.get("settings", {}).get("losses", 0)),
            "ties": int(matchup.get("settings", {}).get("ties", 0)),
            "json_data": matchup 
        })
        
        if len(batch) == BATCH_SIZE or idx == len(matchups):
            try:
                supabase.table("rosters").upsert(batch).execute()
                print(f"✅ Batch von {len(batch)} Roster Liga {league_id} Woche {current_week} gespeichert.")
            except Exception as e:
                print(f"❌ Fehler beim Speichern Liga {league_id} Woche {current_week}: {e}")
            batch = []
