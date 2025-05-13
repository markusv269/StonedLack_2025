import streamlit as st
from config import DYNLEAGUES
from utils import display_draft
import requests
import pandas as pd
from collections import defaultdict

st.write("### Draftübersicht")
st.write('''Die Draftübersicht wurde auf die neue Saison 2025 umgestellt. 
Nur Ligen, die zur neuen Saison einen Draft eingestellt haben, werden nun angezeigt. 
Alle Ligen können den Ligenübersichten entnommen werden. 
''')
for league_id in DYNLEAGUES:
    display_draft(league_id)


def position_color(pos):
    return {
        "QB": "#b26186",
        "RB": "#87c2a5",
        "WR": "#669dcb",
        "TE": "#c0914a",
        "K":  "#fbbc05",
        "DEF": "#ea4335",
        "DL": "#999999",
        "LB": "#999999",
        "DB": "#999999"
    }.get(pos.upper(), "#dddddd")

def player_box(name, team, position, color, round, pick_in_round):
    return f"""
    <div style="
        font-size: 1.3em;
        background-color: {color};
        padding: 2px;
        border-radius: 5px;
        margin: 2px;
        color: white;
        font-weight: bold;
        text-align: left;
        min-height: 90px;
    ">
        <div>{name}</div>
        <div style="font-size: 1em;">{round}.{pick_in_round}</div>
        <div style="font-size: 0.8em;">{team} • {position}</div>
    </div>
    """


@st.cache_data(show_spinner="Lade Draft-Daten ...", ttl=3600)
def fetch_all_drafts(league_ids):
    all_picks = []
    for league_id in league_ids:
        try:
            # Schritt 1: Alle Drafts der Liga abrufen
            draft_resp = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/drafts").json()
            if not draft_resp:
                continue

            # Schritt 2: Nur den Draft mit draft_type == 1 verwenden
            rookie_drafts = [d for d in draft_resp if d["settings"].get("player_type") == 1]
            if not rookie_drafts:
                continue
            draft_id = rookie_drafts[0]['draft_id']

            # Schritt 3: Picks für diesen Draft abrufen
            picks = requests.get(f"https://api.sleeper.app/v1/draft/{draft_id}/picks").json()
            all_picks.extend(picks)
        except Exception as e:
            st.warning(f"Fehler bei League {league_id}: {e}")
    return all_picks


def build_draftboard(picks):
    player_stats = defaultdict(lambda: {"total_pick": 0, "count": 0, "metadata": {}})
    
    for pick in picks:
        if not pick.get("metadata"): continue
        pid = pick["player_id"]
        player_stats[pid]["total_pick"] += pick["pick_no"]
        player_stats[pid]["count"] += 1
        player_stats[pid]["metadata"] = pick["metadata"]
    
    records = []
    for pid, data in player_stats.items():
        avg_pick = data["total_pick"] / data["count"]
        meta = data["metadata"]
        records.append({
            "player_id": pid,
            "avg_pick": avg_pick,
            "name": f"{meta.get('first_name', '')[:1]}. {meta.get('last_name', '')}",
            "position": meta.get("position", ""),
            "team": meta.get("team", ""),
            "count": data["count"]
        })
    
    df = pd.DataFrame(records)
    df = df.sort_values("avg_pick").reset_index(drop=True)
    return df

# --- Streamlit App ---
st.title("📊 Konsolidiertes Dynasty Draftboard (Top 3 Runden)")
with st.spinner("Lade alle Draftdaten..."):
    all_picks = fetch_all_drafts(DYNLEAGUES)
top36 = build_draftboard(all_picks)

col1, col2 = st.columns(2)
with col1:
    select_playerpicks = st.selectbox("Min. Anzahl Picks", list(range(1,16)), index=0)
with col2: 
    select_playerpool = st.selectbox("Spielerpool", ["All", "Ohne IDP", "Nur IDP"], index=0)

if select_playerpicks:
    top36 = top36[top36["count"] >= select_playerpicks]

if select_playerpool == "All":
    top36 = top36
elif select_playerpool == "Ohne IDP":
    top36 = top36[~top36["position"].isin(["DL", "LB", "DB"])]
elif select_playerpool == "Nur IDP":
    top36 = top36[top36["position"].isin(["DL", "LB", "DB"])]
top36 = top36.sort_values("avg_pick").reset_index(drop=True)

top36["round"] = top36.index // 12 + 1
top36["pick_in_round"] = top36.index % 12 + 1

show = top36[top36["round"] <= 3]
# Darstellung als Board mit farbigen Kästchen
for r in range(1, 4):
    # st.subheader(f"🏈 Runde {r}")
    round_picks = show[show["round"] == r]

    cols = st.columns(12)
    for _, row in round_picks.iterrows():
        with cols[row["pick_in_round"] - 1]:
            color = position_color(row["position"])
            html = player_box(row["name"], row["team"], row["position"], color, row["round"], row["pick_in_round"])
            st.markdown(html, unsafe_allow_html=True)