# ==================================================
# Champ of Champs Tippspiel (Wildcard + Divisional + Gesamt)
# ==================================================

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import uuid
import itertools

import streamlit as st
import pandas as pd

from supabase import create_client, Client

from CoC_methods import (
    load_leagues,
    load_managers,
    load_players,
    load_weekly_player_stats,
    validate_sleeper_user,
    load_latest_lineups,
    build_player_select,
)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ROUND_CONFIGS = {
    "Wildcard": {
        "week": 1,
        "budget": 9,
        "kickoff_utc": datetime(2026, 1, 10, 21, 30, tzinfo=timezone.utc),
        "prices": {
            "4984": 5,
            "4034": 5,
            "9493": 5,
            "4217": 5,
            "11564": 3,
            "7543": 3,
            "7569": 3,
            "5022": 3,
            "7523": 1,
            "7567": 1,
            "8167": 1,
            "5001": 1,
            "6797": 0,
            "6790": 0,
            "12526": 0,
            "12517": 0
        },
        "image": "Pictures/IMG_5295.webp",
    },

    "Divisional": {
        "week": 2,  # ✅ wichtig: Divisional sollte nicht week=1 sein
        "budget": 9,
        "kickoff_utc": datetime(2026, 1, 17, 21, 30, tzinfo=timezone.utc),  # <- Beispiel (ändern!)
        "prices": {
            # ✅ später hier die echten Divisional-IDs/Preise rein
            # "4984": 5,
            # "4034": 5,
            # "9493": 5,
            # "4217": 5,
            # "11564": 3,
            # "7543": 3,
            # "7569": 3,
            # "5022": 3,
            # "7523": 1,
            # "7567": 1,
            # "8167": 1,
            # "5001": 1,
            # "6797": 0,
            # "6790": 0,
            # "12526": 0,
            # "12517": 0
        },
        # "image": "Pictures/IMG_5295.webp",
    },
}

berlin_time = ROUND_CONFIGS["Divisional"]["kickoff_utc"].astimezone(ZoneInfo("Europe/Berlin"))
# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def keep_latest_per_user(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nimmt pro sleeper_username nur den letzten Eintrag (nach submission_time).
    Kein Kickoff-Filter -> gut für Gesamtwertung, wenn Historie vollständig bleiben soll.
    """
    if df.empty:
        return df

    df = df.copy()
    df["submission_time"] = pd.to_datetime(df["submission_time"], utc=True, errors="coerce")
    df = df.dropna(subset=["submission_time"])

    df = df.sort_values("submission_time")
    df = df.drop_duplicates(subset=["sleeper_username"], keep="last")

    return df


def keep_latest_submission(df: pd.DataFrame, kickoff_utc: datetime) -> pd.DataFrame:
    """
    Historie bleibt erhalten (mehrere Inserts).
    Für Wertung zählt nur die letzte Einsendung pro User bis Kickoff.
    """
    if df.empty:
        return df

    df = df.copy()

    # submission_time sicher zu datetime (UTC)
    df["submission_time"] = pd.to_datetime(df["submission_time"], utc=True, errors="coerce")
    df = df.dropna(subset=["submission_time"])

    # nur Einsendungen bis Kickoff zählen
    df = df[df["submission_time"] <= kickoff_utc]

    # pro User nur letzte Einsendung behalten
    df = df.sort_values("submission_time")
    df = df.drop_duplicates(subset=["sleeper_username"], keep="last")

    return df


def merge_position_points(lineup_df: pd.DataFrame, players_df: pd.DataFrame, pos_col: str, label: str) -> pd.DataFrame:
    """
    Merged Player-Name und ppr_points für eine Positions-ID-Spalte.
    """
    return (
        lineup_df.merge(
            players_df[["player_id", "name", "ppr_points"]],
            left_on=pos_col,
            right_on="player_id",
            how="left"
        )
        .rename(columns={"name": label, "ppr_points": f"{label} pts"})
        .drop(columns=["player_id"])
    )


# --------------------------------------------------
# RENDER FUNCTIONS
# --------------------------------------------------
def render_round(round_name: str, cfg: dict, leagues: pd.DataFrame):
    POST_WEEK = cfg["week"]
    BUDGET_LIMIT = cfg["budget"]
    PRICES = cfg["prices"]

    FIRST_GAME_KICKOFF = cfg["kickoff_utc"].replace(tzinfo=ZoneInfo("UTC"))
    berlin_time = FIRST_GAME_KICKOFF.astimezone(ZoneInfo("Europe/Berlin"))

    # Sicherheitscheck
    if not PRICES:
        st.warning(f"⚠️ Für **{round_name}** sind noch keine Spielerpreise hinterlegt.")
        return

    st.header(f"{round_name} Round")

    if cfg.get("image"):
        st.image(cfg["image"], width="stretch")

    st.info(f"⏳ Tippabgabe bis: **{berlin_time.strftime('%d.%m.%Y um %H:%M Uhr')}**")

    # Spieler + Stats laden
    players_df = load_players(list(PRICES.keys()), PRICES)
    players_df = players_df.sort_values(by=["position", "price"], ascending=[True, False])

    stats = load_weekly_player_stats(POST_WEEK, PRICES)
    players_df["ppr_points"] = players_df["player_id"].map(stats).fillna(0)

    # --------------------------------------------------
    # FORMULAR
    # --------------------------------------------------
    with st.container():
        if datetime.now(timezone.utc) >= FIRST_GAME_KICKOFF:
            st.error(f"⏰ Die Eingabe für **{round_name}** ist nicht mehr möglich. Das erste Spiel hat bereits begonnen.")
        else:
            left, right = st.columns(2)

            with left:
                qb = build_player_select("Quarterback", players_df, "QB", f"{round_name}_qb")
                wr = build_player_select("Wide Receiver", players_df, "WR", f"{round_name}_wr")

            with right:
                rb = build_player_select("Running Back", players_df, "RB", f"{round_name}_rb")
                te = build_player_select("Tight End", players_df, "TE", f"{round_name}_te")

            prices = players_df.set_index("player_id")["price"].to_dict()
            total_price = prices.get(qb, 0) + prices.get(wr, 0) + prices.get(rb, 0) + prices.get(te, 0)

            st.metric(
                label="Budget Auswahl",
                value=f"{total_price} $",
                delta=f"{total_price - BUDGET_LIMIT} $",
                border=True,
                delta_color="inverse"
            )

            if total_price > BUDGET_LIMIT:
                st.warning("⚠️ Budget überschritten")

            sleeper_username = st.text_input(f"Sleeper-Benutzername ({round_name})")
            sleeper_user_id = validate_sleeper_user(sleeper_username)

            if st.button(f"Lineup absenden ({round_name})"):
                now_utc = datetime.now(timezone.utc)

                if now_utc >= FIRST_GAME_KICKOFF:
                    st.error("⏰ Die Eingabe ist nicht mehr möglich. Das erste Spiel hat bereits begonnen.")
                    st.stop()

                if not sleeper_user_id:
                    st.error("Sleeper-Benutzername existiert nicht.")
                    st.stop()

                if total_price > BUDGET_LIMIT:
                    st.error("Budget überschritten.")
                    st.stop()

                # Info: Historie behalten -> wir insertieren immer
                existing = (
                    supabase.table("lineups")
                    .select("lineup_id")
                    .eq("sleeper_username", sleeper_username.lower())
                    .eq("round", round_name)
                    .execute()
                )
                if existing.data:
                    st.warning("Lineup aktualisiert – **für die Wertung zählt nur deine letzte Einsendung**.")

                lineup = {
                    "lineup_id": str(uuid.uuid4()),
                    "sleeper_username": sleeper_username.lower(),
                    "sleeper_user_id": sleeper_user_id,
                    "qb_id": qb,
                    "wr_id": wr,
                    "rb_id": rb,
                    "te_id": te,
                    "total_price": total_price,
                    "round": round_name,
                    "week": POST_WEEK,
                    "submission_time": datetime.now(timezone.utc).isoformat()
                }

                res = supabase.table("lineups").insert(lineup).execute()

                if res.data:
                    st.success("✅ Lineup erfolgreich gespeichert!")
                else:
                    st.error("❌ Fehler beim Speichern.")

    # --------------------------------------------------
    # BEST / WORST Lineup (theoretisch optimal)
    # --------------------------------------------------
    lineups = []

    qb_pool = players_df[players_df["position"] == "QB"]
    wr_pool = players_df[players_df["position"] == "WR"]
    rb_pool = players_df[players_df["position"] == "RB"]
    te_pool = players_df[players_df["position"] == "TE"]

    for q, w, r, t in itertools.product(
        qb_pool.itertuples(index=False),
        wr_pool.itertuples(index=False),
        rb_pool.itertuples(index=False),
        te_pool.itertuples(index=False),
    ):
        cost = q.price + w.price + r.price + t.price
        if cost <= BUDGET_LIMIT:
            pts = q.ppr_points + w.ppr_points + r.ppr_points + t.ppr_points
            lineups.append({
                "QB": q.name,
                "WR": w.name,
                "RB": r.name,
                "TE": t.name,
                "cost": cost,
                "points": round(pts, 2)
            })

    if lineups:
        st.markdown("---")
        lineups_df = pd.DataFrame(lineups)
        best_lineup = lineups_df.loc[lineups_df["points"].idxmax()]
        worst_lineup = lineups_df.loc[lineups_df["points"].idxmin()]

        left, right = st.columns(2)

        left.markdown(f"#### ⭐️ :green[Bestmögliches Lineup] (Kosten: {best_lineup['cost']} $, Punkte: {best_lineup['points']})")
        left.write(
            f"QB: {best_lineup['QB']}  \n"
            f"WR: {best_lineup['WR']}  \n"
            f"RB: {best_lineup['RB']}  \n"
            f"TE: {best_lineup['TE']}"
        )

        right.markdown(f"#### ⛔️ :red[Schlechtestes Lineup] (Kosten: {worst_lineup['cost']} $, Punkte: {worst_lineup['points']})")
        right.write(
            f"QB: {worst_lineup['QB']}  \n"
            f"WR: {worst_lineup['WR']}  \n"
            f"RB: {worst_lineup['RB']}  \n"
            f"TE: {worst_lineup['TE']}"
        )

    # --------------------------------------------------
    # RANKINGS
    # --------------------------------------------------
    st.markdown("---")
    st.subheader(f"Ranglisten – {round_name}")

    if st.button(f"🔄 Ranglisten neu laden ({round_name})", type="tertiary"):
        load_latest_lineups.clear()
        load_weekly_player_stats.clear()
        st.rerun()

    lineup_data = load_latest_lineups()
    lineup_data = lineup_data[lineup_data["round"] == round_name].copy()

    # ✅ nur letzte Einsendung pro User vor Kickoff
    lineup_data = keep_latest_submission(lineup_data, FIRST_GAME_KICKOFF)

    # Positionen mergen
    lineup_data = merge_position_points(lineup_data, players_df, "qb_id", "QB")
    lineup_data = merge_position_points(lineup_data, players_df, "wr_id", "WR")
    lineup_data = merge_position_points(lineup_data, players_df, "rb_id", "RB")
    lineup_data = merge_position_points(lineup_data, players_df, "te_id", "TE")

    lineup_data["total_points"] = (
        lineup_data["QB pts"].fillna(0)
        + lineup_data["WR pts"].fillna(0)
        + lineup_data["RB pts"].fillna(0)
        + lineup_data["TE pts"].fillna(0)
    )

    lineup_data = lineup_data.sort_values(
        by=["total_points", "submission_time"],
        ascending=[False, True]
    ).reset_index(drop=True)

    if not lineup_data.empty:
        lineup_data.index += 1
        lineup_data["To 1st"] = lineup_data["total_points"].max() - lineup_data["total_points"]
    else:
        lineup_data["To 1st"] = []

    # Picks verstecken solange Runde offen
    if datetime.now(timezone.utc) < FIRST_GAME_KICKOFF:
        lineup_data[["QB", "WR", "RB", "TE"]] = "-"

    champion_set = set(leagues["champion"].dropna().str.lower())
    coc_data = lineup_data[lineup_data["sleeper_username"].str.lower().isin(champion_set)].copy()
    coc_data = coc_data.reset_index(drop=True)
    if not coc_data.empty:
        coc_data.index += 1

    st.markdown("#### 👑 :yellow[Champ of Champs Rangliste]")
    st.dataframe(
        coc_data[["total_points", "sleeper_username", "To 1st", "QB", "QB pts", "WR", "WR pts", "RB", "RB pts", "TE", "TE pts"]],
        column_config={"total_points": "Punkte", "sleeper_username": "Sleeper"}
    )

    st.markdown("#### 🏅 :red[Offene Runde]")
    st.dataframe(
        lineup_data[["total_points", "sleeper_username", "To 1st", "QB", "QB pts", "WR", "WR pts", "RB", "RB pts", "TE", "TE pts"]],
        column_config={"total_points": "Punkte", "sleeper_username": "Sleeper"}
    )


def render_total(leagues: pd.DataFrame):
    st.header("🏆 Gesamtwertung (alle Runden)")

    all_lineups = load_latest_lineups().copy()
    round_frames = []

    for round_name, cfg in ROUND_CONFIGS.items():
        PRICES = cfg["prices"]
        week = cfg["week"]
        kickoff = cfg["kickoff_utc"].replace(tzinfo=ZoneInfo("UTC"))

        if not PRICES:
            continue

        # Spieler + Stats je Runde
        players_df_r = load_players(list(PRICES.keys()), PRICES)
        stats_r = load_weekly_player_stats(week, PRICES)
        players_df_r["ppr_points"] = players_df_r["player_id"].map(stats_r).fillna(0)

        df_r = all_lineups[all_lineups["round"] == round_name].copy()
        df_r = keep_latest_per_user(df_r)

        if df_r.empty:
            continue

        # Punkte je lineup berechnen
        df_r = df_r.merge(players_df_r[["player_id", "ppr_points"]], left_on="qb_id", right_on="player_id", how="left").rename(columns={"ppr_points": "QB_pts"}).drop(columns=["player_id"])
        df_r = df_r.merge(players_df_r[["player_id", "ppr_points"]], left_on="wr_id", right_on="player_id", how="left").rename(columns={"ppr_points": "WR_pts"}).drop(columns=["player_id"])
        df_r = df_r.merge(players_df_r[["player_id", "ppr_points"]], left_on="rb_id", right_on="player_id", how="left").rename(columns={"ppr_points": "RB_pts"}).drop(columns=["player_id"])
        df_r = df_r.merge(players_df_r[["player_id", "ppr_points"]], left_on="te_id", right_on="player_id", how="left").rename(columns={"ppr_points": "TE_pts"}).drop(columns=["player_id"])

        df_r["round_points"] = (
            df_r["QB_pts"].fillna(0)
            + df_r["WR_pts"].fillna(0)
            + df_r["RB_pts"].fillna(0)
            + df_r["TE_pts"].fillna(0)
        )

        df_r["round"] = round_name
        round_frames.append(df_r[["sleeper_username", "round", "round_points"]])

    if not round_frames:
        st.info("Noch keine Runden-Daten vorhanden.")
        return

    pts_all = pd.concat(round_frames, ignore_index=True)

    # Gesamtpunkte je User
    leaderboard = (
        pts_all.groupby("sleeper_username", as_index=False)["round_points"]
        .sum()
        .rename(columns={"round_points": "Punkte Total", "sleeper_username": "Username"})
        .sort_values("Punkte Total", ascending=False)
        .reset_index(drop=True)
    )
    leaderboard.index += 1

    champion_set = set(leagues["champion"].dropna().str.lower())
    leaderboard_coc = leaderboard[leaderboard["Username"].str.lower().isin(champion_set)].copy()
    leaderboard_coc = leaderboard_coc.reset_index(drop=True)
    leaderboard_coc.index += 1

    st.subheader("👑 Champ of Champs Gesamtwertung")
    st.dataframe(leaderboard_coc)

    st.subheader("🏅 Offene Gesamtwertung (alle Teilnehmer)")
    st.dataframe(leaderboard)

    # Round Breakdown
    pivot = (
    pts_all.pivot_table(
        index="sleeper_username",
        columns="round",
        values="round_points",
        aggfunc="sum",
        fill_value=0,
    )
    .rename(columns=lambda x: f"{x} pts")
    .reset_index()
    .rename(columns={"sleeper_username": "Username"})
    )
    pivot.index += 1


    st.subheader("📊 Breakdown pro Runde")
    st.dataframe(pivot)


# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
# Champions laden
leagues = load_leagues()
managers = load_managers()

leagues = (
    leagues.merge(
        managers,
        left_on=["league_id", "league_champion_rid"],
        right_on=["league_id", "roster_id"],
        how="left"
    )
    .rename(columns={"display_name": "champion"})
)

left, right = st.columns([2,15],width="stretch", vertical_alignment="center")
with left:
    st.image("Pictures/SL_logo.png", width=200)

with right:
    st.header("Champ of Champs Tippspiel")

st.write('''             
Liebe Stoned Lack Army,
das **Champ-of-Champs Tippspiel** kürt den ultimativen Champion der Stoned Lack Ligen in der Saison 2025!
            
Alle Champions der Stoned Lack 2025er Redraft- und Dynasty-Ligen treten gegeneinander an, um zu beweisen, wer der wahre Meister ist.
Wähle dein Lineup für jede Runde der Postseason und sammle Punkte basierend auf den Leistungen deiner getippten Spieler.
Am Ende der Postseason wird der Champion mit den meisten Punkten zur Champ-of-Champs-Krone gekrönt!

***Neu:**
Neben den diesjährigen Champs aus den Redraft- und Dynasty-Ligen, können dieses Jahr alle Interessierten am Tippspiel teilnehmen.
Für die Champ-of-Champs-Krone zählen aber natürlich nur die Ergebnisse unter den Champions 2025.*

*Für alle anderen gilt: Viel Spaß beim Mitmachen und mit den Champs messen!*''')
st.divider()
st.header("Organisatorisches")
st.write('''
#### 🏆 So funktioniert's:
1. **Anmeldung:** Melde dich mit deinem Sleeper-Benutzernamen an.  
          Jeder Champion kann nur einmalig teilnehmen, auch wenn er/sie in mehreren Ligen gewonnen hat.
2. **Tipps abgeben:** Wähle in der aktuellen Tipprunde dein Lineup.
3. **Punkte sammeln**: Sammle über die komplette Postseason Punkte basierend auf den Leistungen deiner getippten Spieler.
4. **Gewinnen:** Der Champ mit den meisten Punkten am Ende der Postseason gewinnt die Champ-of-Champs-Krone!
''')
st.divider()
st.write(f'''
#### 📅 Wichtige Daten:
- **Anmeldung & Tipps abgeben:** die Tippabgabe ist in der jeweiligen Woche bis zum Beginn der ersten Partie möglich.
- **Divisional Round:** Die Runde kann bis zum {berlin_time.strftime("%d.%m.%Y um %H:%M Uhr")} getippt werden.
- **Gewinnerbekanntgabe:** Der Gewinner wird nach Abschluss der Postseason bekannt gegeben.
''')
# st.markdown("---")
Scoring_info = st.expander("Wie werden die Punkte berechnet?")
Scoring_info.markdown('''
Es gelten die Statistiken der sleeper-App sowie das Standard-Scoring der Stoned Lack Ligen (1 PPR).
                    
Folgendes Scoring wird angewendet:
                      <center>        
| Kategorie                     | Wert                              | Punkt/e                |
|-------------------------------|-----------------------------------|-----------------------|
| Rushing / Receiving Yards     | pro 10 Yards                              | 1              |
| Rushing / Receiving Touchdown | pro Touchdown                     | 6               |
| Receptions (PPR)              | pro Reception                     | 1                |      
| Passing Yards                 | pro 25 Yards                              | 1           |
| Passing Touchdowns            | pro Touchdown                     | 4               |
| **2-Pt Conversion (pass/rec/rush)**          | **pro 2-pt**           | **2***               |
| Interceptions                 | pro Interception                  | -2              |
| Fumble Lost                  | pro Fumble Lost                        | -2              |
 </center>
                      * nachträglich hinzugefügt, gilt (auch rückwirkend) für alle Runden
                      ''', unsafe_allow_html=True)
# | Field Goal Made               | 0–39 Yards                        | 3               |
# | Field Goal Made               | 40–49 Yards                       | 4               |
# | Field Goal Made               | 50+ Yards                         | 5               |
# | Field Goal Missed             | pro Field Goal Missed                    | -1               |
# | Extra Points Made             | pro Extra Point                   | 1                |
# | Extra Points Missed           | pro Extra Point Missed                   | -1               |

st.write("#### 🏆 Aktuelle Champions 2025")
champs = st.expander("Liste der SL-Champs 2025")
left, right = champs.columns(2)
left.write("**Liga**")
right.write("**Champion**")
for _, col in leagues[["league_name", "champion"]].iterrows():
    left.write(f"**{col['league_name'].strip()}**:")
    right.write(f"{col['champion']}")
n_winner = len(leagues["champion"].unique())
n_leagues = len(leagues["league_name"].unique())
st.divider()

# Tabs
tab_wc, tab_div, tab_total = st.tabs(["Wildcard", "Divisional", "Gesamt"])

with tab_wc:
    render_round("Wildcard", ROUND_CONFIGS["Wildcard"], leagues)

with tab_div:
    render_round("Divisional", ROUND_CONFIGS["Divisional"], leagues)

with tab_total:
    render_total(leagues)
