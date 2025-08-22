from supabase import create_client, Client
import requests
import streamlit as st
from datetime import datetime, timezone, timedelta
import json

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

def ms_to_dhms(ms: int) -> str:
    """Millisekunden in Tage, Stunden, Minuten, Sekunden umrechnen"""
    seconds = ms // 1000
    delta = timedelta(seconds=seconds)
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

# Schritt 1: Redraft-Leagues mit Namen holen
redraft_leagues = supabase.table("leagues").select("league_id, league_name") \
    .eq("league_type", "redraft").execute()

league_map = {row["league_id"]: row["league_name"] for row in redraft_leagues.data}

# Schritt 2: Drafts holen (nur complete + nur aus Redraft-Ligen)
drafts = supabase.table("drafts").select("draft_id, league_id, draft_status, json_data") \
    .in_("league_id", list(league_map.keys())).eq("draft_status", "complete").execute()

# Zwischenspeicher für Ergebnisse
results = []

# Schritt 3: Dauer berechnen + sammeln
for row in drafts.data:
    draft_id = row["draft_id"]
    league_id = row["league_id"]
    league_name = league_map.get(league_id, "Unknown League")
    json_data = row.get("json_data")

    if not json_data:
        continue

    data = json.loads(json_data)
    start_time = data.get("start_time")
    last_picked = data.get("last_picked")

    if start_time and last_picked:
        diff = last_picked - start_time
        duration_str = ms_to_dhms(diff)
        results.append({
            "league_name": league_name,
            "draft_id": draft_id,
            "duration_ms": diff,
            "duration_str": duration_str
        })

# Schritt 4: Ergebnisse nach Dauer sortieren (längster Draft zuerst)
results_sorted = sorted(results, key=lambda x: x["duration_ms"], reverse=True)

# Schritt 5: Ausgabe
for r in results_sorted:
    print(f"League: {r['league_name']} | Draft {r['draft_id']} | Dauer = {r['duration_str']}")