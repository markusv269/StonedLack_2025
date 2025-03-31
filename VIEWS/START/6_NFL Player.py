import streamlit as st
import os
import json
import pandas as pd
from tools.methods import load_matchups, load_players, load_rosters, load_scoring_settings, load_users, get_matchup_results

users_df = load_users()
matchups_df = load_matchups()
matchups_df = matchups_df.merge(users_df[['league_id', 'roster_id', 'display_name', 'league_name']], on=['league_id', 'roster_id'], how='left')
rosters_df = load_rosters()
players_df, players_dict = load_players()
matches_df = get_matchup_results(matchdf=matchups_df, userdf=users_df)
scoring_settings = load_scoring_settings()

st.write('Hier gibt es noch nichts zu sehen. Stay tuned!')

def calculate_fantasy_points(stats, scoring_settings):
    """Berechnet Fantasy-Punkte basierend auf stats und scoring_settings."""
    return sum(stats.get(stat, 0) * scoring_settings.get(stat, 0) for stat in scoring_settings.keys())

def load_player_data(json_file, scoring_settings, is_projection=True):
    """Lädt relevante Spielerstatistiken aus einer JSON-Datei (Projections oder Stats)."""
    if not os.path.exists(json_file):
        # print(f"❌ Datei nicht gefunden: {json_file}")
        return {}

    with open(json_file, 'r') as f:
        data = json.load(f)

    player_data = {}

    if is_projection:
        # Projections sind Listen mit Dictionaries
        if isinstance(data, list):
            for entry in data:
                player_id = entry.get("player_id")
                stats = entry.get("stats", {})

                # Nur relevante Stats extrahieren
                filtered_stats = {stat: value for stat, value in stats.items() if stat in scoring_settings}

                if player_id and filtered_stats:
                    player_data[player_id] = filtered_stats
        else:
            None
            # print(f"⚠ Unerwartetes JSON-Format in {json_file} für Projections")

    else:
        # Stats sind Dictionaries mit player_id als Schlüssel
        if isinstance(data, dict):
            for player_id, stats in data.items():
                filtered_stats = {stat: value for stat, value in stats.items() if stat in scoring_settings}

                if filtered_stats:
                    player_data[player_id] = filtered_stats
        else:
            None
            # print(f"⚠ Unerwartetes JSON-Format in {json_file} für Stats")

    # print(f"✅ Geladene Spieler aus {json_file}: {len(player_data)} Spieler")
    return player_data

def create_combined_df(weeks, scoring_settings):
    """Erstellt ein DataFrame mit 'player_id' sowie proj und stats als Listen über alle Wochen."""
    all_data = {}

    for week in weeks:
        proj_file = f"sleeper_stats/projections/projection_{week}.json"
        stats_file = f"sleeper_stats/stats/stats_{week}.json"

        # Projections laden
        proj_stats = load_player_data(proj_file, scoring_settings, is_projection=True)
        for player_id, stats in proj_stats.items():
            if player_id not in all_data:
                all_data[player_id] = {"proj": [], "stats": []}  # Initialisierung
            all_data[player_id]["proj"].append(calculate_fantasy_points(stats, scoring_settings))

        # Tatsächliche Stats laden
        actual_stats = load_player_data(stats_file, scoring_settings, is_projection=False)
        for player_id, stats in actual_stats.items():
            if player_id not in all_data:
                all_data[player_id] = {"proj": [], "stats": []}  # Initialisierung
            all_data[player_id]["stats"].append(calculate_fantasy_points(stats, scoring_settings))

    # DataFrame erstellen
    df = pd.DataFrame.from_dict(all_data, orient="index").reset_index()
    df.rename(columns={"index": "player_id"}, inplace=True)

    return df

# Beispiel: Wochen 1-5
weeks = range(1, 19)

df_combined = create_combined_df(weeks, scoring_settings)

players_df = players_df.merge(df_combined, on='player_id', how='right')

# Ausgabe in Streamlit
players_show = players_df[['full_name', 'team', 'position', "stats", "proj"]]
# players_show['fpts_total'] = players_show[[f"stats_{week}" for week in weeks]].sum(axis=1)
# players_show['proj_total'] = players_show[[f"proj_{week}" for week in weeks]].sum(axis=1)

players_show = players_show.dropna(subset=['full_name'], axis=0)

def display_df(df):
    st.dataframe(
        df,
        column_order=[
            column
            for column in list(df.columns)
            if column in [
                'full_name',
                'team',
                'position',
                "stats",
                "proj"
            ]
        ],
        column_config={
            "stats": st.column_config.AreaChartColumn(
                "Stats",
                width="medium",
                help="Fantasy Points per Week"),
            "proj": st.column_config.AreaChartColumn(
                "Projection",
                width="medium",
                help="Projected Fantasy Points per Week"),
        },
        hide_index=True,
        height=2500
    )
display_df(players_show)