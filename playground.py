import requests
import pandas as pd
from supabase import create_client, Client
import streamlit as st

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# Alle Redraft-Ligen
leagues_response = supabase.table("leagues").select("league_id").eq("league_type", "redraft").execute()
league_ids = [l["league_id"] for l in leagues_response.data]

base_url = "https://api.sleeper.app/v1/league/{league_id}/transactions/{round}"

records = []
all_player_ids = set()

for league_id in league_ids:
    url = base_url.format(league_id=league_id, round=2)
    r = requests.get(url)
    data = r.json()
    
    for txn in data:
        if txn.get("status") == "complete" and txn.get("type") == "waiver":
            adds = txn.get("adds") or {}
            drops = txn.get("drops") or {}

            # Player-IDs sammeln
            all_player_ids.update(adds.keys())
            all_player_ids.update(drops.keys())

            records.append({
                "league_id": league_id,
                "transaction_id": txn.get("transaction_id"),
                "adds": list(adds.keys()),
                "drops": list(drops.keys()),
                "creator": txn.get("creator"),
                "waiver_bid": txn.get("settings", {}).get("waiver_bid", 0)
            })

# Spieler nur für vorkommende IDs abfragen
players_response = (
    supabase.table("nfl_players")
    .select("player_id, name")
    .in_("player_id", list(all_player_ids))
    .execute()
)

players_df = pd.DataFrame(players_response.data)
player_map = dict(zip(players_df["player_id"], players_df["name"]))

# Mapping anwenden
def map_players(player_ids):
    return [player_map.get(pid, pid) for pid in player_ids]

for rec in records:
    rec["adds"] = map_players(rec["adds"])
    rec["drops"] = map_players(rec["drops"])

df = pd.DataFrame(records)

# Ausgabe
for idx, row in df.iterrows():
    print(f"League ID: {row['league_id']} | Txn ID: {row['transaction_id']}")
    print(f"Adds: {', '.join(row['adds'])}")
    print(f"Drops: {', '.join(row['drops'])}")
    print(f"Waiver Bid: {row['waiver_bid']}")
    print("---")
