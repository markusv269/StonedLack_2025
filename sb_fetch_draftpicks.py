from supabase import create_client, Client
import requests
import streamlit as st
from datetime import datetime, timezone

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

BATCH_SIZE = 999  # Batch-Größe für Upserts

# --- Alle Drafts mit Status "complete" abrufen ---
drafts = supabase.table("drafts").select("draft_id").execute()
draft_ids = [d["draft_id"] for d in drafts.data]

# --- Picks für jeden Draft abrufen ---
all_picks = []
for draft_id in draft_ids:
    url = f"https://api.sleeper.app/v1/draft/{draft_id}/picks"
    res = requests.get(url)
    picks = res.json()
    
    now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    
    for pick in picks:
        pick_record = {
            # "pick_id": pick.get("pick_id"),  # Wichtig für Upsert
            "draft_id": draft_id,
            "round": pick.get("round"),
            "pick_no": pick.get("pick_no"),
            "roster_id": pick.get("roster_id"),
            "player_id": pick.get("player_id"),
            "metadata": pick.get("metadata"),
            "json_data": pick,
            "updated_at": now
        }
        all_picks.append(pick_record)

# --- Upsert in Batches ---
for i in range(0, len(all_picks), BATCH_SIZE):
    batch = all_picks[i:i+BATCH_SIZE]
    supabase.table("draft_picks").upsert(batch).execute()
    print(f"✅ {len(batch)} Picks gespeichert (Batch {i//BATCH_SIZE + 1}).")

print(f"Alle Draft-Picks für {len(draft_ids)} Drafts wurden in Supabase aktualisiert!")
