from supabase import create_client, Client
import requests
import streamlit as st
from datetime import datetime, timezone

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# --- 1. Alle league_ids abrufen ---
leagues = supabase.table("leagues").select("league_id").execute()
league_ids = [l["league_id"] for l in leagues.data]

# --- 2. Alle existierenden Drafts aus Supabase abrufen ---
existing_drafts = supabase.table("drafts").select("draft_id,status").execute()
status_map = {d["draft_id"]: d["status"] for d in existing_drafts.data}

# --- 3. Alle neuen Drafts sammeln ---
all_records = []
now = datetime.now(timezone.utc).isoformat()

for league_id in league_ids:
    url = f"https://api.sleeper.app/v1/league/{league_id}/drafts"
    res = requests.get(url)
    drafts = res.json()

    for draft in drafts:
        draft_id = draft.get("draft_id")
        start_time_ms = draft.get("start_time")
        start_time_dt = None
        if start_time_ms:
            start_time_dt = datetime.fromtimestamp(start_time_ms / 1000, tz=timezone.utc).isoformat()

        draft_record = {
            "draft_id": draft_id,
            "league_id": league_id,
            "season": draft.get("season"),
            "draft_type": draft.get("settings", {}).get("player_type"),
            "status": draft.get("status"),
            "previous_status": status_map.get(draft_id),
            "start_time": start_time_dt,
            "updated_at": now,
            "json_data": draft,  # gesamtes Draft-JSON
        }
        all_records.append(draft_record)

print(f"📦 Insgesamt {len(all_records)} Draft-Datensätze gesammelt.")

# --- 4. Batchweise upsert in 250er Schritten ---
batch_size = 250
for i in range(0, len(all_records), batch_size):
    batch = all_records[i:i+batch_size]
    supabase.table("drafts").upsert(batch, on_conflict="draft_id").execute()
    print(f"✅ {len(batch)} Drafts gespeichert (Batch {i//batch_size + 1}).")
