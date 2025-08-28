import pandas as pd
from supabase import create_client, Client
import streamlit as st

# ░░░ SUPABASE CREDENTIALS ░░░
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# ░░░ REDRAFT-LIGEN UND DRAFTS LADEN ░░░
leagues = supabase.table("leagues").select("league_id").eq("league_type", "redraft").execute().data
league_ids = [l["league_id"] for l in leagues]

drafts = supabase.table("drafts").select("draft_id").in_("league_id", league_ids).execute().data
draft_ids = [d["draft_id"] for d in drafts]

# ░░░ ALLE PICKS LADEN (Pagination) ░░░
all_picks = []
page = 0
page_size = 1000
while True:
    picks_page = supabase.table("draft_picks") \
        .select("player_id, json_data") \
        .in_("draft_id", draft_ids) \
        .range(page*page_size, (page+1)*page_size - 1) \
        .execute().data
    if not picks_page:
        break
    all_picks.extend(picks_page)
    page += 1

picks_df = pd.DataFrame(all_picks)

# pick_no aus json_data extrahieren
picks_df["pick_no"] = picks_df["json_data"].apply(lambda x: x["pick_no"] if isinstance(x, dict) else x.get("pick_no"))

# Min / Max / Count / ADP berechnen
agg = picks_df.groupby("player_id")["pick_no"].agg(
    min_pick="min",
    max_pick="max",
    count="count",
    avg_pick="mean"
).reset_index()

# Nur Spieler, die mindestens 25-mal gepickt wurden
agg = agg[agg["count"] >= 14]

# Spielerinfos laden
player_ids = agg["player_id"].tolist()
players = supabase.table("nfl_players") \
    .select("player_id, name, position, team") \
    .in_("player_id", player_ids).execute().data
players_df = pd.DataFrame(players)

# Merge Picks mit Spielerinfos
draftboard_df = agg.merge(players_df, on="player_id", how="left")

# Short Name erstellen
draftboard_df["name_short"] = draftboard_df["name"].str.split().str[-1]
draftboard_df["name_short"] = draftboard_df["name_short"].apply(
    lambda x: x[:6] + "..." if len(x) > 9 else x
)

# Bye Weeks zuordnen
bye_weeks = {
    5: ["ATL", "CHI", "GB", "PIT"],
    6: ["HOU", "MIN"],
    7: ["BAL", "BUF"],
    8: ["ARI", "DET", "JAX", "LV", "LAR", "SEA"],
    9: ["CLE", "NYJ", "PHI", "TB"],
    10: ["CIN", "DAL", "KC", "TEN"],
    11: ["IND", "NO"],
    12: ["DEN", "LAC", "MIA", "WAS"],
    14: ["CAR", "NE", "NYG", "SF"]
}
team_to_bye = {team: week for week, teams in bye_weeks.items() for team in teams}
draftboard_df["bye_week"] = draftboard_df["team"].map(team_to_bye)

# Nach ADP sortieren und Index neu setzen
draftboard_df = draftboard_df.sort_values(by="avg_pick", ascending=True).reset_index(drop=True)

draftboard_df["pos_ranking"] = (
    draftboard_df.groupby("position")["avg_pick"]
    .rank(method="first")  # "first" = Reihenfolge wie sie auftreten
    .astype(int)
)

# Anzahl Spieler pro Runde (12er-Liga)
players_per_round = 12

# Runde / Pick innerhalb der Runde anhand sortiertem Index
draftboard_df["round_num"] = (draftboard_df.index // players_per_round + 1).astype(int)
draftboard_df["pick_within_round"] = (draftboard_df.index % players_per_round + 1).astype(int)
draftboard_df["pos_in_draftboard"] = draftboard_df["pick_within_round"]
draftboard_df["first_pos"] = draftboard_df["position"]

# Snake-Logik für Position im Draftboard
draftboard_df["pos_in_draftboard"] = draftboard_df.apply(
    lambda row: players_per_round - row["pick_within_round"] + 1
    if row["round_num"] % 2 == 0  # gerade Runde -> von hinten nach vorn
    else row["pick_within_round"],  # ungerade Runde -> normal
    axis=1
)

# TikZ Format-Funktion
def format_row(row):
    return f'\\node[rectangle, fill={row["first_pos"]}, inner sep=2pt, rounded corners=.1cm] ({row["player_id"]}) at ({row["pos_in_draftboard"]},{row["round_num"]}) {{\n' \
           f'\t\\begin{{tabular}}{{@{{}}l@{{}}l@{{}}r@{{}}}}\n' \
           f'\t\t\\multicolumn{{2}}{{p{{2cm}}}}{{\\normalfont\\bfseries\\raggedright {row["name_short"]}}}& \\tiny \\textcolor{{gray!40!black}}{{ {{{row["round_num"]}}}.{{{row["pick_within_round"]}}} }}\\\\[-1ex]\n' \
           f'\t\t\\multicolumn{{3}}{{p{{3cm}}}}{{\\tiny \\textcolor{{gray!40!black}}{{ {row["first_pos"]} -- {row["team"]} ({row["bye_week"]}) }} }} \\\\[-1.25ex]\n' \
           f'\t\t\\multicolumn{{3}}{{p{{3cm}}}}{{\\tiny \\textcolor{{gray!40!black}}{{ {row["first_pos"]}\#{row["pos_ranking"]} Range: {row["min_pick"]} -- {row["max_pick"]} ($\diameter${round(row["avg_pick"],2)})}} }} \\\\[-2.5ex]\n' \
           f'&& \\includegraphics[width=1cm, height=.6cm, keepaspectratio]{{images/{row["player_id"]}}}\\\\[-1ex]\n' \
           f'\t\\end{{tabular}}\n' \
           f'}};\n'

# TikZ Knoten erzeugen und in Datei schreiben
formatted_rows = draftboard_df.sort_values(by="avg_pick", ascending=True).head(180).apply(format_row, axis=1)

with open("draftboard_player_list.py", "w") as f:
    f.write(str(draftboard_df['player_id'].to_list()))

with open("output.txt", "w") as f:
    f.writelines(formatted_rows)

print(f"Fertig! {len(formatted_rows)} Spieler in output.txt exportiert.")
print(len(formatted_rows))  # sollte 170 sein
print(formatted_rows.head())
