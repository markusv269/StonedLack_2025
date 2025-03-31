import streamlit as st
from sleeper_wrapper import League, User
import pandas as pd
from config import DYNLEAGUES

st.write(
    '''
    # Stoned Lack Dynastys coming! _Soon!_
    
    '''
)

dynasty_leagues = DYNLEAGUES

league_overview = {}

for league_id in dynasty_leagues:
    user_name = ""
    league = League(league_id)
    league_data = league.get_league()
    roster_data = league.get_rosters()
    champ = league_data["metadata"].get("latest_league_winner_roster_id",None)
    if champ:
        owner_id = next((entry["owner_id"] for entry in roster_data if entry["roster_id"] == int(champ)), None)
        user = User(owner_id)
        user_name = user.get_display_name()
    if league_data['name'] not in league_overview.keys():
        league_overview[league_data['name']] = [league_data['league_id'], league_data["avatar"], league_data["season"], user_name]
    

league_df = pd.DataFrame(league_overview).T.reset_index(drop=False).rename(columns={"index":"Liga", 0:"League-ID", 1:"avatar", 2:"Saison", 3:"Amt. Champion"})
league_df["avatar_url"] = "https://sleepercdn.com/avatars/" + league_df["avatar"].astype(str)

st.write('''
    ### Die Stoned Lack Dynasty-Ligen
    ''')
st.dataframe(
    league_df[["avatar_url", "Liga", 'Amt. Champion', "Saison"]],
    column_config={"avatar_url": st.column_config.ImageColumn(" ")},
    hide_index=True
)



