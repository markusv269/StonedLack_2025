import pandas as pd
from supabase import create_client, Client
import streamlit as st

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# IDs vorbereiten
leagues = supabase.table("leagues").select("league_id").eq("league_type", "redraft").execute().data
league_ids = [l["league_id"] for l in leagues]
drafts = supabase.table("drafts").select("draft_id").in_("league_id", league_ids).execute().data
draft_ids = [d["draft_id"] for d in drafts]

# ░░░ ALLE PICKS LADEN MIT PAGINATION ░░░
all_picks = []
page = 0
page_size = 1000

while True:
    picks_page = supabase.table("draft_picks") \
        .select("draft_id", "player_id", "json_data", "roster_id") \
        .lte("round", 5) \
        .in_("draft_id", draft_ids) \
        .range(page*page_size, (page+1)*page_size - 1) \
        .execute().data

    if not picks_page:
        break

    all_picks.extend(picks_page)
    page += 1

picks_df = pd.DataFrame(all_picks)
# Extrahiere zuerst pick_no in eine eigene Spalte
picks_df["pick_no"] = picks_df["json_data"].apply(lambda x: x.get("pick_no"))
picks_df["round"] = picks_df["json_data"].apply(lambda x: x.get("round"))

pick_no_df = (
    picks_df.sort_values(by="round").groupby(["draft_id", "roster_id"])["player_id"]
    .agg(list)
    .reset_index()
)
print(pick_no_df.sort_values(by="draft_id", ascending=True).head(40))