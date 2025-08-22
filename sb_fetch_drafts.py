from supabase import create_client, Client
import requests
import streamlit as st
from datetime import datetime, timezone

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# --- 1. Alle league_ids aus Supabase abrufen ---
leagues = supabase.table("leagues").select("league_id").execute()
league_ids = [l["league_id"] for l in leagues.data]

# --- 2. Drafts für jede Liga abrufen und einfügen ---
for league_id in league_ids:
    url = f"https://api.sleeper.app/v1/league/{league_id}/drafts"
    res = requests.get(url)
    drafts = res.json()
    
    now = datetime.utcnow().isoformat()  # Timestamp für updated_at
    
    for draft in drafts:
        draft_id = draft.get("draft_id")
        start_time_ms = draft.get("start_time")
        start_time_dt = None
        if start_time_ms:
            start_time_dt = datetime.fromtimestamp(start_time_ms / 1000, tz=timezone.utc).isoformat()
        
        # --- Aktuellen Status aus der DB abrufen ---
        existing = supabase.table("drafts").select("status").eq("draft_id", draft_id).execute()
        previous_status = existing.data[0]["status"] if existing.data else None

        draft_record = {
            "draft_id": draft_id,
            "league_id": league_id,
            "season": draft.get("season"),
            "draft_type": draft.get("settings", {}).get("player_type"),
            "status": draft.get("status"),
            "previous_status": previous_status,
            "start_time": start_time_dt,
            "updated_at": now,
            "json_data": draft,  # gesamtes Draft-JSON
        }
        supabase.table("drafts").upsert(draft_record, on_conflict="draft_id").execute()

print("Alle Drafts wurden in Supabase aktualisiert!")
