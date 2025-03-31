import streamlit as st
# from tools.methods import load_matchups, load_players, load_rosters, load_users, get_matchup_results

st.title("Wochenkategorien")

matches_df = st.session_state["session_data"]["matchesdf"]
matchups_df = st.session_state["session_data"]["matchupsdf"]
players_df = st.session_state["session_data"]["playersdf"]
players_dict = {}
for index, row in players_df.iterrows():
    players_dict[row['player_id']] = f"{row['first_name'][:1]}. {row['last_name']}"

if not matches_df.empty:
    matches_df['pts_total'] = round(matches_df['winner_points'] + matches_df['loser_points'],2)
    matches_df['pts_diff'] = round(matches_df['winner_points'] - matches_df['loser_points'],2)
    select_week = st.selectbox("Woche auswählen", sorted(matches_df['week'].unique()), index=0)
    week_df = matches_df[matches_df['week'] == select_week]
    week_df = week_df[['league_name', 'winner_name', 'winner_points', 'loser_name', 'loser_points', 'pts_total', 'pts_diff']]
    week_df = week_df.rename(columns={
        'league_name':'Liga',
        'winner_name':'Gewinner',
        'winner_points':'Gewinner Pkt.',
        'loser_name':'Verlierer',
        'loser_points':'Verlierer Pkt.',
        'pts_total':'Matchup Pkt.',
        'pts_diff':'Pkt. Diff.'
    })

    def week_show(df, by, asc, n):
        st.dataframe(
            df.sort_values(by=by, ascending=asc).head(n).style.set_properties(subset=[by],
            **{'background-color': 'lightgray'}),
            hide_index=True,
            column_config={
                "Verlierer Pkt." : st.column_config.NumberColumn(
                    format="%.2f"
                    ),
                "Gewinner Pkt." : st.column_config.NumberColumn(
                    format="%.2f"
                    ),
                "Matchup Pkt." : st.column_config.NumberColumn(
                    format="%.2f"
                    ),
                "Pkt. Diff." : st.column_config.NumberColumn(
                    format="%.2f"
                    ),
                "Punkte": st.column_config.NumberColumn(
                    format="%.2f"
                    ),
            })

    # Shootout der Woche
    st.subheader('🔥 Shootout der Woche')
    week_show(week_df, "Matchup Pkt.", False, 1)

    # Klatsche der Woche
    st.subheader('💀 Klatsche der Woche')
    week_show(week_df,'Pkt. Diff.', False,1)
   
    
    # Nailbiter der Woche
    st.subheader('😱 Nailbiter der Woche')
    week_show(week_df,'Pkt. Diff.', True,1)
    
    # Top 5 Roster
    st.subheader('🏆 Top 5 Roster')
    top_roster_df = matchups_df[matchups_df['week']==select_week]
    # top_roster_df = top_roster_df.merge(users_df[['league_id', 'roster_id', 'display_name', 'league_name']], on=['league_id', 'roster_id'], how='left')
    top_roster_df = top_roster_df[['display_name', 'points', 'league_name', 'QB', 'RB1','RB2','WR1', 'WR2', 'TE', 'FL', 'K', 'DEF']].sort_values(by='points', ascending=False).head(5)
    top_roster_df = top_roster_df.rename(columns={
        'display_name':'Manager', 'points':'Punkte', 'league_name':'Liga'
    })
    for pos in ["QB", "RB1", "RB2", "WR1", "WR2", "TE", "FL", "K"]:
        top_roster_df[pos] = top_roster_df[pos].map(players_dict)
    week_show(top_roster_df,'Punkte', False,5)
else:
    st.warning("Keine Daten für die ausgewählte Woche verfügbar.")