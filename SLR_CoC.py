import streamlit as st
from sleeper_wrapper import User
from datetime import datetime
from supabase import create_client, Client
import pandas as pd
import uuid
import requests

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

DIV_ROUND_WEEK = 18
ROUND_NAME = "Divisional"
BUDGET_LIMIT = 9

DIV_ROUND_PRICES = {
    "4881": 5, "4866": 5, "6794": 5, "5012": 5,
    "11566": 3, "8150": 3, "9493": 3, "7600": 3,
    "11563": 1, "11584": 1, "5045": 1, "9484": 1,
    "6797": 0, "4018": 0, "11618": 0, "10236": 0
}

# --------------------------------------------------
# DATA LOADERS
# --------------------------------------------------
@st.cache_data(ttl=600)
def load_leagues():
    df = pd.DataFrame(
        supabase.table("leagues")
        .select("*")
        .execute()
        .data
    )
    return df[df["league_type"] != "empty"] \
        .sort_values(by=["league_type", "league_sort"]) \
        .reset_index(drop=True)


@st.cache_data(ttl=600)
def load_managers(batch_size=1000):
    all_rows = []
    start = 0

    while True:
        res = (
            supabase.table("managers")
            .select("league_id, roster_id, display_name")
            .range(start, start + batch_size - 1)
            .execute()
        )

        data = res.data
        if not data:
            break

        all_rows.extend(data)
        start += batch_size

    return pd.DataFrame(all_rows)



@st.cache_data(ttl=600)
def load_players(player_ids):
    df = pd.DataFrame(
        supabase.table("nfl_players")
        .select("*")
        .in_("player_id", player_ids)
        .execute()
        .data
    )
    df["price"] = df["player_id"].map(DIV_ROUND_PRICES)
    return df


# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def validate_sleeper_user(username: str) -> str | None:
    try:
        return User(username).get_user_id()
    except Exception:
        return None


def existing_submission(username: str) -> bool:
    res = (
        supabase.table("lineups")
        .select("lineup_id")
        .eq("sleeper_username", username.lower())
        .eq("round", ROUND_NAME)
        .execute()
    )
    return bool(res.data)


def build_player_select(label, df, position, key):
    options = df[df["position"] == position]
    return st.selectbox(
        label,
        options=options["player_id"],
        format_func=lambda pid: (
            f"{options.loc[options.player_id == pid, 'name'].iloc[0]}"
            f" (${options.loc[options.player_id == pid, 'price'].iloc[0]})"
        ),
        key=key
    )
# --------------------------------------------------

leagues = load_leagues()
managers = load_managers()

leagues = leagues.merge(
    managers,
    left_on=["league_id", "league_champion_rid"],
    right_on=["league_id", "roster_id"],
    how="left"
).rename(columns={"display_name": "champion"})

players_df = load_players(list(DIV_ROUND_PRICES.keys()))
players_df = players_df.sort_values(by=["position", "price"], ascending=[True, False])

left, right = st.columns([2,6])
with left:
    st.image("Pictures/SL_logo.png", width=200)

with right:
    st.write('''
    ### 📝 Champ of Champs Tippspiel
             
    Liebe Stoned Lack Army,
    das **Champ-of-Champs Tippspiel** kürt den ultimativen Champion der Stoned Lack Ligen in der Saison 2025!
             
    Alle Champions der Stoned Lack 2025er Redraft- und Dynasty-Ligen treten gegeneinander an, um zu beweisen, wer der wahre Meister ist.
    Wähle dein Lineup für jede Runde der Postseason und sammle Punkte basierend auf den Leistungen deiner getippten Spieler.
    Am Ende der Postseason wird der Champion mit den meisten Punkten zur Champ-of-Champs-Krone gekrönt!

    ***Neu:**
    Neben den diesjährigen Champs aus den Redraft- und Dynasty-Ligen, können dieses Jahr alle Interessierten am Tippspiel teilnehmen.
    Für die Champ-of-Champs-Krone zählen aber natürlich nur die Ergebnisse unter den Champions 2025.*

    *Für alle anderen gilt: Viel Spaß beim Mitmachen und mit den Champs messen!*
    ''')
    st.markdown("---")
    st.write('''
    ### 🏆 So funktioniert's:
    1. **Anmeldung:** Melde dich mit deinem Sleeper-Benutzernamen an.
    2. **Tipps abgeben:** Wähle in der aktuellen Tipprunde dein Lineup.
    3. **Punkte sammeln**: Sammle über die komplette Postseason Punkte basierend auf den Leistungen deiner getippten Spieler.
    4. **Gewinnen:** Der Champ mit den meisten Punkten am Ende der Postseason gewinnt die Champ-of-Champs-Krone!
    ''')

    st.markdown("---")
    st.write('''
    ### 📅 Wichtige Daten:
    - **Anmeldung & Tipps abgeben:** die Tippabgabe ist in der jeweiligen Woche bis zum Beginn der ersten Partie möglich.
    - **Postseason:** Die Postseason beginnt nach Abschluss der regulären Saison 2025.
    - **Gewinnerbekanntgabe:** Der Gewinner wird nach Abschluss der Postseason bekannt gegeben.
    ''')
    st.markdown("---")
    Scoring_info = st.expander("ℹ️ Wie werden die Punkte berechnet?")
    Scoring_info.markdown('''
    Es gelten die Statistiken der sleeper-App sowie das Standard-Scoring der Stoned Lack Ligen (1 PPR).
                       
    Folgendes Scoring wird angewendet:             
    | Kategorie                     | Wert                              | Punkt/e                |
    |-------------------------------|-----------------------------------|-----------------------|
    | Rushing / Receiving Yards     | pro 10 Yards                              | 1              |
    | Rushing / Receiving Touchdown | pro Touchdown                     | 6               |
    | Receptions (PPR)              | pro Reception                     | 1                |      
    | Passing Yards                 | pro 25 Yards                              | 1           |
    | Passing Touchdowns            | pro Touchdown                     | 4               |
    | Interceptions                 | pro Interception                  | -2              |
    | Fumble Lost                  | pro Fumble Lost                        | -2              |
    | Field Goal Made               | 0–39 Yards                        | 3               |
    | Field Goal Made               | 40–49 Yards                       | 4               |
    | Field Goal Made               | 50+ Yards                         | 5               |
    | Field Goal Missed             | pro Field Goal Missed                    | -1               |
    | Extra Points Made             | pro Extra Point                   | 1                |
    | Extra Points Missed           | pro Extra Point Missed                   | -1               |
    ''')
    st.subheader("Aktuelle Champions 2025")
    champs = st.expander("Liste der SL-Champs 2025")
    champs.dataframe(
        leagues[["league_name", "champion"]], 
        hide_index=True,
        column_config={
            # "league_type": "Typ",
            "league_name": "Liga",
            "champion": "Champion 2025"
        }
        )
    st.subheader("Tippspiel Divisonal Round")
    st.image("Pictures/DIV_ROUND.webp", width="stretch")
    div_round_players = {
        "4881":5,
        "4866":5,
        "6794":5,
        "5012":5,
        "11566":3,
        "8150":3,
        "9493":3,
        "7600":3,
        "11563":1,
        "11584":1,
        "5045":1,
        "9484":1,
        "6797":0,
        "4018":0,
        "11618":0,
        "10236":0
    }

    st.markdown("---")

    qb = build_player_select("Quarterback", players_df, "QB", "qb")
    rb = build_player_select("Running Back", players_df, "RB", "rb")
    wr = build_player_select("Wide Receiver", players_df, "WR", "wr")
    te = build_player_select("Tight End", players_df, "TE", "te")

    prices = players_df.set_index("player_id")["price"].to_dict()
    total_price = prices[qb] + prices[wr] + prices[rb] + prices[te]

    st.metric("💰 Budget", f"{total_price} $", delta=f"{BUDGET_LIMIT - total_price} $")

    if total_price > BUDGET_LIMIT:
        st.warning("⚠️ Budget überschritten")

    st.markdown("---")
    sleeper_username = st.text_input("Sleeper-Benutzername")

    if st.button("Lineup absenden"):
        if not sleeper_username:
            st.error("Bitte Sleeper-Benutzername eingeben.")
            st.stop()

        if not validate_sleeper_user(sleeper_username):
            st.error("Sleeper-Benutzername existiert nicht.")
            st.stop()

        if existing_submission(sleeper_username):
            st.warning("Dein Lineup wurde erfolgreich aktualisiert.")

        if total_price > BUDGET_LIMIT:
            st.error("Budget überschritten.")
            st.stop()

        lineup = {
            "lineup_id": str(uuid.uuid4()),
            "sleeper_username": sleeper_username.lower(),
            "sleeper_user_id": validate_sleeper_user(sleeper_username),
            "qb_id": qb,
            "wr_id": wr,
            "rb_id": rb,
            "te_id": te,
            "total_price": total_price,
            "round": ROUND_NAME,
            "week": DIV_ROUND_WEEK,
            "submission_time": datetime.now().isoformat()
        }

        res = supabase.table("lineups").insert(lineup).execute()
        if res.data:
            st.success("✅ Lineup erfolgreich gespeichert!")
        else:
            st.error("❌ Fehler beim Speichern.")

    st.markdown("---")
    for key,_ in div_round_players.items():
        url = f"https://api.sleeper.com/stats/nfl/player/{key}?season_type=regular&season=2025&grouping=week"
        response = requests.get(url)
        week_data = response.json()[str(DIV_ROUND_WEEK)]
        if not week_data:
            ppr_points = 0
        else:
            rushing_points = week_data.get("stats", {}).get("rush_yd", 0) / 10 + \
                             week_data.get("stats", {}).get("rush_td", 0) * 6
            receiving_points = week_data.get("stats", {}).get("rec_yd", 0) / 10 + \
                               week_data.get("stats", {}).get("rec_td", 0) * 6 + \
                               week_data.get("stats", {}).get("rec", 0) * 1
            passing_points = week_data.get("stats", {}).get("pass_yd", 0) / 25 + \
                             week_data.get("stats", {}).get("pass_td", 0) * 4 + \
                             week_data.get("stats", {}).get("pass_int", 0) * -1
            fumble_points = week_data.get("stats", {}).get("fum_lost", 0) * -2
            kicking_points = 0
            fg_made_0_39 = week_data.get("stats", {}).get("fgm_0_39", 0) * 3
            fg_made_40_49 = week_data.get("stats", {}).get("fgm_40_49", 0) * 4
            fg_made_50_plus = week_data.get("stats", {}).get("fgm_50_plus", 0) * 5
            fg_missed = week_data.get("stats", {}).get("fgm_missed", 0) * -1
            xp_made = week_data.get("stats", {}).get("xpm", 0) * 1
            xp_missed = week_data.get("stats", {}).get("xpm_missed", 0) * -1
            kicking_points = fg_made_0_39 + fg_made_40_49 + fg_made_50_plus + fg_missed + xp_made + xp_missed
            ppr_points = rushing_points + receiving_points + passing_points + fumble_points + kicking_points

        players_df.loc[
            players_df["player_id"] == key, "ppr_points"
        ] = ppr_points

    lineup_data = pd.DataFrame(
        supabase.table("latest_lineups_per_user")
        .select("*")
        .execute()
        .data
    )
 
    lineup_data = lineup_data.merge(
        players_df[["player_id", "name", "ppr_points"]],
        left_on="qb_id",
        right_on="player_id",
        how="left"
    ).rename(columns={"name": "QB", "ppr_points": "QB Punkte"}).drop(columns=["player_id"])
    lineup_data = lineup_data.merge(
        players_df[["player_id", "name", "ppr_points"]],
        left_on="wr_id",
        right_on="player_id",
        how="left"
    ).rename(columns={"name": "WR", "ppr_points": "WR Punkte"}).drop(columns=["player_id"])
    lineup_data = lineup_data.merge(
        players_df[["player_id", "name", "ppr_points"]],
        left_on="rb_id",
        right_on="player_id",
        how="left"
    ).rename(columns={"name": "RB", "ppr_points": "RB Punkte"}).drop(columns=["player_id"])
    lineup_data = lineup_data.merge(
        players_df[["player_id", "name", "ppr_points"]],
        left_on="te_id",
        right_on="player_id",
        how="left"
    ).rename(columns={"name": "TE", "ppr_points": "TE Punkte"}).drop(columns=["player_id"])
    lineup_data["total_points"] = (
        lineup_data["QB Punkte"].fillna(0) +
        lineup_data["WR Punkte"].fillna(0) +
        lineup_data["RB Punkte"].fillna(0) +
        lineup_data["TE Punkte"].fillna(0)
    )   
    lineup_data = lineup_data.sort_values(
        by=["total_points", "submission_time"],
        ascending=[False, True]
    ).reset_index(drop=True)
    lineup_data.index += 1
    coc_data = lineup_data[
        lineup_data["sleeper_username"].str.lower().isin(
            [c.lower() for c in leagues["champion"]]
        )
    ].reset_index(drop=True)
    coc_data.index += 1
    st.markdown("#### Champ of Champs Rangliste")
    st.dataframe(coc_data[["total_points","sleeper_username", "QB", "QB Punkte","WR","WR Punkte",
                 "RB","RB Punkte","TE","TE Punkte"]],
                 column_config={
                    "total_points": "Punkte",
                    "sleeper_username": "Sleepername"
                 })
    st.markdown("#### Offene Runde")
    st.dataframe(lineup_data[["total_points","sleeper_username", "QB", "QB Punkte","WR","WR Punkte",
                 "RB","RB Punkte","TE","TE Punkte"]],
                 column_config={
                    "total_points": "Punkte",
                    "sleeper_username": "Sleepername"
                 })
    st.markdown("---")
    st.write("© 2026 Stoned Lack Army")