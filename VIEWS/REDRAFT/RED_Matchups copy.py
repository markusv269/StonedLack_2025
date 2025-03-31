import streamlit as st

users_df = st.session_state["session_data"]["userdf"]
matchups_df = st.session_state["session_data"]["matchupsdf"]
matchups_df = matchups_df.merge(users_df[['league_id', 'roster_id', 'display_name', 'league_name']], on=['league_id', 'roster_id'], how='left')
rosters_df = st.session_state["session_data"]["rostersdf"]
players_df, players_dict = st.session_state["session_data"]["playersdf"], st.session_state["session_data"]["playersdict"]
matches_df = st.session_state["session_data"]["matchesdf"]

st.title('Matchup-Übersicht')

matches_show = matches_df[['league_name', 'week', 'winner_name', 'winner_points', 'loser_name', 'loser_points', 'winner_roster_id', 'loser_roster_id']]
matches_show = matches_show.rename(columns={
    'league_name' : 'Liga',
    'week' : 'Woche',
    'winner_name' : 'Gewinner',
    'winner_points' : 'Pkt. Gewinner',
    'loser_name' : 'Verlierer',
    'loser_points' : 'Pkt. Verlierer',
    'winner_roster_id': 'Winner_ID',
    'loser_roster_id': 'Loser_ID'
})

matches_show['Pkt. Summe'] = matches_show['Pkt. Gewinner'] + matches_show['Pkt. Verlierer']
matches_show['Pkt. Diff'] = matches_show['Pkt. Gewinner'] - matches_show['Pkt. Verlierer']

# Filter-UI
col1, col2, col3 = st.columns([1, 1, 1.6])

with col1:
    activate_league = st.checkbox("Ligafilter aktivieren", key="cb_league")
with col2:
    activate_week = st.checkbox("Wochenfilter aktivieren", key="cb_week")

with col1:
    select_league = st.selectbox("Wähle Liga", matches_show["Liga"].unique(), key="sel_league") if activate_league else None
with col2:
    select_week = st.selectbox("Wähle Woche", sorted(matches_show["Woche"].unique()), key="sel_week") if activate_week else None
with col3:
    select_manager = st.multiselect("Manager wählen", sorted(set(matches_show["Gewinner"]).union(set(matches_show["Verlierer"]))))

# Daten filtern
filtered_df = matches_show.copy()

if activate_league and select_league:
    filtered_df = filtered_df[filtered_df["Liga"] == select_league]

if activate_week and select_week:
    filtered_df = filtered_df[filtered_df["Woche"] == select_week]

if select_manager:
    filtered_df = filtered_df[filtered_df["Gewinner"].isin(select_manager) | filtered_df["Verlierer"].isin(select_manager)]

# Gefilterte Tabelle anzeigen
filtered_df = filtered_df.head(100)

st.write("### Matchups")

for _, matchup in filtered_df.iterrows():
    with st.expander(f"{matchup['Gewinner']} ({matchup['Pkt. Gewinner']:.2f}) vs. {matchup['Verlierer']} ({matchup['Pkt. Verlierer']:.2f})"):
        st.write(f"**Liga:** {matchup['Liga']} | **Woche:** {matchup['Woche']}")

        winner_roster = rosters_df[(rosters_df["league_id"] == matchup["Liga"]) & (rosters_df["roster_id"] == matchup["Winner_ID"])]
        loser_roster = rosters_df[(rosters_df["league_id"] == matchup["Liga"]) & (rosters_df["roster_id"] == matchup["Loser_ID"])]

        winner_players = {p: players_dict.get(p, {}) for p in winner_roster.iloc[0]["starters"]} if not winner_roster.empty else {}
        loser_players = {p: players_dict.get(p, {}) for p in loser_roster.iloc[0]["starters"]} if not loser_roster.empty else {}

        # Positionen extrahieren
        positions = set(winner_players.keys()).union(set(loser_players.keys()))
        positions = sorted(positions, key=lambda x: ["QB", "RB", "WR", "TE", "FLEX", "K", "DST"].index(x) if x in ["QB", "RB", "WR", "TE", "FLEX", "K", "DST"] else 99)

        col1, col2, col3 = st.columns([1.5, 1, 1.5])

        with col1:
            st.subheader(matchup["Gewinner"])
            for pos in positions:
                player = winner_players.get(pos, {}).get("full_name", "—")
                points = winner_players.get(pos, {}).get("points", 0)
                st.write(f"**{pos}:** {player} ({points:.2f})")

        with col2:
            st.write("### Positionen")
            for pos in positions:
                st.write(f"**{pos}**")

        with col3:
            st.subheader(matchup["Verlierer"])
            for pos in positions:
                player = loser_players.get(pos, {}).get("full_name", "—")
                points = loser_players.get(pos, {}).get("points", 0)
                st.write(f"**{pos}:** {player} ({points:.2f})")

        st.markdown("---")
