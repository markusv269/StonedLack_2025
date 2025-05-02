import streamlit as st
from sleeper_wrapper import League, Drafts
import pandas as pd
from collections import Counter

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
        },
        "Return Yards": {
            "kr_yd": "Kick Return Yards",
            "pr_yd": "Punt Return Yards"
        },
        "Individual Defensive Player (IDP)": {
            "idp_blk_kick": "IDP Blocked Kick",
            "idp_def_td": "IDP Defensive Touchdown",
            "idp_ff": "IDP Forced Fumble",
            "idp_fum_rec": "IDP Fumble Recovery",
            "idp_fum_ret_yd": "IDP Fumble Return Yards",
            "idp_int": "IDP Interception",
            "idp_int_ret_yd": "IDP Interception Return Yards",
            "idp_pass_def": "IDP Pass Defended",
            "idp_qb_hit": "IDP QB Hit",
            "idp_safe": "IDP Safety",
            "idp_sack": "IDP Sack",
            "idp_sack_yd": "IDP Sack Yards",
            "idp_tkl_ast": "IDP Assisted Tackle",
            "idp_tkl_loss": "IDP Tackle for Loss",
            "idp_tkl_solo": "IDP Solo Tackle"
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


def get_picks(league_id):
    # Initialize league and draft info
    league = League(league_id)
    league_data = league.get_league()
    season0 = int(league_data['season'])
    draft_id = league_data['draft_id']
    draft = Drafts(draft_id)
    draft_settings = draft.get_specific_draft()['settings']

    # Build seasons and rounds
    seasons = list(range(season0, season0 + 3))
    rounds = list(range(1, draft_settings['rounds'] + 1))

    # Map rosters to owners
    # users = {u['user_id']: u for u in league.get_users()}
    roster_map = league.map_rosterid_to_ownerid(league.get_rosters())
    owners = list(roster_map.keys())

    # Create full grid of picks via Cartesian product
    idx = pd.MultiIndex.from_product([seasons, rounds, owners], names=['season', 'round', 'roster_id'])
    df_all = pd.DataFrame(index=idx).reset_index()
    # Default owner_id is the roster_id
    df_all['owner_id'] = df_all['roster_id']

    # Fetch and apply traded picks
    traded = pd.DataFrame(league.get_traded_picks(), dtype=int)
    # Merge on season, round, roster_id
    df_all = df_all.merge(
        traded[['season', 'round', 'roster_id', 'owner_id']], 
        on=['season', 'round', 'roster_id'], 
        how='left', 
        suffixes=('', '_new')
    )
    # Update owner_id where a trade exists
    df_all['owner_id'] = df_all['owner_id_new'].fillna(df_all['owner_id'])
    # Cleanup
    df_all = df_all.drop(columns=['owner_id_new'])

    return df_all
