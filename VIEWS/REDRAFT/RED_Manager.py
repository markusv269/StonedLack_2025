import streamlit as st
from tools.methods import load_matchups, load_players, load_rosters, load_users, get_matchup_results

users_df = st.session_state["session_data"]["userdf"]
matchups_df = st.session_state["session_data"]["matchupsdf"]
matchups_df = matchups_df.merge(users_df[['league_id', 'roster_id', 'display_name', 'league_name']], on=['league_id', 'roster_id'], how='left')
rosters_df = st.session_state["session_data"]["rostersdf"]

st.title('SLR Manager')

# st.selectbox()
user_show = users_df[['league_name', 'display_name', 'roster_id', 'draft_pos', 'league_id']]
user_show['URL'] = user_show.apply(lambda x: f'<a href="https://sleeper.com/roster/{x["league_id"]}/{x["roster_id"]}" target="_blank">Roster Link</a>', axis=1)
user_show = user_show.rename(columns={
    'league_name': 'Liga',
    'display_name': 'Manager',
    'roster_id': 'Roster-ID',
    'draft_pos': 'Draftposition'
})
selected_leagues = st.multiselect("Ligen auswählen:", user_show['Liga'].unique(), default=[])

# Falls keine Liga ausgewählt ist, zeige den gesamten DataFrame
filtered_df = user_show if not selected_leagues else user_show[user_show['Liga'].isin(selected_leagues)]
filtered_df = filtered_df.drop(columns=['league_id'])

# Dataframe anzeigen
# st.dataframe(filtered_df, hide_index=True)

st.markdown(filtered_df.to_html(escape=False, index=False), unsafe_allow_html=True)
