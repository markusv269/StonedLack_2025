import streamlit as st
import pandas as pd
from supabase import create_client, Client
from assets.styles_def import metric_box  # deine eigene Komponente
from methods import load_leagues_with_type, load_season_drafts

# ░░░ SUPABASE CREDENTIALS ░░░
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# owner = supabase.table("managers").select("*").eq("display_name", "Witfar").execute().data[0]
# league = supabase.table("leagues").select("*").eq("league_id", owner["league_id"]).execute().data[0]
# draft = supabase.table("drafts").select("*").eq("league_id", ).execute().data[0]
draft_picks = supabase.table("draft_picks").select("*").eq("draft_id", "1259456415748083712").execute().data
draft_picks_df = pd.DataFrame(draft_picks)
# Zeile mit dem höchsten pick_no
highest_pick = draft_picks_df.loc[draft_picks_df["pick_no"].idxmax()]

print(highest_pick['pick_no'])