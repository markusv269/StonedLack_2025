import streamlit as st
import pandas as pd
import json
from DATA_PERMANENT._2024.COC.config import COC, scoring_settings, wc_round_player, div_round_player, conf_round_player, super_bowl_player

# Benutzerdefinierte Sortierreihenfolge für Positionen
position_order = ["QB", "RB", "WR", "TE"]

# Funktion zum Hinzufügen des Preises aus den jeweiligen Runden
def add_price(player_id, round_player_data):
    # Iterate over the dictionary items: (player_name, player_info)
    for player_name, player_info in round_player_data.items():
        if player_info['player_id'] == player_id:
            return player_info['price']
    return 0  # Default value if the player isn't found

# Sortiere den DataFrame nach Position und Preis (absteigend)
def ind_calculate_fantasy_points_and_sort(json_file, round_player_data, scoring_settings):
    with open(json_file, encoding="utf-8") as f:
        stats_data = json.load(f)

    valid_player_ids = {data["player_id"] for data in round_player_data.values()}
    data = []

    # Spieler filtern und ihre Stats extrahieren
    for player in stats_data:
        if player["player_id"] in valid_player_ids:
            player_name = player['player'].get("first_name", "") + " " + player['player'].get("last_name", "")
            player_data = {
                "player_id": player["player_id"],
                "Spieler": player_name,  # Spielernamen hinzufügens
                "Position": player["player"]["position"],
                "Gruppe": player["team"],
                "FFP": 0
            }

            # Preis aus der Runde hinzufügen
            player_data["Preis"] = add_price(player["player_id"], round_player_data)

            # Fantasy-Punkte berechnen
            fantasy_points = 0
            for key, multiplier in scoring_settings.items():
                stat_value = player.get("stats", {}).get(key, 0)  # Falls Wert fehlt, setze 0
                player_data[key] = stat_value
                fantasy_points += stat_value * multiplier  # Punkte berechnen

            # Finalen Punktestand speichern
            player_data["FFP"] = round(fantasy_points, 2)  # Runden für bessere Lesbarkeit

            data.append(player_data)

    # DataFrame erstellen
    df = pd.DataFrame(data)

    # Position sortieren mit benutzerdefinierter Reihenfolge und Preis absteigend
    df["Position"] = pd.Categorical(df["Position"], categories=position_order, ordered=True)
    df = df.sort_values(by=["Position", "Preis"], ascending=[True, False])
    df = df[['player_id', "Spieler", "Position", "Gruppe", "FFP", "Preis"]].set_index("player_id")

    return df

# Streamlit-Setup
st.write("# Champ of Champs 2024")
st.write('''Das Champ of Champs-Spiel ist der Abschluss der StonedLack-Saison und kührt den Sieger aller Sieger aus den StonedLack-Ligen.
         Zugelassen waren dieses Jahr alle Champions aus den aktuellen Redraftligen (Saison 2024) sowie alle Dynasty-Champs der StonedLack Dynastys.

Die ersten drei Runden (Wild Card Weekend, Divisional Round und Conference Finals) bestanden aus dem $9-Game. Ziel ist, ein Team aus QB, RB, WR und TE zusammen zu stellen. Das Budget darf 9 Dollar nicht überschreiten. Die Werte der Spieler sind den Grafiken zu entnehmen. Als Besonderheit wurden bei den Conference Finals für die RB- und WR-Position jeweils Spielerpaare aus den Teams gewertet.

Im Superbowl wurden drei Spieler frei ihrer Position gewählt. Jeder Spieler hat einen Multiplikator, mit dem seine Fantasy-Punkte multipliziert werden.

In jeder Runde galt es, möglichst viele Punkte zu erreichen. Gesamtsieger ist der oder diejenige mit den meisten Punkten nach dem Superbowl.

Stonis Auswertung findet ihr im Discord im entsprechenden Kanal!
## Das Scoring''')
st.table(scoring_settings)



# Wild Card Weekend
st.write("## Wild Card Weekend")
st.write("### Tippbild")
st.image("Pictures/2024/CoC/WC.jfif", width=500)
wc_df = ind_calculate_fantasy_points_and_sort("DATA_PERMANENT/_2024/COC/wc.json", wc_round_player, scoring_settings)
st.write("### Fantasyergebnisse")
st.dataframe(wc_df[[column for column in wc_df.columns if column != "Gruppe"]], hide_index=True)

# Divisional Round
st.write("## Divisional Round")
st.write("### Tippbild")
st.image("Pictures/2024/CoC/DR.png", width=500)
dr_df = ind_calculate_fantasy_points_and_sort("DATA_PERMANENT/_2024/COC/dr.json", div_round_player, scoring_settings)
st.write("### Fantasyergebnisse")
st.dataframe(dr_df[[column for column in dr_df.columns if column != "Gruppe"]], hide_index=True)


# Conference Finals
st.write("## Conference Finals")
st.write("### Tippbild")
st.image("Pictures/2024/CoC/CC.jfif", width=500)
cf_df = ind_calculate_fantasy_points_and_sort("DATA_PERMANENT/_2024/COC/cf.json", conf_round_player, scoring_settings)
# QB einzeln
qb_df = cf_df[cf_df['Position'] == 'QB']

# RB und WR zusammenfassen nach Teams
rb_wr_df = cf_df[cf_df['Position'].isin(['RB', 'WR'])]
rb_wr_df = rb_wr_df.groupby(['Gruppe', 'Position'], observed=True).agg({'FFP': 'sum', 'Preis': 'first'}).reset_index()
rb_wr_df["Spieler"] = rb_wr_df['Gruppe'].astype(str) + " " + rb_wr_df['Position'].astype(str) + "s"

# TE einzeln
te_df = cf_df[cf_df['Position'] == 'TE']

# Alle Daten zusammenführen
final_df = pd.concat([qb_df[['Spieler', 'Position', 'Gruppe', 'FFP', 'Preis']], rb_wr_df[['Spieler', 'Gruppe', 'Position', 'FFP', 'Preis']], te_df[['Spieler', 'Position', 'Gruppe', 'FFP', 'Preis']]])
final_df = final_df.sort_values(by=['Position', 'Preis'], ascending=[True, False]).reset_index(drop=True)

st.write("### Fantasyergebnisse")
st.dataframe(final_df[[column for column in final_df.columns if column != "Gruppe"]], hide_index=True)

# Super Bowl
st.write("## Super Bowl LIX")
st.write("### Tippbild")
st.image("Pictures/2024/CoC/SB.jfif", width=500)
cont_sb = st.container()

with open("DATA_PERMANENT/_2024/COC/sb.json",encoding="utf-8") as f:
    sb_data = json.load(f)

# valid_player_ids = {str(data[2]): data[1] for data in super_bowl_player}
# data = []
# for player in sb_data:
#         if player["player_id"] in valid_player_ids:
#             player_name = player['player'].get("first_name", "") + " " + player['player'].get("last_name", "")
#             player_data = {
#                 "player_id": player["player_id"],
#                 "Spieler": player_name,  # Spielernamen hinzufügens
#                 "Position": player["player"]["position"],
#                 "Gruppe": player["team"],
#                 "FFP 1x": 0,
#                 "Multiplikator": valid_player_ids[player["player_id"]],
#                 "FFP SB-Game": 0,
#                 "last_name": player['player'].get("last_name", "")
#             }

#             fantasy_points = 0
#             for key, multiplier in scoring_settings.items():
#                 stat_value = player.get("stats", {}).get(key, 0)  # Falls Wert fehlt, setze 0
#                 player_data[key] = stat_value
#                 fantasy_points += stat_value * multiplier  # Punkte berechnen
#             # Finalen Punktestand speichern
#             player_data["FFP 1x"] = round(fantasy_points, 2)  # Runden für bessere Lesbarkeit
#             player_data["FFP SB-Game"] = player_data["FFP 1x"] * player_data["Multiplikator"]
#             data.append(player_data)
# data_df = pd.DataFrame(data)
# st.dataframe(data_df[["player_id", "Spieler", "Position", "FFP 1x", "Multiplikator", "FFP SB-Game"]].sort_values(by=["Multiplikator", "Position"], ascending=[True, True]).set_index("player_id"), hide_index=True)
# sb_df = calculate_fantasy_points("views/CoC/sb.json", super_bowl_challenge, scoring_settings)
# cont_sb.dataframe(sb_df.set_index("player_id"), hide_index=True)

st.write("### Tippabgaben")
with open("DATA_PERMANENT/_2024/COC/coc.csv", "r", ) as f:
    tips = pd.read_csv(f)
st.write("#### Wildcard Weekend")
st.dataframe(tips[["Name", "QB WC", "RB WC", "WR WC", "TE WC"]].set_index("Name"))

st.write("#### Divisional Round")
dr_df = tips[["Name", "QB DR", "RB DR", "WR DR", "TE DR"]].set_index("Name")
dr_df = dr_df.dropna(how="any")
st.dataframe(dr_df)

st.write("#### Conference Finals")
cf_df = tips[["Name", "QB CF", "RB CF", "WR CF", "TE CF"]].set_index("Name")
cf_df = cf_df.dropna(how="any")
st.dataframe(cf_df)

st.write("#### Super Bowl")
sb_df = tips[["Name", "Player 1", "Player 2", "Player 3"]].set_index("Name")
sb_df = sb_df.dropna(how="any")
st.dataframe(sb_df)




# import streamlit as st
# import pandas as pd
# from views.CoC.utils import load_json, process_players, calculate_fantasy_points
# from views.CoC.config import scoring_settings, wc_round_player, div_round_player, conf_round_player, super_bowl_challenge

# # Streamlit-Setup
# st.title("🏆 Champ of Champs 2024")
# st.write("""
# Das Champ of Champs-Spiel ist der Abschluss der StonedLack-Saison und kührt den Sieger aller Sieger.
# Zugelassen waren alle Champions der aktuellen Redraftligen (Saison 2024) und alle Dynasty-Champs.
# """)

# st.write("### 📊 Scoring")
# st.table(scoring_settings)

# # **WILDCARD ROUND**
# st.header("Wild Card Weekend")
# st.image("Pictures/WC.jfif", width=500)
# wc_df = process_players(load_json("views/CoC/wc.json"), wc_round_player, scoring_settings)
# st.dataframe(wc_df.drop(columns=["Gruppe"]), hide_index=True)

# # **DIVISIONAL ROUND**
# st.header("Divisional Round")
# st.image("Pictures/DR.png", width=500)
# dr_df = process_players(load_json("views/CoC/dr.json"), div_round_player, scoring_settings)
# st.dataframe(dr_df.drop(columns=["Gruppe"]), hide_index=True)

# # **CONFERENCE FINALS**
# st.header("Conference Finals")
# st.image("Pictures/CC.jfif", width=500)
# cf_df = process_players(load_json("views/CoC/cf.json"), conf_round_player, scoring_settings)

# # Spezialverarbeitung: QB normal, RB/WR gruppiert, TE normal
# qb_df = cf_df[cf_df['Position'] == 'QB']
# rb_wr_df = cf_df[cf_df['Position'].isin(['RB', 'WR'])].groupby(['Gruppe', 'Position'], observed=True).agg({'FFP': 'sum', 'Preis': 'first'}).reset_index()
# rb_wr_df["Spieler"] = rb_wr_df["Gruppe"] + " " + rb_wr_df["Position"] + "s"
# te_df = cf_df[cf_df['Position'] == 'TE']

# # Alles zusammenführen
# final_df = pd.concat([qb_df, rb_wr_df, te_df], ignore_index=True).sort_values(by=["Position", "Preis"])
# st.dataframe(final_df.drop(columns=["Gruppe"]), hide_index=True)

# # **SUPER BOWL**
# st.header("Super Bowl LIX")
# st.image("Pictures/SB.jfif", width=500)

# sb_data = load_json("views/CoC/sb.json")
# valid_player_ids = {str(data[2]): data[1] for data in super_bowl_challenge}

# data = [
#     {
#         "player_id": player["player_id"],
#         "Spieler": f"{player['player'].get('first_name', '')} {player['player'].get('last_name', '')}".strip(),
#         "Position": player["player"]["position"],
#         "Gruppe": player["team"],
#         "FFP 1x": round(calculate_fantasy_points(player, scoring_settings), 2),
#         "Multiplikator": valid_player_ids[player["player_id"]],
#         "FFP SB-Game": round(calculate_fantasy_points(player, scoring_settings) * valid_player_ids[player["player_id"]], 2),
#     }
#     for player in sb_data if player["player_id"] in valid_player_ids
# ]

# sb_df = pd.DataFrame(data).sort_values(by=["Multiplikator", "Position"], ascending=[True, True])
# st.dataframe(sb_df.drop(columns=["Gruppe"]), hide_index=True)

# # **Tippabgaben laden**
# st.header("📋 Tippabgaben")
# tips = pd.read_csv("views/CoC/coc.csv")

# for round_name, columns in [
#     ("Wildcard Weekend", ["Name", "QB WC", "RB WC", "WR WC", "TE WC"]),
#     ("Divisional Round", ["Name", "QB DR", "RB DR", "WR DR", "TE DR"]),
#     ("Conference Finals", ["Name", "QB CF", "RB CF", "WR CF", "TE CF"]),
#     ("Super Bowl", ["Name", "Player 1", "Player 2", "Player 3"])
# ]:
#     st.subheader(round_name)
#     df = tips[columns].dropna(how="any").set_index("Name")
#     st.dataframe(df)
