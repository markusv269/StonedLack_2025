import streamlit as st
# import pandas as pd
from supabase import create_client, Client
from methods import load_rosters, load_leagues_with_type, load_managers

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# Matchups laden
leagues_df = load_leagues_with_type("redraft")
rosters_df = load_rosters()
managers_df = load_managers()
rosters_df = rosters_df.merge(leagues_df, on="league_id", how="right")
rosters_df = rosters_df.merge(managers_df[["league_id", "roster_id", "display_name"]], on=["league_id", "roster_id"], how="left")
st.write("### Standings SLR 2025")
# st.dataframe(rosters_df)
select_week = st.selectbox("Woche wählen", options=sorted(rosters_df["week"].unique(), reverse=True))
if select_week is not None:
    rosters_df = rosters_df[rosters_df["week"] == select_week]
for league_id, group in rosters_df.groupby("league_id"):
    st.write(f"#### {group['league_name'].iloc[0]}")
    standings = group[["display_name", "wins", "losses", "ties", "fpts_for", "fpts_against", "ppts"]]
    standings = standings.sort_values(by=["wins", "fpts_for"], ascending=[False, False]).reset_index(drop=True)
    # standings.index += 1  # Start index at 1
    standings.insert(0, "#", standings.index + 1)
    standings.rename(columns={
        "#":"#",
        "display_name": "Manager",
        "wins": "W",
        "losses": "L",
        "ties": "T",
        "fpts_for": "FPTS for",
        "fpts_against": "FPTS against",
        "ppts": "max PF"
    }, inplace=True)
    # Funktion zum Einfärben
     # Funktion zum Einfärben von Zeilen
    def highlight_rows(row):
        if row.name in [0, 1]:  # Platz 1 & 2
            return ['background-color: rgba(255, 99, 71, 0.3)'] * len(row)  # weiches Tomatenrot
        elif row.name in [2, 3, 4, 5]:  # Platz 3 bis 6
            return ['background-color: rgba(70, 130, 180, 0.3)'] * len(row)  # sanftes Stahlblau
        else:
            return [''] * len(row)

    # Funktion zum Fett-Schreiben von Platzierung (Index) und Manager
    def bold_text(row):
        styles = [''] * len(row)
        if 'Manager' in row.index:
            manager_idx = row.index.get_loc("Manager")
            styles[manager_idx] = 'font-weight: bold'
        return styles

    # Anzeige mit Styling
    styled = standings.style \
        .apply(highlight_rows, axis=1) \
        .apply(bold_text, axis=1)

    # Index fett formatieren
    styled.set_table_styles([{
        'selector': 'th.row_heading',
        'props': [('font-weight', 'bold')]
    }])
    st.dataframe(styled, width="content", hide_index=True,
                 column_config={
                    "#": st.column_config.NumberColumn(
                        "#",
                        format="%d",
                        help="Platzierung",
                        width="small"
                    ),
                    "Manager": st.column_config.TextColumn(
                        "Manager",
                        help="Team Manager",
                        width="medium"
                    ),
                    "W": st.column_config.NumberColumn(
                        "W",
                        format="%d",
                        help="Wins",
                        width="small"
                    ),
                    "L": st.column_config.NumberColumn(
                        "L",
                        format="%d",
                        help="Losses",
                        width="small"
                    ),
                    "T": st.column_config.NumberColumn(
                        "T",
                        format="%d",
                        help="Ties",
                        width="small"
                    ),
                    "FPTS for": st.column_config.NumberColumn(
                        "FPTS for",
                        format="%.2f",
                        help="Fantasy Points For",
                        width="small"
                    ),
                    "FPTS against": st.column_config.NumberColumn(
                        "FPTS against",
                        format="%.2f",
                        help="Fantasy Points Against",
                        width="small"
                    ),
                    "max PF": st.column_config.NumberColumn(
                        "max PF",
                        format="%.2f",
                        help="Max Possible Points For",
                        width="small"
                    ),
                 }
    )
