import streamlit as st
import supabase
import pandas as pd
from supabase import create_client, Client

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)
# Daten aus der Supabase-Tabelle abrufen
matchups = supabase.rpc("get_matchup_starters").execute()
# league_settings = supabase.table("leagues").select("*").execute()
# st.write("### Matchups")
# st.dataframe(pd.DataFrame(matchups.data))
# for matchup in matchups.data:
#     st.write("Starter")
#     for player in matchup['json_data'].get('starters', []):
#         st.write(player)
#     st.write("---")
#     st.write("Bench")
#     for player in matchup['json_data'].get('starters', []):
#         st.write(player)
#     st.write("---")

import pandas as pd

# Beispiel: df ist dein DataFrame mit den Rohdaten
# Spalten (basierend auf deinem Dump): 
# ["matchup_uid", "player_idx", "league_name", "league_type", "league_id", "matchup_id", "slot", "position", "player_id", "player_name", "team", "points"]
df = pd.DataFrame(matchups.data)

st.write(df)

import streamlit as st
import pandas as pd

# df: dein DataFrame mit den Rohdaten
# Spalten: ["league_id","matchup_id","roster_id","player_name","player_points","player_position"]

# Alle eindeutigen Matchups
matchup_ids = df[['league_id','matchup_id']].drop_duplicates()

import streamlit as st
import pandas as pd

# df: dein DataFrame mit den Rohdaten
# Spalten: ["league_id","matchup_id","roster_id","player_name","player_points","slot"]

# Alle eindeutigen Matchups
matchup_ids = df[['league_id','matchup_id']].drop_duplicates()

for _, matchup in matchup_ids.iterrows():
    league_id = matchup['league_id']
    matchup_id = matchup['matchup_id']
    # league_name = matchup['league_name']  # Falls du den Namen der Liga hast, ersetze dies entsprechend
    
    st.write(f"**League {league_id} – Matchup {matchup_id}**")
    
    # Spieler der beiden Rosters filtern
    rosters = df[(df['league_id']==league_id) & (df['matchup_id']==matchup_id)]
    roster_ids = rosters['roster_id'].unique()
    
    if len(roster_ids) != 2:
        st.warning(f"Matchup {matchup_id} hat nicht genau 2 Roster!")
        continue
    
    roster1 = rosters[rosters['roster_id']==roster_ids[0]].sort_values('slot')
    roster2 = rosters[rosters['roster_id']==roster_ids[1]].sort_values('slot')
    
    # Beide Roster auf gleiche Länge bringen
    max_len = max(len(roster1), len(roster2))
    roster1 = roster1.reindex(range(max_len))
    roster2 = roster2.reindex(range(max_len))
    
    # Streamlit Columns: Spieler1 | Punkte1 | Slot | Punkte2 | Spieler2
    for i in range(max_len):
        col1, col2, col3, col4, col5 = st.columns([2,1,1,1,2])
        col1.write(roster1['player_name'].iloc[i] if pd.notna(roster1['player_name'].iloc[i]) else "")
        col2.write(roster1['player_points'].iloc[i] if pd.notna(roster1['player_points'].iloc[i]) else "")
        col3.write(roster1['slot'].iloc[i] if pd.notna(roster1['slot'].iloc[i]) else "")
        col4.write(roster2['player_points'].iloc[i] if pd.notna(roster2['player_points'].iloc[i]) else "")
        col5.write(roster2['player_name'].iloc[i] if pd.notna(roster2['player_name'].iloc[i]) else "")
    
    st.markdown("---")  # Trennlinie zwischen Matchups
