import streamlit as st
import pandas as pd
from supabase import create_client, Client
from methods import load_managers, load_leagues, load_weekly_matchups

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# Matchups laden

def build_weekly_points(matchups_df, week):
    df_week = matchups_df[matchups_df["week"] == week]
    weekly_points = []

    for matchup, group in df_week.groupby(["league_id", "matchup_id"]):
        if len(group) != 2:
            continue  # nur vollständige Matchups
        roster1, roster2 = group.iloc[0], group.iloc[1]
        points1 = sum(roster1.get("json_data", {}).get("starter_points", []))
        points2 = sum(roster2.get("json_data", {}).get("starter_points", []))

        weekly_points.append({
            "matchup_id": matchup[1],
            "league_id": matchup[0],
            "roster1_id": roster1["roster_id"],
            "roster2_id": roster2["roster_id"],
            "points1": points1,
            "points2": points2,
            "total_points": points1 + points2,
            "winner_points": max(points1, points2),
            "loser_points": min(points1, points2),
            "point_diff": abs(points1 - points2)
        })

    return pd.DataFrame(weekly_points)

# ░░░ STREAMLIT ░░░
st.title("Knappstes & High-Scoring Matchup der Woche")

week_select = st.number_input("Woche wählen", min_value=1, step=1)

matchups_df = load_weekly_matchups(week_select)
managers_df = load_managers()
leagues_df = load_leagues()

df_points = build_weekly_points(matchups_df, week_select)
# df_points = df_points.merge(managers_df.add_suffix("_1"), left_on="roster1_id", right_on="roster_id_1")
# df_points = df_points.merge(managers_df.add_suffix("_2"), left_on="roster2_id", right_on="roster_id_2")
df_points = df_points.merge(leagues_df[["league_id", "league_name"]], on="league_id")

lucky_winner = df_points.loc[df_points["point_diff"].idxmin()]
high_scoring = df_points.loc[df_points["total_points"].idxmax()]
unlucky_loser = df_points.loc[df_points["loser_points"].idxmax()]
low_scoring = df_points.loc[df_points["total_points"].idxmin()]
st.subheader(f"Knappstes Matchup der Woche {week_select} (Punktdifferenz: {lucky_winner['point_diff']})")

st.dataframe(lucky_winner[['league_name', 'roster1_id', 'points1', 'roster2_id', 'points2']])
