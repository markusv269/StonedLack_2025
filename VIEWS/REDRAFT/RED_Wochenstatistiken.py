import streamlit as st
# from tools.methods import load_matchups, load_players, load_rosters, load_scoring_settings, load_users, get_matchup_results

import requests
import graphviz

users_df = st.session_state["session_data"]["userdf"]
matchups_df = st.session_state["session_data"]["matchupsdf"]
rosters_df = st.session_state["session_data"]["rostersdf"]
rosters_df = rosters_df.merge(users_df, on=['league_id', 'roster_id'], how='left')

st.title("Wöchentliche Statistiken")
weeklystats_show = rosters_df[['league_name', 'display_name', 'week', 'wins','losses', 'ties', 'fpts', 'fpts_against', 'ppts']]
weeklystats_show['St/Sit-Acc. [%]'] = round(weeklystats_show['fpts'] / weeklystats_show['ppts'] * 100,2)
weekly_league = st.selectbox('Wähle Liga:', weeklystats_show['league_name'].unique())
weekly_week = st.selectbox('Wähle Woche:', weeklystats_show['week'].unique())
weeklystats_show = weeklystats_show.rename(columns={
    'league_name':'Liga',
    'display_name':'Manager',
    'week':'Woche',
    'wins':'W',
    'losses':'L',
    'ties':'T',
    'fpts':'FPTS for',
    'fpts_against':'FPTS against',
    'ppts':'Max PF'
})
if weekly_week != None and weekly_league != None:
    filtered_weekly = weeklystats_show[(weeklystats_show['Woche']==weekly_week) & (weeklystats_show['Liga']==weekly_league)]
else:
    filtered_weekly = weeklystats_show
filtered_weekly = filtered_weekly.sort_values(by=['W', 'FPTS for'], ascending=False).reset_index(drop=True)
st.dataframe(filtered_weekly.set_index(["Liga", "Woche"]), hide_index=True, height=460, width=1000)

def get_team_info(lid, rid, rnum, matchups):
    week = 14 + rnum
    match = matchups[
        (matchups["league_id"] == lid) &
        (matchups["roster_id"] == rid) &
        (matchups["week"] == week)
    ]
    
    if not match.empty:
        return match.iloc[0]["display_name"], match.iloc[0]["points"]
    return "Unknown", 0  # Falls keine Daten gefunden werden

def build_bracket_graph(data, league_id, matchups_df):
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR', nodesep='0.9', ranksep='1.2')  # Erhöht Abstände zwischen Nodes

    for match in data:
        match_id = match["m"]
        round_num = match["r"]
        place = match.get("p")

        team1_id = match["t1"]
        team2_id = match["t2"]

        team1_name, team1_points = get_team_info(league_id, team1_id, round_num, matchups_df)
        team2_name, team2_points = get_team_info(league_id, team2_id, round_num, matchups_df)

        # HTML-Label mit fettem Teamnamen und normalem Punktestand
        label = f"""<<B>Week {14+round_num}</B><BR/><BR/><B>{team1_name}</B> ({team1_points})<BR/><B>{team2_name}</B> ({team2_points})>"""

        if place is not None:
            label = f"""<<B>Week {14+round_num} (Spiel um Platz {place})</B><BR/><BR/><B>{team1_name}</B> ({team1_points})<BR/><B>{team2_name}</B> ({team2_points})>"""

        # Füge Knoten mit Stil hinzu
        dot.node(f"M{match_id}", label=label, shape="box", style="filled", fillcolor="#f8f9fa", fontsize="12")

        # Verbindungslinien für vorherige Matches
        if "t1_from" in match:
            prev_match = match["t1_from"]
            if "w" in prev_match:
                dot.edge(f"M{prev_match['w']}", f"M{match_id}", color="black", penwidth="2")
            elif "l" in prev_match:
                dot.edge(f"M{prev_match['l']}", f"M{match_id}", style="dashed", color="gray")

        if "t2_from" in match:
            prev_match = match["t2_from"]
            if "w" in prev_match:
                dot.edge(f"M{prev_match['w']}", f"M{match_id}", color="black", penwidth="2")
            elif "l" in prev_match:
                dot.edge(f"M{prev_match['l']}", f"M{match_id}", style="dashed", color="gray")
    return dot

# Bestimme die league_id anhand der ausgewählten Liga
league_ids = rosters_df.loc[rosters_df['league_name'] == weekly_league, 'league_id'].unique()
if len(league_ids) > 0:
    league_id = league_ids[0]
else:
    st.error("Keine gültige Liga-ID gefunden.")
    st.stop()

# API-Aufruf zur Abfrage des Playoff-Brackets
winner_url = f"https://api.sleeper.app/v1/league/{league_id}/winners_bracket"
loser_url = f"https://api.sleeper.app/v1/league/{league_id}/losers_bracket"
winner_response = requests.get(winner_url)
loser_respone = requests.get(loser_url)

if winner_response.status_code == 200:
    winner_bracket_data = winner_response.json()
else:
    st.error(f"Fehler beim Abrufen der Playoff-Daten: {winner_response.status_code}")
    st.stop() 
if loser_respone.status_code == 200:
    loser_bracket_data = loser_respone.json()
else:
    st.error(f"Fehler beim Abrufen der Playoff-Daten: {loser_respone.status_code}")
    st.stop() 
winner_graph = build_bracket_graph(winner_bracket_data, league_id, matchups_df)
loser_graph = build_bracket_graph(loser_bracket_data, league_id, matchups_df)
winner_graph.graph_attr.update({'rankdir': 'LR'})
loser_graph.graph_attr.update({'rankdir': 'LR'})
st.title("Playoff Picture")
st.graphviz_chart(winner_graph)
st.title("Toilet Bowl")
st.graphviz_chart(loser_graph)