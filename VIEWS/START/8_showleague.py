import streamlit as st
from sleeper_wrapper import League, User, Drafts
import urllib.parse
from collections import Counter

league_info = {}

def scoring_settings(scoring):
    # Mapping von Scoring-Keys zu Kategorien und verständlichen Namen
    scoring_map = {
        "Passing": {
            "pass_yd": "Passing Yards (pro Yard)",
            "pass_td": "Passing Touchdown",
            "pass_2pt": "2pt Conversion (Pass)",
            "pass_int": "Interception (Pass)"
        },
        "Rushing": {
            "rush_yd": "Rushing Yards (pro Yard)",
            "rush_td": "Rushing Touchdown",
            "rush_2pt": "2pt Conversion (Rush)"
        },
        "Receiving": {
            "rec": "Receptions (PPR)",
            "rec_yd": "Receiving Yards (pro Yard)",
            "rec_td": "Receiving Touchdown",
            "rec_2pt": "2pt Conversion (Receiving)"
        },
        "Kicking": {
            "fgm_0_19": "Field Goal Made 0–19 Yards",
            "fgm_20_29": "Field Goal Made 20–29 Yards",
            "fgm_30_39": "Field Goal Made 30–39 Yards",
            "fgm_40_49": "Field Goal Made 40–49 Yards",
            "fgm_50p": "Field Goal Made 50+ Yards",
            "fgmiss": "Field Goal Missed",
            "xpm": "Extra Point Made",
            "xpmiss": "Extra Point Missed"
        },
        "Defense / Special Teams": {
            "sack": "Sack",
            "int": "Interception (Defense)",
            "fum_rec": "Fumble Recovery",
            "def_st_fum_rec": "DEF/ST Fumble Recovery",
            "ff": "Forced Fumble",
            "def_st_ff": "DEF/ST Forced Fumble",
            "safe": "Safety",
            "blk_kick": "Blocked Kick",
            "def_td": "Defensive Touchdown",
            "def_st_td": "DEF/ST Touchdown",
            "st_td": "Special Teams Touchdown",
            "fum_rec_td": "Fumble Return Touchdown",
            "st_fum_rec": "Special Teams Fumble Recovery",
            "st_ff": "Special Teams Forced Fumble"
        },
        "Points Allowed (Defense)": {
            "pts_allow_0": "0 Points Allowed",
            "pts_allow_1_6": "1–6 Points Allowed",
            "pts_allow_7_13": "7–13 Points Allowed",
            "pts_allow_14_20": "14–20 Points Allowed",
            "pts_allow_21_27": "21–27 Points Allowed",
            "pts_allow_28_34": "28–34 Points Allowed",
            "pts_allow_35p": "35+ Points Allowed"
        },
        "Turnovers": {
            "fum": "Fumble",
            "fum_lost": "Fumble Lost"
        }
    }

    # Ausgabe dynamisch generieren
    for category, keys in scoring_map.items():
        entries = []
        for key, label in keys.items():
            value = scoring.get(key, 0)
            if value != 0:
                entries.append(f"- **{label}:** {round(value,2)} Punkt{'e' if abs(value) != 1 else ''}")

        if entries:
            st.markdown(f"#### {category}")
            st.markdown("\n".join(entries))

def showleague_info(league_id, roster_id):
    try:
        league = League(league_id)
        league_data = league.get_league()
        st.write(f"## Liga: {league_data.get('name')} ({league_data.get('season')})")
        st.write("### Einstellungen:")
        # st.json(league_data)
        st.write(f"Waiver Budget: {league_data['settings'].get('waiver_budget')} FAAB$")
        st.write("### Roster Positionen:")
        roster_positions = league_data.get('roster_positions', [])
        position_counts = Counter(roster_positions)
        # Format: "1 QB", "2 RB", ...
        formatted_positions = [f"{count} {pos}" for pos, count in position_counts.items()]
        st.write("Roster Positionen: " + ", ".join(formatted_positions))
        st.write("### Scoring Settings:")
        scoring_settings(league_data.get("scoring_settings"))
    except Exception as e:
        st.error(f"Fehler beim Laden der Liga: {e}")
        return

    try:
        rosters = league.get_rosters()
        roster_info = next((r for r in rosters if str(r['roster_id']) == str(roster_id)), None)
    except Exception as e:
        st.error(f"Fehler beim Laden der Roster: {e}")
        return

    if roster_info:
        st.write(f"**Roster ID {roster_id} Details:**")
        st.json(roster_info)
    else:
        st.warning("Roster nicht gefunden.")

# Neue API verwenden
params = st.query_params
league_id = params.get("league_id")
roster_id = params.get("roster_id")

# Titel
# st.title("Sleeper League Roster Viewer")

# Anzeige oder Eingabe
if league_id and roster_id:
    # st.success(f"Liga: {league_id}, Roster: {roster_id}")
    showleague_info(league_id, roster_id)
else:
    league_id_input = st.text_input("League ID")
    roster_id_input = st.text_input("Roster ID")
    if st.button("Lade Roster"):
        if league_id_input and roster_id_input:
            # Query-Parameter setzen (Seite wird neu geladen)
            st.query_params.league_id = league_id_input
            st.query_params.roster_id = roster_id_input
            showleague_info(league_id_input, roster_id_input)
        else:
            st.error("Bitte beide Felder ausfüllen.")

        query_string = urllib.parse.urlencode({
            "league_id": league_id_input,
            "roster_id": roster_id_input
        })
        share_url = f"https://stonedlack-2025.streamlit.app/showleague?{query_string}"
        st.success(f"Teile diese Seite: {share_url}")