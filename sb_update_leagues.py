from supabase import create_client, Client
import requests
from datetime import datetime, timezone
import os

# Supabase Credentials aus Environment Variables
url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Alle league_ids aus der leagues-Tabelle holen
leagues_response = supabase.table("leagues").select("league_id").execute()
league_ids = [l["league_id"] for l in leagues_response.data]

SLEEPER_URL_TEMPLATE = "https://api.sleeper.app/v1/league/{}"
BATCH_SIZE = 500

for league_id in league_ids:
    url = SLEEPER_URL_TEMPLATE.format(league_id)
    resp = requests.get(url)
    
    if resp.status_code != 200:
        print(f"❌ Fehler beim Abrufen von Liga {league_id}: {resp.status_code}")
        continue
    
    leagues = resp.json()
    
    batch = []
    for idx, league in enumerate(leagues, start=1):
      type = league.get("settings", {}).get("type", 0)
      if league_type == 0:
          is_redraft, is_dynasty = True, False
      elif league_type == 2:
          is_redraft, is_dynasty = False, True
      else:
          is_redraft = is_dynasty = None

      is_bestball = bool(league.get("settings"), {}).get("best_ball")

      roster = league.get("roster_positions")
      is_idp = any(position in roster for position in ("IDP", "CB", "DT", "DE"))
      is_idponly = is_idp and not any(
        position in roster for position in ("QB", "RB", "WR", "TE")
      )
            
      batch.append({
        "league_id": league_id,
        "league_name": str(league.get("name"), ""),
        "league_season": int(league.get("season"), 0),
        # "league_type": ,
        "league_scoring": league.get("scoring_settings", []),
        # "created_at": ,
        # "updated_at": ,
        "roster_positions": league.get("roster_positions", []),
        "league_champion_rid": league.get("metadata", {}).get("latest_league_winner_roster_id", 0),
        "previous_league_id": league.get("previous_league_id", None),
        "avatar": league.get("avatar", ""),
        "is_redraft": is_redraft,
        "is_dynasty": is_dynasty,
        "is_bestball": is_bestball,
        "is_idp": is_idp,
        "is_idponly": is_idponly,
        "status": league.get("status", "")
      })
        
        if len(batch) == BATCH_SIZE or idx == len(leagues):
            try:
                supabase.table("leagues").upsert(batch).execute()
                print(f"✅ Batch von {len(batch)} Ligen gespeichert.")
            except Exception as e:
                print(f"❌ Fehler beim Speichern Liga {league_id}: {e}")
            batch = []
