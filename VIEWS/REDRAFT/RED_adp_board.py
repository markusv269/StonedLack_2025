import streamlit as st
from assets.styles_def import position_color, player_box
from sb_fetch_adpboard import get_adpboard

all_picks = get_adpboard("redraft")

col1, col3 = st.columns(2)
with col1:
    select_playerpicks = st.selectbox("Min. Anzahl Picks", list(range(1,49)), index=0)
# with col3:
#     select_scoring = st.selectbox("Liga", ["All", "1QB", "2QB", "IDP"], index=0)

if select_playerpicks:
    show = all_picks[all_picks["pick_count"] >= select_playerpicks]

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
                row["avg_pick"]
            )
            st.markdown(html, unsafe_allow_html=True)

select_positions = st.multiselect("Positionen filtern", ["QB", "RB", "WR", "TE", "K", "DEF"], default=["QB", "RB", "WR", "TE", "K", "DEF"])
if select_positions:
    show = show[show["player_position"].isin(select_positions)]

st.dataframe(show[['name', 'team', 'player_position', "avg_pick", "min_pick", "max_pick"]], hide_index=True, use_container_width=True)