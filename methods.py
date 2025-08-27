import streamlit as st
import pandas as pd
from supabase import create_client, Client

#### Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

#### LOAD LEAGUES
@st.cache_data(ttl=24*60*60) # 1 Tag cachen
def load_leagues():
    leagues = supabase.table("leagues").select("*").execute()
    return pd.DataFrame(leagues.data)

@st.cache_data(ttl=24*60*60) # 1 Tag cachen
def load_leagues_with_type(type: str):
    leagues = supabase.table("leagues").select("*").eq("league_type", type).execute()
    return pd.DataFrame(leagues.data)



#### LOAD MANAGERS
@st.cache_data(ttl=5*60) # 5 Minuten cachen
def load_managers():
    managers = supabase.table("managers").select("*").execute()
    return pd.DataFrame(managers.data)



#### LOAD MATCHUPS
@st.cache_data(ttl=5*60) # 5 Minuten cachen
def load_matchups():
    matchups = supabase.table("matchup_week_stats").select("*").execute()
    return pd.DataFrame(matchups.data)

@st.cache_data(ttl=5*60) # 5 Minuten cachen
def load_weekly_matchups(week: int):
    matchups = supabase.table("matchup_week_stats").select("*").eq("week", week).execute()
    return pd.DataFrame(matchups.data)


#### LOAD DRAFTS
@st.cache_data(ttl=5*60) # 15 Minuten cachen
def load_season_drafts(season: int):
    drafts = supabase.table("drafts").select("*").eq("season", season).execute()
    return pd.DataFrame(drafts.data)