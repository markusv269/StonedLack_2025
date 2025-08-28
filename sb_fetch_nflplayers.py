from supabase import create_client, Client
import requests
import streamlit as st
from datetime import datetime, timezone

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# --- Alle player_ids aus draft_picks abrufen ---
resp = supabase.table("draft_picks").select("player_id", count="exact").execute()
player_ids = set(str(p["player_id"]) for p in resp.data if p["player_id"])

# --- Alle NFL-Spieler von Sleeper abrufen ---
url = "https://api.sleeper.app/v1/players/nfl"
r = requests.get(url)
all_players = r.json()

# --- Nur Spieler, die in draft_picks vorkommen ---
players_to_insert = []
for pid, player in all_players.items():
    # if pid.strip() in player_ids:
    player["updated_at"] = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    players_to_insert.append({
        "player_id": pid,
        "name": player.get("full_name") or f"{player.get('first_name', '')} {player.get('last_name', '')}",
        "team": player.get("team"),
        "position": player.get("position"),
        "json_data": player,
        "updated_at": player["updated_at"]
    })

# --- Funktion zum Batch-Upsert ---
def batch_upsert(table_name, records, batch_size=500):
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        supabase.table(table_name).upsert(batch, on_conflict="player_id").execute()
        print(f"{len(batch)} Spieler hochgeladen...")

# --- In Supabase einfügen ---
batch_upsert("nfl_players", players_to_insert)
print("NFL-Spieler aus Draft-Picks wurden aktualisiert.")
print(player_ids)