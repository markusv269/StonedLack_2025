import streamlit as st
import pandas as pd
from supabase import create_client, Client

#### Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)


#### Hilfsfunktion: alle Seiten laden
def fetch_all(table: str, filters: list = None, page_size: int = 1000) -> pd.DataFrame:
    """
    Lädt alle Datensätze aus einer Supabase-Tabelle über Paging.
    
    :param table: Tabellenname
    :param filters: Liste mit Filterfunktionen (z.B. [lambda q: q.eq("season", 2025)])
    :param page_size: Anzahl Datensätze pro Page
    :return: Pandas DataFrame
    """
    all_data = []
    start = 0

    while True:
        query = supabase.table(table).select("*").range(start, start + page_size - 1)
        
        # Filter anhängen
        if filters:
            for f in filters:
                query = f(query)
        
        resp = query.execute()
        data = resp.data

        if not data:
            break

        all_data.extend(data)
        start += page_size

    return pd.DataFrame(all_data)


#### LOAD LEAGUES
@st.cache_data(ttl=24*60*60)
def load_leagues():
    return fetch_all("leagues")


@st.cache_data(ttl=24*60*60)
def load_leagues_with_type(type: str):
    return fetch_all("leagues", filters=[lambda q: q.eq("league_type", type)])


#### LOAD MANAGERS
@st.cache_data(ttl=5*60)
def load_managers():
    return fetch_all("managers")


#### LOAD MATCHUPS
@st.cache_data(ttl=5*60)
def load_matchups():
    return fetch_all("matchup_week_stats")


@st.cache_data(ttl=5*60)
def load_weekly_matchups(week: int):
    return fetch_all("matchup_week_stats", filters=[lambda q: q.eq("week", week)])


#### LOAD DRAFTS
@st.cache_data(ttl=15*60)
def load_season_drafts(season: int):
    return fetch_all("drafts", filters=[lambda q: q.eq("season", season)])

@st.cache_data(ttl=15*60)
def load_draftpicks():
    return fetch_all("draft_picks")

#### LOAD ROSTERS
@st.cache_data(ttl=5*60)
def load_rosters():
    return fetch_all("rosters")