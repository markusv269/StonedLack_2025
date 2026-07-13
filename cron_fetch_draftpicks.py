from supabase import create_client, Client
import requests
from datetime import datetime, timezone
import os

# Supabase Credentials aus Environment Variables
url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

BATCH_SIZE = 1000  # Batch-Größe für Upserts

# --- Alle Drafts abrufen ---
drafts = supabase.table("drafts").select("draft_id").execute()#.neq("previous_status", "complete").execute()
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
