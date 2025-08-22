from sb_fetch_adpboard import get_adpboard
import streamlit as st
import pandas as pd

draft_df = get_adpboard("redraft")

# Anzahl Teams
num_teams = 12
teams = [f"Team {i+1}" for i in range(num_teams)]

# --- Farben für Positionen ---
POSITION_COLORS = {
    "QB": "#FFD700",
    "RB": "#1E90FF",
    "WR": "#32CD32",
    "TE": "#FF69B4",
    "K": "#FFA500",
    "DL": "#8B0000",
    "LB": "#DC143C",
    "DB": "#FF4500",
    "IDP": "#FF6347",  # für Sammel-Def-Positionen
}

def position_color(pos):
    return POSITION_COLORS.get(pos, "#CCCCCC")
def player_box(name, team, pos):
    color = position_color(pos)
    return f"""
    <div style="
        background-color:{color};
        padding:6px;
        margin:2px;
        border-radius:6px;
        text-align:center;
        font-weight:bold;
        font-size:14px;
    ">
        {name} ({team})<br>{pos}
    </div>
    """
st.write("### Draftboard (Snake-Draft)")
# --- Max Picks pro Runde ---
num_teams = 12  # feste Anzahl Spalten

rounds = sorted(draft_df["adp_round"].unique())
for r in rounds:
    st.subheader(f"Runde {r}")
    round_picks = draft_df[draft_df["adp_round"] == r].sort_values("adp_pick")
    
    # Snake-Logik: gerade Runden umdrehen
    if r % 2 == 0:
        round_picks = round_picks.iloc[::-1]
    
    cols = st.columns(num_teams)  # immer 12 Spalten
    for idx, row in enumerate(round_picks.itertuples()):
        team_col = idx % num_teams  # Spalte innerhalb der Runde
        with cols[team_col]:
            html = player_box(row.name, row.team, row.position)
            st.markdown(html, unsafe_allow_html=True)