import streamlit as st
import pandas as pd
import json
from DATA_PERMANENT._2024.COC.config import COC, scoring_settings, wc_round_player_by_id, div_round_player_by_id, conf_round_groups

with open("DATA_PERMANENT/_2024/COC/wc.json", encoding="utf-8") as f:
    WC_stats = json.load(f)
with open("DATA_PERMANENT/_2024/COC/dr.json", encoding="utf-8") as f:
    DR_stats = json.load(f)

# Umkehr-Mapping von Namen zu Spieler-IDs
player_name_to_id = {f"{p['last_name']}".strip(): p for p in wc_round_player_by_id.values()}

# DataFrame erstellen
teams_data = []
for tipper, players in COC['WC'].items():
    total_price = 0
    team_entry = {'Tipper': tipper}

    for pos, player_name in players.items():
        player_info = player_name_to_id.get(player_name)
        if player_info:
            team_entry[pos] = player_name
            team_entry[f"{pos}_Price"] = player_info['price']
            total_price += player_info['price']
        else:
            team_entry[pos] = "Unknown"
            team_entry[f"{pos}_Price"] = None
    
    team_entry['Total_Price'] = total_price
    team_entry['Valid_Tip'] = total_price <= 9
    teams_data.append(team_entry)

df_wc_teams = pd.DataFrame(teams_data)

# Fantasy-Punkte berechnen
for player_data in WC_stats:
    player_id = player_data['player_id']
    if player_id in wc_round_player_by_id:
        player_info = wc_round_player_by_id[player_id]
        fantasy_points = sum(player_data["stats"].get(stat, 0) * value for stat, value in scoring_settings.items())
        player_info['points'] = fantasy_points

# DataFrame mit Punkten aktualisieren
for pos in ['QB', 'RB', 'WR', 'TE']:
    df_wc_teams[f"{pos}_Points"] = df_wc_teams[pos].map(lambda x: player_name_to_id.get(x, {}).get('points', 0))

df_wc_teams['Wildcard Points'] = df_wc_teams[[f"{pos}_Points" for pos in ['QB', 'RB', 'WR', 'TE']]].sum(axis=1)

st.dataframe(df_wc_teams[['Tipper', 'Wildcard Points', 'Valid_Tip']].sort_values(by=['Wildcard Points'], ascending=[False]), hide_index=True)


# Umkehr-Mapping von Namen zu Spieler-IDs
player_name_to_id = {f"{p['last_name']}".strip(): p for p in div_round_player_by_id.values()}

# DataFrame erstellen
teams_data = []
for tipper, players in COC['DR'].items():
    total_price = 0
    team_entry = {'Tipper': tipper}

    for pos, player_name in players.items():
        player_info = player_name_to_id.get(player_name)
        if player_info:
            team_entry[pos] = player_name
            team_entry[f"{pos}_Price"] = player_info['price']
            total_price += player_info['price']
        else:
            team_entry[pos] = "Unknown"
            team_entry[f"{pos}_Price"] = None
    
    team_entry['Total_Price'] = total_price
    team_entry['Valid_Tip'] = total_price <= 9
    teams_data.append(team_entry)

df_dr_teams = pd.DataFrame(teams_data)

# Fantasy-Punkte berechnen
for player_data in DR_stats:
    player_id = player_data['player_id']
    if player_id in div_round_player_by_id:
        player_info = div_round_player_by_id[player_id]
        fantasy_points = sum(player_data["stats"].get(stat, 0) * value for stat, value in scoring_settings.items())
        player_info['points'] = fantasy_points

# DataFrame mit Punkten aktualisieren
for pos in ['QB', 'RB', 'WR', 'TE']:
    df_dr_teams[f"{pos}_Points"] = df_dr_teams[pos].map(lambda x: player_name_to_id.get(x, {}).get('points', 0))

df_dr_teams['Divisional Points'] = df_dr_teams[[f"{pos}_Points" for pos in ['QB', 'RB', 'WR', 'TE']]].sum(axis=1)

st.dataframe(df_dr_teams[['Tipper', 'Divisional Points', 'Valid_Tip']].sort_values(by=['Divisional Points'], ascending=[False]), hide_index=True)

df_teams_total = df_dr_teams[["Tipper", "Divisional Points"]].merge(df_wc_teams[["Tipper", "Wildcard Points"]], on="Tipper")
df_teams_total["Total"] = df_teams_total["Wildcard Points"] + df_teams_total["Divisional Points"]
st.dataframe(df_teams_total.sort_values(by="Total", ascending=False), hide_index=True)