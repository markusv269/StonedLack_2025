import streamlit as st
import requests
import pandas as pd
from collections import defaultdict
from config import REDLEAGUES_2025
from assets.styles_def import position_color, player_box
from sb_fetch_adpboard import get_adpboard

all_picks = get_adpboard("redraft")
st.dataframe(all_picks)

# @st.cache_data(show_spinner="Lade Draft-Daten ...", ttl=3600)
# def fetch_all_drafts(league_ids):
#     all_picks = []
#     for league_id in league_ids:
#         try:
#             # Schritt 1: Alle Drafts der Liga abrufen
#             draft_resp = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/drafts").json()
#             if not draft_resp:
#                 continue

#             # # Schritt 2: Nur den Draft mit draft_type == 1 verwenden
#             # rookie_drafts = [d for d in draft_resp if d["settings"].get("player_type") == 1]
#             # if not rookie_drafts:
#             #     continue
#             draft_id = draft_resp[0]['draft_id']

#             # Schritt 3: Picks für diesen Draft abrufen
#             picks = requests.get(f"https://api.sleeper.app/v1/draft/{draft_id}/picks").json()

#             # Optional: scoring_type jedem Pick hinzufügen
#             # for pick in picks:
#             #     pick['scoring_type'] = draft_type

#             # Dann alle Picks sammeln
#             all_picks.extend(picks)
#         except Exception as e:
#             st.warning(f"Fehler bei League {league_id}: {e}")
#     return all_picks


# def build_draftboard(picks):
#     player_stats = defaultdict(lambda: {"total_pick": 0, "count_idp": 0, "count_ppr":0, "count_2qb":0, "count_total":0, "pick_idp":0, "pick_ppr":0, "pick_2qb":0, "metadata": {}})
    
#     for pick in picks:
#         if not pick.get("metadata"): continue
#         pid = pick["player_id"]
#         player_stats[pid]["total_pick"] += pick["pick_no"]
#         player_stats[pid]["count_total"] += 1
#         player_stats[pid]["metadata"] = pick["metadata"]
#         # if pick["scoring_type"] == "idp":
#         #     player_stats[pid]["count_idp"] += 1
#         #     player_stats[pid]["pick_idp"] += pick["pick_no"]
#         # elif pick["scoring_type"] == "dynasty_ppr":
#         #     player_stats[pid]["count_ppr"] += 1
#         #     player_stats[pid]["pick_ppr"] += pick["pick_no"]
#         # elif pick["scoring_type"] == "dynasty_2qb":
#         #     player_stats[pid]["count_2qb"] += 1
#         #     player_stats[pid]["pick_2qb"] += pick["pick_no"]
#     records = []
#     for pid, data in player_stats.items():
#         if data["count_idp"] > 0:
#             avg_pick_idp = data["pick_idp"] / data["count_idp"]
#         else:
#             avg_pick_idp = 999
#         if data["count_ppr"] > 0:
#             avg_pick_ppr = data["pick_ppr"] / data["count_ppr"]
#         else:
#             avg_pick_ppr = 999
#         if data["count_2qb"] > 0:
#             avg_pick_2qb = data["pick_2qb"] / data["count_2qb"]
#         else:
#             avg_pick_2qb = 999
#         avg_pick = data["total_pick"] / data["count_total"]
#         meta = data["metadata"]
#         records.append({
#             "player_id": pid,
#             "avg_pick": avg_pick,
#             "avg_pick_idp": avg_pick_idp,
#             "avg_pick_ppr": avg_pick_ppr,
#             "avg_pick_2qb": avg_pick_2qb,
#             "name": f"{meta.get('first_name', '')[:1]}. {meta.get('last_name', '')}",
#             "position": meta.get("position", ""),
#             "team": meta.get("team", ""),
#             "count_total": data["count_total"],
#             "count_idp": data["count_idp"],
#             "count_ppr": data["count_ppr"],
#             "count_2qb": data["count_2qb"],
#         })
    
#     df = pd.DataFrame(records)
#     return df

# # --- Streamlit App ---
# st.write("### SLR ADP Draftboard")
# with st.spinner("Lade alle Draftdaten..."):
#     all_picks = fetch_all_drafts(list(REDLEAGUES_2025.keys()))
# top36 = build_draftboard(all_picks)

col1, col3 = st.columns(2)
with col1:
    select_playerpicks = st.selectbox("Min. Anzahl Picks", list(range(1,49)), index=0)
# with col3:
#     select_scoring = st.selectbox("Liga", ["All", "1QB", "2QB", "IDP"], index=0)

if select_playerpicks:
    show = all_picks[all_picks["pick_count"] >= select_playerpicks]

# value = "avg_pick"
# count = "count_total"
# # elif select_scoring == "IDP":
# #     value = "avg_pick_idp"
# #     count = "count_idp"
# # elif select_scoring == "1QB":   
# #     value = "avg_pick_ppr"
# #     count = "count_ppr"
# # elif select_scoring == "2QB":
# #     value = "avg_pick_2qb"
# #     count = "count_2qb"

# if select_playerpicks:
#     top36 = top36[top36[count] >= select_playerpicks]

# top36 = top36.sort_values(value).reset_index(drop=True)

# top36["round"] = top36.index // 12 + 1
# top36["pick_in_round"] = top36.index % 12 + 1

# show = top36#[top36["round"] <= 3]
# Darstellung als Board mit farbigen Kästchen
for r in range(1, 16):
    # st.subheader(f"🏈 Runde {r}")
    round_picks = show[show["adp_round"] == r]

    cols = st.columns(12)
    for _, row in round_picks.iterrows():
    # Prüfen, ob die Runde gerade ist
        if row["adp_round"] % 2 == 0:
            # Spalten umdrehen: "pick_in_round" wird umgekehrt
            col_index = len(cols) - row["adp_pick"]
        else:
            col_index = row["adp_pick"] - 1

        with cols[col_index]:
            color = position_color(row["player_position"])
            html = player_box(
                row["name"], 
                row["team"], 
                row["player_position"], 
                color, 
                row["adp_round"], 
                row["adp_pick"], 
                row["pick_count"]
            )
            st.markdown(html, unsafe_allow_html=True)

# scoring_types = []

# # for pick in all_picks:
# #     scoring_type = pick.get("scoring_type")  # Sicherer Zugriff
# #     if scoring_type and scoring_type not in scoring_types:
# #         scoring_types.append(scoring_type)

# # st.write(scoring_types)

# st.write("### Vertical Draftboard")

# top36 = top36[top36[value] <= 900]

# col1, col2, col3 = st.columns(3)
# col4, col5, col6 = st.columns(3)

# with col2:
#     st.write("**RB**")
#     rb = top36[top36["position"] == "RB"]
#     st.dataframe(rb[["name", "team", "position", value]].sort_values(value), use_container_width=True, hide_index=True)
# with col3:
#     st.write("**WR**")
#     wr = top36[top36["position"] == "WR"]
#     st.dataframe(wr[["name", "team", "position", value]].sort_values(value), use_container_width=True, hide_index=True)
# with col4:
#     st.write("**TE**")
#     te = top36[top36["position"] == "TE"]
#     st.dataframe(te[["name", "team", "position", value]].sort_values(value), use_container_width=True, hide_index=True)
# with col1:
#     st.write("**QB**")
#     qb = top36[top36["position"] == "QB"]
#     st.dataframe(qb[["name", "team", "position", value]].sort_values(value), use_container_width=True, hide_index=True)
# with col6:
#     st.write("**K**")
#     k = top36[top36["position"] == "K"]
#     st.dataframe(k[["name", "team", "position", value]].sort_values(value), use_container_width=True, hide_index=True)
# with col5:
#     st.write("**DST**")
#     def_ = top36[top36["position"].isin(["DEF", "DST"])]
#     st.dataframe(def_[["name", "team", "position", value]].sort_values(value), use_container_width=True, hide_index=True)

# # player_pos = []
# # for pick in all_picks:
# #     if pick.get("metadata", {}).get("position") not in player_pos:
# #         player_pos.append(pick["metadata"]["position"])
# # st.write(player_pos)