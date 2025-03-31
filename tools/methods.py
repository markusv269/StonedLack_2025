import streamlit as st
import pandas as pd
import numpy as np
import streamlit as st

def load_matchups():
    matchups = pd.read_parquet('DATA_PERMANENT/_2024/MATCHUPS/matchups.parquet', engine='pyarrow')
    matchups['starters'] = matchups['starters'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
    matchups['players'] = matchups['players'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
    matchups['bench'] = matchups.apply(lambda row: [p for p in row['players'] if p not in row['starters']], axis=1)
    matchups[['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'TE', 'FL', 'K', 'DEF']] = pd.DataFrame(matchups['starters'].to_list(), index=matchups.index)
    return matchups

def load_rosters():
    rosters = pd.read_parquet('DATA_PERMANENT/_2024/ROSTERS/rosters.parquet', engine='pyarrow')
    settings = rosters['settings'].apply(pd.Series)
    rosters = rosters.drop(columns=['settings']).join(settings)
    rosters['fpts'] = round(rosters['fpts'] + rosters['fpts_decimal'] / 100,2)
    rosters['fpts_against'] = round(rosters['fpts_against'] + rosters['fpts_against_decimal'] / 100,2)
    rosters['ppts'] = round(rosters['ppts'] + rosters['ppts_decimal'] / 100,2)
    rosters = rosters.drop(columns=['fpts_decimal', 'fpts_against_decimal', 'ppts_decimal', 'starters'])
    return rosters

def load_users():
    users = pd.read_parquet('data_changeable/users.parquet', engine='pyarrow')
    return users

def load_players():
    players = pd.read_json('data_changeable/players.json')
    players = players.T.reset_index(drop=True)
    players["full_name"] = players["full_name"].fillna(players["last_name"])
    player_dict = players.set_index("player_id")["full_name"].to_dict()
    return players, player_dict

def get_matchup_results(matchdf, userdf):
    matchups = matchdf.groupby(["league_id", "week", "matchup_id"]).apply(
        lambda x: pd.Series({
            "winner_roster_id": x.loc[x["points"].idxmax(), "roster_id"],
            "winner_points": x["points"].max(),
            "loser_roster_id": x.loc[x["points"].idxmin(), "roster_id"],
            "loser_points": x["points"].min()
        })
    ).reset_index()

    # Merge für Gewinner-Namen
    matchups = matchups.merge(userdf, left_on=["league_id", "winner_roster_id"], right_on=["league_id", "roster_id"], how="left")
    matchups = matchups.rename(columns={"display_name": "winner_name"}).drop(columns=["roster_id", 'league_name', 'user_id', 'draft_pos'])

    # Merge für Verlierer-Namen
    matchups = matchups.merge(userdf, left_on=["league_id", "loser_roster_id"], right_on=["league_id", "roster_id"], how="left")
    matchups = matchups.rename(columns={"display_name": "loser_name"}).drop(columns=["roster_id", 'user_id', 'draft_pos'])
    return matchups