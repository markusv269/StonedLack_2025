
from sleeper_wrapper import User, League
import streamlit as st
from supabase import create_client, Client
import pandas as pd
from config import REDLEAGUES_2025

# leagues = REDLEAGUES_2025
# name_link_dict = {league.name: league.invite_link for league in leagues.values()}

# # Supabase-Konfiguration
# SUPABASE_URL = st.secrets["supabase"]["url"]
# SUPABASE_KEY = st.secrets["supabase"]["key"]
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# auslosung = supabase.table("Auslosung").select("*").execute()
# auslosung_df = pd.DataFrame(auslosung.data)

# anmeldung = supabase.table("SLR2025").select("*").execute()
# anmeldung_df = pd.DataFrame(anmeldung.data)

# auslosung_df_long = auslosung_df.melt(id_vars=["league_name"], var_name="draft_pos", value_name="sleeper_name")

# mail_df = anmeldung_df.merge(auslosung_df_long, left_on="Sleeper", right_on="sleeper_name", how="left")
# mail_df["invite_link"] = mail_df["league_name"].map(name_link_dict)

# print(mail_df)

username = "nakedchef"
user = User(username)
user_leagues = user.get_all_leagues(season=2025, sport="nfl")
for league in user_leagues:
    league_id = league.get("league_id")
    league_name = League(league_id).get_league_name()
    print(league_id, league_name)