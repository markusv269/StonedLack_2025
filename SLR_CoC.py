# ==================================================
# Champ of Champs Tippspiel (Wildcard + Divisional + Gesamt)
# ==================================================

from datetime import datetime, timezone
from statistics import mode
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
            "4984": 5, "4034": 5, "9493": 5, "4217": 5,
            "11564": 3, "7543": 3, "7569": 3, "5022": 3,
            "7523": 1, "7567": 1, "8167": 1, "5001": 1,
            "6797": 0, "6790": 0, "12526": 0, "12517": 0
        },
        "image": "Pictures/IMG_5295.webp",
    },

    "Divisional": {
        "week": 2,  # ✅ wichtig: Divisional sollte nicht week=1 sein
        "budget": 9,
        "kickoff_utc": datetime(2026, 1, 17, 21, 30, tzinfo=timezone.utc),  # <- Beispiel (ändern!)
        "prices": {
            # ✅ später hier die echten Divisional-IDs/Preise rein
            "11563": 5, "8150": 5, "9488": 5, "12517": 5,
            "11560": 3, "8698": 3, "2133": 3, "8138": 3,
            "8183": 1, "12489": 1, "5045": 1, "3214": 1,
            "9758": 0, "7611": 0, "12519": 0, "6865": 0
        },
        "image": "Pictures/Cheers.webp",
    },
    "Conference": {
        "week": 3,
        "budget": 9,
        "kickoff_utc": datetime(2026, 1, 25, 20, 0, tzinfo=timezone.utc),
        "prices": {
            "11564": 5, "8150": 5, "9488": 5, "3214": 5,
            "421": 3, "8151": 3, "2133": 3, "4066": 3,
            "4943": 1, "12489": 1, "9494": 1, "6865": 1,
            "6136": 0, "7611": 0, "9504": 0, "11603": 0,
        },
        "image": "Pictures/Cheers_2.webp",
    },
    "Super Bowl": {
        "week": 4,
        "kickoff_utc": datetime(2026, 2, 8, 23, 30, tzinfo=timezone.utc),

        # ✅ neues Mode-Flag
        "mode": "fixed_multipliers",

        # ✅ feste Multiplikatoren pro Spieler-ID (wie vorher Preise)
        "prices": {
            # "4984": 5,   # Spieler A ist x5
            # "4034": 5,   # Spieler B ist x5
            # "9493": 3,   # Spieler C ist x3
            # "4217": 1,   # Spieler D ist x1
            # ...
        },
        # "image": "Pictures/Cheers_2.webp",
},
}

berlin_time = ROUND_CONFIGS["Divisional"]["kickoff_utc"].astimezone(ZoneInfo("Europe/Berlin"))
# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def merge_pick_fixed_multiplier(
    lineup_df: pd.DataFrame,
    players_df: pd.DataFrame,
    id_col: str,
    label: str,
) -> pd.DataFrame:
    """
    Merged Spielername, Fantasy-Punkte und festen Multiplikator (players_df['price'])
    und berechnet Tippspiel-Punkte = base * mult.
    """
    out = (
        lineup_df.merge(
            players_df[["player_id", "name", "ppr_points", "price"]],
            left_on=id_col,
            right_on="player_id",
            how="left",
        )
        .rename(columns={"name": label, "ppr_points": f"{label} base", "price": f"{label} mult"})
        .drop(columns=["player_id"])
    )
    out[f"{label} pts"] = out[f"{label} base"].fillna(0) * out[f"{label} mult"].fillna(0)
    return out

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

def render_super_bowl_fixed_multipliers(round_name: str, cfg: dict, players_df: pd.DataFrame, leagues: pd.DataFrame):
    kickoff_utc = cfg["kickoff_utc"].replace(tzinfo=ZoneInfo("UTC"))

    # "price" = Multiplikator (1/3/5)
    players_df = players_df.copy()
    players_df = players_df.sort_values(["price", "ppr_points"], ascending=[False, False]).reset_index(drop=True)

    id_to_row = players_df.set_index("player_id")[["name", "position", "ppr_points", "price"]].to_dict("index")
    options = players_df["player_id"].tolist()

    def fmt(pid: str) -> str:
        r = id_to_row.get(pid, {})
        return f"{r.get('name','?')} (x{r.get('price',0)})"

    # -----------------------
    # Formular: 3 Picks
    # -----------------------
    with st.container():
        if datetime.now(timezone.utc) >= kickoff_utc:
            st.error(f"⏰ Die Eingabe für **{round_name}** ist nicht mehr möglich. Das erste Spiel hat bereits begonnen.")
        else:
            c1, c2, c3 = st.columns(3)

            with c1:
                p1 = st.selectbox("Pick 1", options=options, format_func=fmt, key=f"{round_name}_p1")
            with c2:
                p2 = st.selectbox("Pick 2", options=[o for o in options if o != p1], format_func=fmt, key=f"{round_name}_p2")
            with c3:
                p3 = st.selectbox("Pick 3", options=[o for o in options if o not in {p1, p2}], format_func=fmt, key=f"{round_name}_p3")

            # ✅ nur IDs müssen verschieden sein – Multiplikator darf gleich sein (z.B. 3× x5)
            if len({p1, p2, p3}) != 3:
                st.error("Bitte 3 verschiedene Spieler auswählen.")
                st.stop()

            # tip_points = (
            #     id_to_row[p1]["ppr_points"] * id_to_row[p1]["price"] +
            #     id_to_row[p2]["ppr_points"] * id_to_row[p2]["price"] +
            #     id_to_row[p3]["ppr_points"] * id_to_row[p3]["price"]
            # )
            # st.metric("Deine Tippspiel-Punkte (Preview)", f"{round(tip_points,2)}")

            sleeper_username = st.text_input(f"Sleeper-Benutzername ({round_name})")
            sleeper_user_id = validate_sleeper_user(sleeper_username)

            if st.button(f"Lineup absenden ({round_name})"):
                now_utc = datetime.now(timezone.utc)

                if now_utc >= kickoff_utc:
                    st.error("⏰ Die Eingabe ist nicht mehr möglich. Das erste Spiel hat bereits begonnen.")
                    st.stop()

                if not sleeper_user_id:
                    st.error("Sleeper-Benutzername existiert nicht.")
                    st.stop()

                existing = (
                    supabase.table("lineups")
                    .select("lineup_id")
                    .eq("sleeper_username", sleeper_username.lower())
                    .eq("round", round_name)
                    .execute()
                )
                if existing.data:
                    st.warning("Lineup aktualisiert – **für die Wertung zählt nur deine letzte Einsendung**.")

                # ✅ Wir nutzen weiter qb_id/wr_id/rb_id als drei Picks (keine DB-Migration)
                lineup = {
                    "lineup_id": str(uuid.uuid4()),
                    "sleeper_username": sleeper_username.lower(),
                    "sleeper_user_id": sleeper_user_id,
                    "qb_id": p1,
                    "wr_id": p2,
                    "rb_id": p3,
                    "te_id": None,
                    "total_price": 0,
                    "round": round_name,
                    "week": cfg["week"],
                    "submission_time": datetime.now(timezone.utc).isoformat(),
                }

                res = supabase.table("lineups").insert(lineup).execute()
                if res.data:
                    st.success("✅ Lineup erfolgreich gespeichert!")
                else:
                    st.error("❌ Fehler beim Speichern.")

    # -----------------------
    # Theoretisch Best/Worst (3er-Kombi)
    # -----------------------
    st.markdown("---")
    if len(players_df) >= 3:
        combos = []
        rows = list(players_df.itertuples(index=False))
        for a, b, c in itertools.combinations(rows, 3):
            pts = a.ppr_points * a.price + b.ppr_points * b.price + c.ppr_points * c.price
            combos.append((pts, a.name, a.price, b.name, b.price, c.name, c.price))

        combos.sort(key=lambda x: x[0])
        worst = combos[0]
        best = combos[-1]

        left, right = st.columns(2)
        left.markdown(f"#### ⭐️ :green[Bestmögliche 3er-Kombi] (Punkte: {round(best[0],2)})")
        left.write(f"{best[1]} × x{best[2]}\n\n{best[3]} × x{best[4]}\n\n{best[5]} × x{best[6]}")

        right.markdown(f"#### ⛔️ :red[Schlechteste 3er-Kombi] (Punkte: {round(worst[0],2)})")
        right.write(f"{worst[1]} × x{worst[2]}\n\n{worst[3]} × x{worst[4]}\n\n{worst[5]} × x{worst[6]}")

    # -----------------------
    # Rankings
    # -----------------------
    st.markdown("---")
    st.subheader(f"Ranglisten – {round_name}")

    if st.button(f"🔄 Ranglisten neu laden ({round_name})", type="tertiary"):
        load_latest_lineups.clear()
        load_weekly_player_stats.clear()
        st.rerun()

    lineup_data = load_latest_lineups()
    lineup_data = lineup_data[lineup_data["round"] == round_name].copy()
    lineup_data = keep_latest_submission(lineup_data, kickoff_utc)

    # 3 Picks mergen (Name/base/mult/pts)
    lineup_data = merge_pick_fixed_multiplier(lineup_data, players_df, "qb_id", "P1")
    lineup_data = merge_pick_fixed_multiplier(lineup_data, players_df, "wr_id", "P2")
    lineup_data = merge_pick_fixed_multiplier(lineup_data, players_df, "rb_id", "P3")

    lineup_data["total_points"] = (
        lineup_data["P1 pts"].fillna(0) + lineup_data["P2 pts"].fillna(0) + lineup_data["P3 pts"].fillna(0)
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
    if datetime.now(timezone.utc) < kickoff_utc:
        lineup_data[["P1", "P2", "P3"]] = "-"

    champion_set = set(leagues["champion"].dropna().str.lower())
    coc_data = lineup_data[lineup_data["sleeper_username"].str.lower().isin(champion_set)].copy().reset_index(drop=True)
    if not coc_data.empty:
        coc_data.index += 1

    st.markdown("#### 👑 :yellow[Champ of Champs Rangliste]")
    st.dataframe(
        coc_data[["total_points", "sleeper_username", "To 1st", "P1", "P1 base", "P1 mult", "P2", "P2 base", "P2 mult", "P3", "P3 base", "P3 mult"]],
        column_config={"total_points": "Punkte", "sleeper_username": "Sleeper"},
    )

    st.markdown("#### 🏅 :red[Offene Runde]")
    st.dataframe(
        lineup_data[["total_points", "sleeper_username", "To 1st", "P1", "P1 base", "P1 mult", "P2", "P2 base", "P2 mult", "P3", "P3 base", "P3 mult"]],
        column_config={"total_points": "Punkte", "sleeper_username": "Sleeper"},
    )


# --------------------------------------------------
# RENDER FUNCTIONS
# --------------------------------------------------
def render_round(round_name: str, cfg: dict, leagues: pd.DataFrame):
    POST_WEEK = cfg["week"]
    PRICES = cfg["prices"]

    FIRST_GAME_KICKOFF = cfg["kickoff_utc"].astimezone(ZoneInfo("UTC"))
    berlin_time = FIRST_GAME_KICKOFF.astimezone(ZoneInfo("Europe/Berlin"))

    mode = cfg.get("mode", "budget")  # 👈 default wie bisher

    # Sicherheitscheck
    if not PRICES:
        st.warning(f"⚠️ Für **{round_name}** sind noch keine Spieler hinterlegt.")
        return

    st.header(f"{round_name} Round")

    if cfg.get("image"):
        st.image(cfg["image"], width="stretch")

    st.info(f"⏳ Tippabgabe bis: **{berlin_time.strftime('%d.%m.%Y um %H:%M Uhr')}**")

    # Spieler + Stats laden
    players_df = load_players(list(PRICES.keys()), PRICES)
    stats = load_weekly_player_stats(POST_WEEK, PRICES)
    players_df["ppr_points"] = players_df["player_id"].map(stats).fillna(0)

    # ✅ Super Bowl: feste Multiplikatoren pro Spieler (in PRICES)
    if mode == "fixed_multipliers":
        return render_super_bowl_fixed_multipliers(round_name, cfg, players_df, leagues)

    # --------------------------------------------------
    # ab hier: Budget-Runden (Wildcard/Div/Conf)
    # --------------------------------------------------
    BUDGET_LIMIT = cfg["budget"]  # 👈 jetzt erst lesen!
    players_df = players_df.sort_values(by=["position", "price"], ascending=[True, False])

    if mode == "fixed_multipliers":
        return render_super_bowl_fixed_multipliers(round_name, cfg, players_df, leagues)

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
        df_r = df_r.merge(players_df_r[["player_id", "ppr_points", "price"]], left_on="qb_id", right_on="player_id", how="left") \
           .rename(columns={"ppr_points": "QB_base", "price": "QB_mult"}).drop(columns=["player_id"])

        df_r = df_r.merge(players_df_r[["player_id", "ppr_points", "price"]], left_on="wr_id", right_on="player_id", how="left") \
                .rename(columns={"ppr_points": "WR_base", "price": "WR_mult"}).drop(columns=["player_id"])

        df_r = df_r.merge(players_df_r[["player_id", "ppr_points", "price"]], left_on="rb_id", right_on="player_id", how="left") \
                .rename(columns={"ppr_points": "RB_base", "price": "RB_mult"}).drop(columns=["player_id"])

        df_r = df_r.merge(players_df_r[["player_id", "ppr_points", "price"]], left_on="te_id", right_on="player_id", how="left") \
                .rename(columns={"ppr_points": "TE_base", "price": "TE_mult"}).drop(columns=["player_id"])
        mode = cfg.get("mode", "budget")

        if mode == "fixed_multipliers":
            # ✅ 3 Picks: qb_id/wr_id/rb_id
            df_r["round_points"] = (
                df_r["QB_base"].fillna(0) * df_r["QB_mult"].fillna(0) +
                df_r["WR_base"].fillna(0) * df_r["WR_mult"].fillna(0) +
                df_r["RB_base"].fillna(0) * df_r["RB_mult"].fillna(0)
            )
        else:
            df_r["round_points"] = (
                df_r["QB_base"].fillna(0) +
                df_r["WR_base"].fillna(0) +
                df_r["RB_base"].fillna(0) +
                df_r["TE_base"].fillna(0)
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
tab_wc, tab_div, tab_conf, tab_sb, tab_total = st.tabs(["Wildcard", "Divisional", "Conference", "Super Bowl", "Gesamtwertung"], default="Gesamtwertung")

with tab_wc:
    render_round("Wildcard", ROUND_CONFIGS["Wildcard"], leagues)

with tab_div:
    render_round("Divisional", ROUND_CONFIGS["Divisional"], leagues)

with tab_conf:
    render_round("Conference", ROUND_CONFIGS["Conference"], leagues)

with tab_sb:
    render_round("Super Bowl", ROUND_CONFIGS["Super Bowl"], leagues)

with tab_total:
    render_total(leagues)
