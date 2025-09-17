import streamlit as st
from .supabase_client import fetch_all


# --- LEAGUES ---
@st.cache_data(ttl=24 * 60 * 60)
def load_leagues():
    return fetch_all("leagues")


@st.cache_data(ttl=24 * 60 * 60)
def load_leagues_with_type(league_type: str):
    return fetch_all("leagues", filters=[lambda q: q.eq("league_type", league_type)])


# --- MANAGERS ---
@st.cache_data(ttl=5 * 60)
def load_managers():
    return fetch_all("managers")


# --- MATCHUPS ---
@st.cache_data(ttl=5 * 60)
def load_matchups():
    return fetch_all("matchup_week_stats")


@st.cache_data(ttl=5 * 60)
def load_weekly_matchups(week: int):
    return fetch_all("matchup_week_stats", filters=[lambda q: q.eq("week", week)])


# --- DRAFTS ---
@st.cache_data(ttl=15 * 60)
def load_season_drafts(season: int):
    return fetch_all("drafts", filters=[lambda q: q.eq("season", season)])


@st.cache_data(ttl=15 * 60)
def load_draftpicks():
    return fetch_all("draft_picks")


# --- ROSTERS ---
@st.cache_data(ttl=5 * 60)
def load_rosters():
    return fetch_all("rosters")
