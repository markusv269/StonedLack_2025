import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
from styles import metric_box

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

@st.cache_data(ttl=3600)
def load_drafts():
    drafts = supabase.table("drafts").select("*").eq("season", 2025).execute()
    leagues = supabase.table("leagues").select("*").eq("league_type", "redraft").execute()
    picks = supabase.table("draft_picks").select("*").execute()
    picks_data = picks.data
    picks_df = pd.DataFrame(picks_data)
    league_data = leagues.data
    league_df = pd.DataFrame(league_data)
    drafts_data = drafts.data
    drafts_df = pd.DataFrame(drafts_data)
    drafts_df = drafts_df.merge(league_df[["league_id", "league_name"]], on="league_id", how="right")
    # drafts_df = drafts_df.merge(picks_df.groupby("draft_id").size().reset_index(name="total_picks"), on="draft_id", how="left")
    # drafts_df['start_time'] = pd.to_datetime(drafts_df['start_time'], utc=True)
    # alles nach dem Sekunden-Anteil wegschneiden
    drafts_df['start_time'] = drafts_df['start_time'].astype(str).str.replace(r'\.\d+', '', regex=True)

    # danach normal in datetime wandeln
    drafts_df['start_time'] = (pd.to_datetime(drafts_df['start_time'], utc=True, errors='coerce')+ pd.Timedelta(hours=2))
    drafts_df['start_time_str'] = drafts_df['start_time'].dt.strftime('%d.%m.%Y, %H:%M')
    drafts_df['updated_at'] = (pd.to_datetime(drafts_df['updated_at'], utc=True)+ pd.Timedelta(hours=2))
    drafts_df['last_updated_str'] = drafts_df['updated_at'].dt.strftime('%d.%m.%Y, %H:%M')
    drafts_df['league_number'] = drafts_df['league_name'].str.extract(r'(\d+)$').astype(int)
    return drafts_df
drafts_df = load_drafts()
for _,row in drafts_df[drafts_df["league_number"]<49].sort_values(by="league_number", ascending=True).iterrows():
    st.write(f"#### {row['league_name']}")

    col1, col2 = st.columns(2)
    with col2:
        metric_box("Draft Link:",f'<a href="https://sleeper.com/draft/nfl/{row["draft_id"]}" target="_blank">https://sleeper.com/draft/nfl/{row["draft_id"]}</a>')
    with col1:
        status = row['status']
        if status == "pre_draft":
            status = st.warning("Draft ausstehend")
        elif status == "drafting":
            status = st.info("Draft läuft")
        elif status == "paused":
            status = st.info("Draft pausiert")
        elif status == "complete":
            status = st.success("Draft abgeschlossen")
        else:
            status = st.warning(row["status"])
    col3, col4 = st.columns(2)
    with col3:
        metric_box("Startzeit:",f"{row['start_time_str']}")
    with col4:
        metric_box("Stand Datenbank:", f"{row['last_updated_str']}")
    st.write("---")
# st.write(load_drafts())
