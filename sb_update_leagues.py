from supabase import create_client, Client 
import requests 
import os 

# Supabase Credentials aus Environment Variables 
supabase_url: str = os.environ["SUPABASE_URL"] 
supabase_key: str = os.environ["SUPABASE_KEY"] 
supabase: Client = create_client(supabase_url, supabase_key) 

# Alle league_ids aus der leagues-Tabelle holen 
leagues_response = supabase.table("leagues").select("league_id").execute() 
league_ids = [league["league_id"] for league in leagues_response.data] 
SLEEPER_URL_TEMPLATE = "https://api.sleeper.app/v1/league/{}" 
BATCH_SIZE = 500 

batch = []

for league_id in league_ids: 
    sleeper_url = SLEEPER_URL_TEMPLATE.format(league_id) 
    try: 
        resp = requests.get(sleeper_url, timeout=10) 
        resp.raise_for_status() 
    except requests.RequestException as e: 
        print(f"❌ Fehler beim Abrufen von Liga {league_id}: {e}") 
        continue 
    league = resp.json() 

    # League Type 
    league_type = league.get("settings", {}).get("type", 0) 
    if league_type == 0: 
        is_redraft, is_dynasty = True, False 
    elif league_type == 2: 
        is_redraft, is_dynasty = False, True 
    else: is_redraft = is_dynasty = None 

    # Best Ball 
    is_bestball = bool( league.get("settings", {}).get("best_ball", False) ) 

    # IDP 
    roster = league.get("roster_positions", []) 
    is_idp = any( 
        position in roster 
        for position in ("IDP", "CB", "DT", "DE")
    ) 
    is_idponly = is_idp and not any( 
        position in roster 
        for position in ("QB", "RB", "WR", "TE") 
    ) 
    
    batch.append({ 
        "league_id": league_id, 
        "league_name": league.get("name", ""), 
        "league_season": int(league.get("season", 0)), 
        "league_scoring": league.get("scoring_settings", {}), 
        "roster_positions": roster, 
        "league_champion_rid": league.get("metadata", {}).get( "latest_league_winner_roster_id" ), 
        "previous_league_id": league.get("previous_league_id"), 
        "avatar": league.get("avatar", ""), 
        "is_redraft": is_redraft, 
        "is_dynasty": is_dynasty, 
        "is_bestball": is_bestball, 
        "is_idp": is_idp, 
        "is_idponly": is_idponly, 
        "status": league.get("status", ""), 
    })

    if len(batch) >= BATCH_SIZE: 
        supabase.table("leagues").upsert(batch).execute() 
        batch = []
    
if batch:
    supabase.table("leagues").upsert(batch).execute()
