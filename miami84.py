
from sleeper_wrapper import User
import streamlit as st
from supabase import create_client, Client
import pandas as pd


# Supabase-Konfiguration
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

result = supabase.table("SLR2025").select("*").execute()
records = result.data

for record in records:
    user = User(record["Sleeper"])
    leagues = user.get_all_leagues(season=2025, sport="nfl")
    print(record["Sleeper"], len(leagues))