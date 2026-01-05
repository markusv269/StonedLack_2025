import requests
from supabase import create_client, Client
import streamlit as st

# Supabase-Konfiguration
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_leagues(supabase):
    response = supabase.table("leagues") \
        .select("league_id") \
        .execute()

    return response.data

def update_league_champion(supabase, league_id, roster_id):
    supabase.table("leagues") \
        .update({"league_champion_rid": roster_id}) \
        .eq("league_id", league_id) \
        .execute()

def get_league_winner(league_id):
    res = requests.get(
        f"https://api.sleeper.app/v1/league/{league_id}/winners_bracket"
    )

    if res.status_code != 200:
        return None, None

    bracket = res.json()

    # Finale → p == 1
    final_game = next((g for g in bracket if g.get("p") == 1), None)

    if not final_game:
        return None, None

    roster_id = final_game.get("w")

    return roster_id

def update_all_league_champions(supabase):
    leagues = get_leagues(supabase)

    for league in leagues:
        league_id = league["league_id"]

        roster_id = get_league_winner(league_id)

        if roster_id is None:
            print(f"❌ Kein Champion gefunden für League {league_id}")
            continue

        update_league_champion(supabase, league_id, roster_id)
        # oder:
        # update_league_champion_name(supabase, league_id, display_name)

        print(f"✅ League {league_id}: Champion = {roster_id}")
update_all_league_champions(supabase)