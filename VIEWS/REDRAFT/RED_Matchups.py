import streamlit as st
import pandas as pd
from supabase import create_client, Client
from methods import load_managers, load_leagues_with_type, load_matchups

# ░░░ SUPABASE CREDENTIALS ░░░
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)


# ░░░ JSON-KONSTRUKT ░░░
def build_weekly_json(matchups_df: pd.DataFrame, week: int, league_id: str):
    df = matchups_df[(matchups_df["week"] == week) & (matchups_df["league_id"] == league_id)]

    result = {"week": week, "league_id": league_id, "matchups": {}}

    for _, row in df.iterrows():
        matchup_id = str(row["matchup_id"])
        roster_id = str(row["roster_id"])
        starters = row.get("json_data", {}).get("starters", []) or []
        players_points = row.get("json_data", {}).get("players_points", {}) or {}

        starter_dict = {pid: players_points.get(pid, 0) for pid in starters}
        all_players = list(players_points.keys())
        bench_players = [p for p in all_players if p not in starters]
        bench_dict = {pid: players_points.get(pid, 0) for pid in bench_players}

        if matchup_id not in result["matchups"]:
            result["matchups"][matchup_id] = {}

        result["matchups"][matchup_id][roster_id] = {"starter": starter_dict, "bench": bench_dict}

    return result

def collect_player_ids(weekly_json: dict) -> set:
    player_ids = set()
    for matchup in weekly_json.get("matchups", {}).values():
        for roster in matchup.values():
            for section in ["starter", "bench"]:
                player_ids.update(roster[section].keys())
    return player_ids

# ░░░ HELFER ░░░
def roster_name(league_id, roster_id, managers_df):
    m = managers_df[(managers_df["league_id"] == league_id) & (managers_df["roster_id"] == int(roster_id))]
    if m.empty:
        return f"Roster {roster_id}"
    display = m.iloc[0]["display_name"]
    team = m.iloc[0]["team_name"]
    if team:
        return f"{display} ({team})"
    else:
        return f"{display}"

def player_box(player_id: str, points: float, starter=True, players_dict=None):
    if players_dict and player_id in players_dict:
        info = players_dict[player_id]
        label = info['name']
        team = info['team']
        position = info['position']
        if position == "DEF":
            headshot_url = f"https://a.espncdn.com/i/teamlogos/nfl/500/{team}.png"
        else:
            headshot_url = f"https://sleepercdn.com/content/nfl/players/thumb/{player_id}.jpg"
    else:
        label = player_id
        team = ""
        position = "BENCH"
        headshot_url = "https://via.placeholder.com/70"

    card_class = f"{position} {'starter' if starter else 'bench'}"

    st.markdown(
        f"""
        <div class="playercard {card_class}">
            <img src="{headshot_url}" class="playerimg">
            <div class="playername">{label}</div>
            <div class="playerteam">{team} - {position}</div>
            <div class="playerpoints">{points:.2f} pts</div>
        </div>
        """,
        unsafe_allow_html=True
    )




# ░░░ MATCHUP DARSTELLUNG ░░░
def show_matchups(weekly_json: dict, league_id: str, managers_df: pd.DataFrame, players_dict: dict, roster_positions: list):
    for matchup_id, matchup_data in weekly_json.get("matchups", {}).items():
        # st.subheader(f"Matchup {matchup_id}")

        roster_ids = list(matchup_data.keys())
        if len(roster_ids) != 2:
            st.warning("⚠️ Matchup hat nicht genau 2 Roster")
            continue

        r1, r2 = roster_ids
        name1 = roster_name(league_id, r1, managers_df)
        name2 = roster_name(league_id, r2, managers_df)

        # Gesamtpunkte
        def total(roster):
            d = matchup_data[roster]
            return sum(d["starter"].values())

        total1, total2 = total(r1), total(r2)

        col1, col_mid, col2 = st.columns([5,1,5])
        with col1:
            st.markdown(f"#### {name1}")
            if total1 > total2:
                st.success(f"Gesamtpunkte: {round(total1, 2)}")
            elif total1 < total2:
                st.error(f"Gesamtpunkte: {round(total1, 2)}")
            else:
                st.info(f"Gesamtpunkte: {round(total1, 2)}")
        with col2:
            st.markdown(f"#### {name2}")
            if total1 < total2:
                st.success(f"Gesamtpunkte: {round(total2, 2)}")
            elif total1 > total2:
                st.error(f"Gesamtpunkte: {round(total2, 2)}")
            else:
                st.info(f"Gesamtpunkte: {round(total2, 2)}")

        # Starter nebeneinander mit mittiger Spalte
        st.write("**Starter**")
        starters1 = list(matchup_data[r1]["starter"].items())
        starters2 = list(matchup_data[r2]["starter"].items())
        max_len = max(len(starters1), len(starters2), len(roster_positions))
        ext = [".jpg", ".png"]
        for i in range(max_len):
            col1, col_mid, col2 = st.columns([5,1,5])
            with col1:
                if i < len(starters1):
                    pid, pts = starters1[i]
                    player_box(pid, pts, starter=True, players_dict=players_dict)
            with col_mid:
                if i < len(starters1):
                    st.markdown(
                        f"<div style='text-align:center; margin-top:25%; font-weight:bold;'>{roster_positions[i]}</div>",
                        unsafe_allow_html=True
                    )
            # with col1a:
            #     if i < len(starters1):
            #         pid, pts = starters1[i]
            #         try: 
            #             url = supabase.storage.from_("images").create_signed_url(f"{pid}.jpg", expires_in=3600)
            #             st.image(url)
            #         except:
            #             try:
            #                 url = supabase.storage.from_("images").create_signed_url(f"{pid}.png", expires_in=3600)
            #                 st.image(url)
            #             except:
            #                 st.write(pid)                    

            # # with col2a:
            # #     if i < len(starters2):
            # #         pid, pts = starters2[i]
            # #         try: 
            # #             st.image(supabase.storage.from_('images').download(f'{pid}.jpg'))
            # #         except:
            # #             try:
            # #                 st.image(supabase.storage.from_('images').download(f'{pid}.png'))
            # #             except:
            # #                 st.write(pid)
            with col2:
                if i < len(starters2):
                    pid, pts = starters2[i]
                    player_box(pid, pts, starter=True, players_dict=players_dict)

        # Bench nebeneinander (ohne Positionsspalte)
        st.write("**Bench**")
        bench1 = list(matchup_data[r1]["bench"].items())
        bench2 = list(matchup_data[r2]["bench"].items())
        max_len = max(len(bench1), len(bench2))
        for i in range(max_len):
            col1, col_mid, col2 = st.columns([5,1,5])
            with col1:
                if i < len(bench1):
                    pid, pts = bench1[i]
                    player_box(pid, pts, starter=False, players_dict=players_dict)
            with col2:
                if i < len(bench2):
                    pid, pts = bench2[i]
                    player_box(pid, pts, starter=False, players_dict=players_dict)

        st.divider()

# ░░░ STREAMLIT ░░░
st.title("Matchup Viewer")

matchups_df = load_matchups()
leagues_df = load_leagues_with_type("redraft")
managers_df = load_managers()

week_select = st.number_input("Woche wählen", min_value=int(matchups_df["week"].min()), max_value=int(matchups_df["week"].max()), step=1)
league_name = st.selectbox("League wählen", leagues_df["league_name"].unique())

if st.button("Zeige Matchups"):
    league_id = leagues_df.loc[leagues_df["league_name"] == league_name, "league_id"].iloc[0]
    roster_positions = leagues_df.loc[leagues_df["league_name"] == league_name, "roster_positions"].iloc[0]

    weekly_json = build_weekly_json(matchups_df, week=week_select, league_id=league_id)
    player_ids = collect_player_ids(weekly_json)

    players = (
        supabase.table("nfl_players")
        .select("player_id, name, position, team")
        .in_("player_id", list(player_ids))
        .execute()
    )
    players_df = pd.DataFrame(players.data)
    players_dict = {str(row["player_id"]): row for _, row in players_df.iterrows()}

    show_matchups(weekly_json, league_id, managers_df, players_dict, roster_positions)

st.markdown("""
<style>
.playercard {
    border-radius: 16px;
    padding: 12px;
    margin: 6px;
    text-align: center;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: #111;
    position: relative;
}
.playercard:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0px 8px 20px rgba(0,0,0,0.25);
}

/* Positionen */
.playercard.QB { background: #f9a3a4; }
.playercard.RB { background: #7bd4a2; }
.playercard.WR { background: #72c5f4; color: #fff; }
.playercard.TE { background: #e6b07c; color: #fff; }
.playercard.K { background: #d7e878; }
.playercard.DEF { background: #b085f7; color: #fff; }
.playercard.FLEX { background: #70d2d8; color: #fff; }
.playercard.BENCH { background: #e0e0e0; }

/* Player Image */
.playercard .playerimg {
    border-radius: 50%;
    width: 70px;
    height: 70px;
    object-fit: cover;
    margin-bottom: 10px;
    border: 0px solid rgba(0,0,0,0.1);
}

/* Team Logo Overlay oben rechts */
.playercard .teamlogo {
    width: 30px;
    height: 30px;
    position: absolute;
    top: 8px;
    right: 8px;
    border-radius: 50%;
    border: 0px solid rgba(0,0,0,0.2);
    background: #fff;
}

/* Text */
.playercard .playername { font-size: 20px; font-weight: 700; margin-bottom: 4px; }
.playercard .playerteam { font-size: 14px; font-weight: 500; color: #4a4a4a; margin-bottom: 6px; }
.playercard .playerpoints { font-size: 18px; font-weight: 800; color: #222; }
</style>
""", unsafe_allow_html=True)
