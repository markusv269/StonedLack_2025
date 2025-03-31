import streamlit as st

users_df = st.session_state["session_data"]["userdf"]
matchups_df = st.session_state["session_data"]["matchupsdf"]
matchups_df = matchups_df.merge(users_df[['league_id', 'roster_id', 'display_name', 'league_name']], on=['league_id', 'roster_id'], how='left')
rosters_df = st.session_state["session_data"]["rostersdf"]

players_df, players_dict = st.session_state["session_data"]["playersdf"], st.session_state["session_data"]["playersdict"]
matches_df = st.session_state["session_data"]["matchesdf"]

st.title('Matchup-Übersicht')
st.write('''Übersicht über alle Matchups. Filter nach Woche, Liga oder bestimmten Manager (zeigt alle gewonnenen und verlorernen Spiele).
            \n_Aus Performance-Gründen werden maximal 100 Matchups angezeigt._''')

matches_show = matches_df[['league_name', 'week', 'winner_name', 'winner_points', 'loser_name', 'loser_points']]
matches_show = matches_show.rename(columns={
    'league_name' : 'Liga',
    'week' : 'Woche',
    'winner_name' : 'Gewinner',
    'winner_points' : 'Pkt. Gewinner',
    'loser_name' : 'Verlierer',
    'loser_points' : 'Pkt. Verlierer'        
})
matches_show['Pkt. Summe'] = matches_show['Pkt. Gewinner'] + matches_show['Pkt. Verlierer']
matches_show['Pkt. Diff'] = matches_show['Pkt. Gewinner'] - matches_show['Pkt. Verlierer']
   
   
# Filter-UI
ucol1, ucol2, ucol3 = st.columns([1, 1, 1.6])
dcol1, dcol2, dcol3 = st.columns([1, 1, 1.6])

with ucol1:
    activate_league = st.checkbox("Ligafilter aktivieren", key="cb_league")
with ucol2:
    activate_week = st.checkbox("Wochenfilter aktivieren", key="cb_week")

# Bedingte Filteroptionen
with dcol1:
    select_league = st.selectbox("Wähle Liga", matches_show["Liga"].unique(), key="sel_league") if activate_league else None
with dcol2:
    select_week = st.selectbox("Wähle Woche", sorted(matches_show["Woche"].unique()), key="sel_week") if activate_week else None
with dcol3:
    select_manager = st.multiselect("Manager wählen", sorted(set(matches_show["Gewinner"]).union(set(matches_show["Verlierer"]))))

# Daten filtern
filtered_df = matches_show.copy()

if activate_league and select_league:
    filtered_df = filtered_df[filtered_df["Liga"] == select_league]

if activate_week and select_week:
    filtered_df = filtered_df[filtered_df["Woche"] == select_week]

if select_manager:
    filtered_df = filtered_df[filtered_df["Gewinner"].isin(select_manager) | filtered_df["Verlierer"].isin(select_manager)]

# Dynamische Spaltenauswahl
column_order = [col for col in filtered_df.columns if col not in (["Liga"] if activate_league else []) + (["Woche"] if activate_week else [])]

# Gefilterte Tabelle anzeigen
# st.dataframe(filtered_df, column_order=column_order, hide_index=True)
filtered_df = filtered_df.head(100)

st.write("### Matchups")
matchups_per_row = 4
rows = [filtered_df.iloc[i:i+matchups_per_row] for i in range(0, len(filtered_df), matchups_per_row)]

for row in rows:
    cols = st.columns(matchups_per_row)
    for col, (_, matchup) in zip(cols, row.iterrows()):
        with col:
            st.markdown(
                f"""
                <div style="border:1px solid #ddd; border-radius:10px; padding:10px; text-align:center; background-color:#f9f9f9;">
                    <div style="font-size:11px; font-weight:bold; color:#555;">{matchup['Liga']} - Woche {matchup['Woche']}</div>
                    <hr style="margin:5px 0; border-top:1px solid #ddd;">
                    <div style="font-size:16px; font-weight:bold; color:#28a745;">{matchup['Gewinner']}</div>
                    <div style="font-size:13px; color:gray;">{matchup['Pkt. Gewinner']:.2f}</div>
                    <div style="font-size:20px; font-weight:bold;">:</div>
                    <div style="font-size:13px; color:gray;">{matchup['Pkt. Verlierer']:.2f}</div>
                    <div style="font-size:16px; font-weight:bold; color:#dc3545;">{matchup['Verlierer']}</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
# st.subheader("Alle Matchups eines Managers")