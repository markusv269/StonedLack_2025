import requests
import pandas as pd
from supabase import create_client, Client
import streamlit as st
from methods import load_managers

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# Alle Redraft-Ligen
leagues_response = supabase.table("leagues").select("league_id").eq("league_type", "redraft").execute()
league_ids = [l["league_id"] for l in leagues_response.data]

# manager = supabase.table("managers").select("user_id, display_name").execute()
managers_df = load_managers()
manager_map = dict(zip(managers_df["user_id"], managers_df["display_name"]))

base_url = "https://api.sleeper.app/v1/league/{league_id}/transactions/{round}"

records = []
all_player_ids = set()

for league_id in league_ids:
    for round in [1, 2]:  # Beispiel für Runde 1 und 2
        url = base_url.format(league_id=league_id, round=round)
        r = requests.get(url)
        data = r.json()
        
        for txn in data:
            if  txn.get("type") == "waiver" and txn.get("status_updated") > 1757512800000:
                adds = txn.get("adds") or {}
                drops = txn.get("drops") or {}

                # Player-IDs sammeln
                all_player_ids.update(adds.keys())
                all_player_ids.update(drops.keys())

                records.append({
                    "league_id": league_id,
                    "transaction_id": txn.get("transaction_id"),
                    "status": txn.get("status"),
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

def map_creator(creator_id):
    return manager_map.get(creator_id, creator_id)

for rec in records:
    rec["adds"] = map_players(rec["adds"])
    rec["drops"] = map_players(rec["drops"])

df = pd.DataFrame(records)

# Adds und Drops in einzelne Zeilen auflösen
adds_df = df.explode("adds")[["league_id", "transaction_id", "creator", "waiver_bid", "adds", "status"]]
adds_df = adds_df.rename(columns={"adds": "player"})
adds_df["action"] = "add"

drops_df = df.explode("drops")[["league_id", "transaction_id", "creator", "waiver_bid", "drops", "status"]]
drops_df = drops_df.rename(columns={"drops": "player"})
drops_df["action"] = "drop"

# Zusammenführen
moves_df = pd.concat([adds_df, drops_df], ignore_index=True)
moves_df["creator"] = moves_df["creator"].apply(map_creator)

# Jetzt Gruppierung pro Spieler
summary = (
    moves_df.groupby(["player", "status", "action"])
    .agg(
        min_price=("waiver_bid", "min"),
        max_price=("waiver_bid", "max"),
        avg_price=("waiver_bid", "mean"),
        transactions=("transaction_id", "count"),
        owners_bid=("creator", lambda x: list(set(x)))
    )
    .reset_index()
)

print(summary[summary["action"]=="add"].sort_values(by=["player", "max_price"], ascending=[True, False]))
summary[summary["action"]=="add"].sort_values(by=["player", "max_price"], ascending=[True, False]).to_csv("waiver_adds_week2.csv", index=False)
