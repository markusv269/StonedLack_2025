import streamlit as st
import pandas as pd
from supabase import create_client, Client
from assets.styles_def import metric_box  # deine eigene Komponente
from methods import load_leagues_with_type, load_season_drafts, load_draftpicks

# ░░░ SUPABASE CREDENTIALS ░░░
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# ░░░ DATEN LADEN ░░░
@st.cache_data(ttl=5*60)
def load_drafts():
    # Supabase-Abfragen
    drafts_df = load_season_drafts(2025)
    leagues_df = load_leagues_with_type("redraft")
    picks_df = load_draftpicks()

    # Ligenname hinzufügen
    drafts_df = drafts_df.merge(
        leagues_df[["league_id", "league_name"]],
        on="league_id",
        how="right"
    )

    # Sekundenbruchteil bei start_time abschneiden
    drafts_df['start_time'] = drafts_df['start_time'].astype(str).str.replace(r'\.\d+', '', regex=True)
    drafts_df['start_time'] = pd.to_datetime(drafts_df['start_time'], utc=True, errors='coerce') + pd.Timedelta(hours=2)
    drafts_df['updated_at'] = pd.to_datetime(drafts_df['updated_at'], utc=True, errors='coerce') + pd.Timedelta(hours=2)

    # Formatierte Strings für Anzeige
    drafts_df['start_time_str'] = drafts_df['start_time'].dt.strftime('%d.%m.%Y, %H:%M').fillna("–")
    drafts_df['last_updated_str'] = drafts_df['updated_at'].dt.strftime('%d.%m.%Y, %H:%M').fillna("–")

    # League Number extrahieren
    drafts_df['league_number'] = drafts_df['league_name'].str.extract(r'(\d+)$').astype(float).astype('Int64')

    # Dictionary für schnelles Lookup: draft_id -> (round, pick_in_round)
    last_pick_by_draft_id = {}
    if not picks_df.empty:
        for draft_id, df in picks_df.groupby("draft_id"):
            highest_pick = df.loc[df["pick_no"].idxmax()]
            round_no = int(highest_pick["round"])
            pick_in_round = int((highest_pick["pick_no"] - 1) % 12 + 1)  # Sleeper = 12er-Runden
            last_pick_by_draft_id[draft_id] = (round_no, pick_in_round)

    return drafts_df, picks_df, last_pick_by_draft_id

# ░░░ DATEN LADEN ░░░
drafts_df, picks_df, last_pick_by_draft_id = load_drafts()

# ░░░ ANZEIGE ░░░
filtered_drafts = drafts_df[drafts_df["league_number"] < 49].sort_values(by="league_number")

for _, row in filtered_drafts.iterrows():
    st.write(f"#### {row['league_name']}")

    col1, col2 = st.columns(2)
    with col2:
        # Draft-Link
        metric_box(
            "Draft Link:",
            f'<a href="https://sleeper.com/draft/nfl/{row["draft_id"]}" target="_blank">Link öffnen</a>'
        )

    with col1:
        # Statusanzeige
        status = row.get('status', '').lower()
        if status == "pre_draft":
            st.warning("Draft ausstehend")
        elif status == "drafting":
            last_pick = last_pick_by_draft_id.get(row['draft_id'])
            if last_pick:
                round_no, pick_no = last_pick
                st.info(f"Draft läuft (Pick {round_no}.{pick_no})")
            else:
                st.info("Draft läuft (noch kein Pick)")
        elif status == "paused":
            last_pick = last_pick_by_draft_id.get(row['draft_id'])
            if last_pick:
                round_no, pick_no = last_pick
                st.info(f"Draft pausiert (Pick {round_no}.{pick_no})")
            else:
                st.info("Draft pausiert (noch kein Pick)")
            # st.info("Draft pausiert")
        elif status == "complete":
            st.success("Draft abgeschlossen")
        else:
            st.warning(f"Status: {status}")

    col3, col4 = st.columns(2)
    with col3:
        metric_box("Startzeit:", f"{row['start_time_str']}")
    with col4:
        metric_box("Stand Datenbank:", f"{row['last_updated_str']}")

    st.divider()

