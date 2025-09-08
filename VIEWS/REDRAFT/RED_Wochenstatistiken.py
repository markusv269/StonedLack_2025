import streamlit as st
import pandas as pd
from supabase import create_client, Client
from methods import load_managers, load_leagues, load_weekly_matchups, load_leagues_with_type

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
        points1 = round(sum(roster1.get("json_data", {}).get("starters_points", [])),2)
        points2 = round(sum(roster2.get("json_data", {}).get("starters_points", [])),2)

        weekly_points.append({
            "matchup_id": matchup[1],
            "league_id": matchup[0],
            "roster1_id": roster1["roster_id"],
            "roster2_id": roster2["roster_id"],
            "points1": points1,
            "points2": points2,
            "total_points": round(points1 + points2,2),
            "winner_points": round(max(points1, points2),2),
            "loser_points": round(min(points1, points2),2),
            "point_diff": round(abs(points1 - points2),2),
            "winner": roster1["roster_id"] if points1 > points2 else roster2["roster_id"],
            "loser": roster2["roster_id"] if points1 > points2 else roster1["roster_id"],
        })

    return pd.DataFrame(weekly_points)

# ░░░ STREAMLIT ░░░
st.title("Wochenstatistiken SLR2025")

week_select = st.number_input("Woche wählen", min_value=1, step=1)

matchups_df = load_weekly_matchups(week_select)
managers_df = load_managers()
leagues_df = load_leagues_with_type("redraft")

df_points = build_weekly_points(matchups_df, week_select)
# df_points = df_points.merge(managers_df.add_suffix("_1"), left_on="roster1_id", right_on="roster_id_1")
# df_points = df_points.merge(managers_df.add_suffix("_2"), left_on="roster2_id", right_on="roster_id_2")
df_points = df_points.merge(leagues_df[["league_id", "league_name"]], on="league_id")
df_points = df_points.merge(managers_df.add_suffix("_1"), left_on=["league_id", "roster1_id"], right_on=["league_id_1", "roster_id_1"])
df_points = df_points.merge(managers_df.add_suffix("_2"), left_on=["league_id", "roster2_id"], right_on=["league_id_2", "roster_id_2"])
df_points["winner_name"] = df_points.apply(lambda row: row["display_name_1"] if row["winner"] == row["roster1_id"] else row["display_name_2"], axis=1)
df_points["loser_name"] = df_points.apply(lambda row: row["display_name_1"] if row["loser"] == row["roster1_id"] else row["display_name_2"], axis=1)

knappstes_matchup = df_points.loc[df_points["point_diff"].idxmin()]
klatsche = df_points.loc[df_points["point_diff"].idxmax()]
high_scoring = df_points.loc[df_points["total_points"].idxmax()]
unlucky_loser = df_points.loc[df_points["loser_points"].idxmax()]
low_scoring = df_points.loc[df_points["total_points"].idxmin()]
lucky_winner = df_points.loc[df_points["winner_points"].idxmin()]
top_roster = matchups_df[matchups_df["week"] == week_select].copy()
top_roster = top_roster.merge(managers_df, on=["league_id", "roster_id"])
top_roster = top_roster[top_roster["league_id"].isin(leagues_df[leagues_df["league_type"]=="redraft"]["league_id"])]
top_roster = top_roster.merge(leagues_df[["league_id", "league_name"]], on="league_id")
# st.dataframe(managers_df)

st.write(f"#### Knappstes Matchup")
st.write(f"**{klatsche['league_name']}**")
col1, col2, col3 = st.columns([3,1,3])
with col1:
    st.metric(label=knappstes_matchup['winner_name'], value=round(knappstes_matchup['winner_points'],2), delta=f"{round(knappstes_matchup['point_diff'],2)}")
with col2:
    st.write("")
with col3:
    st.metric(label=knappstes_matchup['loser_name'], value=round(knappstes_matchup['loser_points'],2), delta=f"-{round(knappstes_matchup['point_diff'],2)}")
st.write("---")

st.write(f"#### Unglücklichster Verlierer ({unlucky_loser['loser_name']}, {round(unlucky_loser['loser_points'],2)} Punkte)")
st.write(f"**{unlucky_loser['league_name']}**")
col1, col2, col3 = st.columns([3,1,3])
with col1:
    st.metric(label=unlucky_loser['loser_name'], value=round(unlucky_loser['loser_points'],2), delta=f"-{round(unlucky_loser['point_diff'],2)}")
with col2:
    st.write("")
with col3:
    st.metric(label=unlucky_loser['winner_name'], value=round(unlucky_loser['winner_points'],2), delta=f"{round(unlucky_loser['point_diff'],2)}")
st.write("---")

st.write(f"#### Glücklichster Gewinner ({lucky_winner['winner_name']}, {round(lucky_winner['winner_points'],2)} Punkte)")
st.write(f"**{lucky_winner['league_name']}**")
col1, col2, col3 = st.columns([3,1,3])
with col1:
    st.metric(label=lucky_winner['winner_name'], value=round(lucky_winner['winner_points'],2), delta=f"{round(lucky_winner['point_diff'],2)}")
with col2:
    st.write("")
with col3:
    st.metric(label=lucky_winner['loser_name'], value=round(lucky_winner['loser_points'],2), delta=f"-{round(lucky_winner['point_diff'],2)}")
st.write("---")

st.write(f"#### High-Scoring Matchup (Gesamtpunkte: {round(high_scoring['total_points'],2)})")
st.write(f"**{high_scoring['league_name']}**")
col1, col2, col3 = st.columns([3,1,3])
with col1:
    st.metric(label=high_scoring['display_name_1'], value=round(high_scoring['points1'],2))
with col2:
    st.write("")
with col3:
    st.metric(label=high_scoring['display_name_2'], value=round(high_scoring['points2'],2))
st.write("---")

st.write(f"#### Low-Scoring Matchup (Gesamtpunkte: {round(low_scoring['total_points'],2)})")
st.write(f"**{low_scoring['league_name']}**")
col1, col2, col3 = st.columns([3,1,3])
with col1:
    st.metric(label=low_scoring['display_name_1'], value=round(low_scoring['points1'],2))
with col2:
    st.write("")
with col3:
    st.metric(label=low_scoring['display_name_2'], value=round(low_scoring['points2'],2))
st.write("---")

st.write(f"#### Größte Klatsche")
st.write(f"**{klatsche['league_name']}**")
col1, col2, col3 = st.columns([3,1,3])
with col1:
    st.metric(label=klatsche['winner_name'], value=round(klatsche['winner_points'],2), delta=f"{round(klatsche['point_diff'],2)}")
with col2:
    st.write("")
with col3:
    st.metric(label=klatsche['loser_name'], value=round(klatsche['loser_points'],2), delta=f"-{round(klatsche['point_diff'],2)}")
st.write("---")

st.write("#### Top 5 Roster der Woche")
select_top = st.slider("Anzahl Top-Roster anzeigen", min_value=1, value=5, step=1)
for idx, row in top_roster.sort_values(by="points", ascending=False).head(select_top).iterrows():
    col1, col2, col3 = st.columns([1,3,2])
    with col1:
        st.write(f"**{row['points']}**")
    with col2:
        teamname = f"*({row['team_name']})*" if row['team_name'] else ""
        st.write(f"**{row['display_name']}** {teamname}")
    with col3:
        st.write(row['league_name'])
    st.write("---")

st.write("### Alle Matchups der Woche")
st.dataframe(df_points[["league_name", "winner_name", "winner_points", "loser_name", "loser_points", "total_points", "point_diff"]].sort_values(by="total_points", ascending=False), use_container_width=True, hide_index=True)      