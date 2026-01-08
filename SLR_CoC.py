import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from supabase import create_client, Client
import supabase
import uuid
from CoC_methods import (
    load_leagues,
    load_managers,
    load_players,
    load_weekly_player_stats,
    validate_sleeper_user,
    existing_submission,
    load_latest_lineups,
    build_player_select
)
import pandas as pd

# st.set_page_config(layout="wide")


# --------------------------------------------------
# CONFIG
# --------------------------------------------------
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

POST_WEEK = 1
ROUND_NAME = "Wildcard"
BUDGET_LIMIT = 9

DIV_ROUND_PRICES = {
    "4984": 5,
    "4866": 5,
    "6794": 5,
    "5012": 5,
    "11566": 3,
    "8150": 3,
    "9493": 3,
    "7600": 3,
    "11563": 1,
    "11584": 1,
    "5045": 1,
    "9484": 1,
    "6797": 0,
    "4018": 0,
    "11618": 0,
    "10236": 0
}

FIRST_GAME_KICKOFF = datetime(
    2026, 1, 10, 21, 30, tzinfo=timezone.utc  # Beispiel!
)
FIRST_GAME_KICKOFF = FIRST_GAME_KICKOFF.replace(tzinfo=ZoneInfo("UTC"))
berlin_time = FIRST_GAME_KICKOFF.astimezone(ZoneInfo("Europe/Berlin"))
leagues = load_leagues()
managers = load_managers()

leagues = leagues.merge(
    managers,
    left_on=["league_id", "league_champion_rid"],
    right_on=["league_id", "roster_id"],
    how="left"
).rename(columns={"display_name": "champion"})

players_df = load_players(list(DIV_ROUND_PRICES.keys()), DIV_ROUND_PRICES)
players_df = players_df.sort_values(by=["position", "price"], ascending=[True, False])

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
- **Wildcard:** Die Wildcard-Runde kann bis zum {berlin_time.strftime("%d.%m.%Y um %H:%M Uhr")} getippt werden.
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
| Interceptions                 | pro Interception                  | -2              |
| Fumble Lost                  | pro Fumble Lost                        | -2              |</center>
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
st.header("Wildcard Round")

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
lineup_form = st.container()
with lineup_form:
    stats = load_weekly_player_stats(POST_WEEK, DIV_ROUND_PRICES)
    players_df["ppr_points"] = players_df["player_id"].map(stats).fillna(0)
    if datetime.now(timezone.utc) >= FIRST_GAME_KICKOFF:
        st.error(f"⏰ Die Eingabe für die {ROUND_NAME} ist nicht mehr möglich. Das erste Spiel hat bereits begonnen.")
        points_chart = st.container()
    else:
        st.markdown("---")
        left, right = st.columns(2)
        with left:
            qb = build_player_select("Quarterback", players_df, "QB", "qb")
            wr = build_player_select("Wide Receiver", players_df, "WR", "wr")
        with right:
            rb = build_player_select("Running Back", players_df, "RB", "rb")
            te = build_player_select("Tight End", players_df, "TE", "te")

        prices = players_df.set_index("player_id")["price"].to_dict()
        total_price = prices[qb] + prices[wr] + prices[rb] + prices[te]
        
        st.metric(label="Budget Auswahl",value=f"{total_price} $", delta=f"{total_price - BUDGET_LIMIT} $", border=True,delta_color="inverse")

        if total_price > BUDGET_LIMIT:
            st.warning("⚠️ Budget überschritten")

        sleeper_username = st.text_input("Sleeper-Benutzername")
        sleeper_user_id = validate_sleeper_user(sleeper_username)

        if st.button("Lineup absenden"):
            now_utc = datetime.now(timezone.utc)

            if now_utc >= FIRST_GAME_KICKOFF:
                st.error("⏰ Die Eingabe ist nicht mehr möglich. Das erste Spiel hat bereits begonnen.")
                st.stop()

            if not sleeper_user_id:
                st.error("Sleeper-Benutzername existiert nicht.")
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
                "sleeper_user_id": sleeper_user_id,
                "qb_id": qb,
                "wr_id": wr,
                "rb_id": rb,
                "te_id": te,
                "total_price": total_price,
                "round": ROUND_NAME,
                "week": POST_WEEK,
                "submission_time": datetime.now().isoformat()
            }

            res = supabase.table("lineups").insert(lineup).execute()
            if res.data:
                st.success("✅ Lineup erfolgreich gespeichert!")
            else:
                st.error("❌ Fehler beim Speichern.")

st.markdown("---")
st.header("Ranglisten")
players_df["ppr_points"] = players_df["player_id"].map(stats).fillna(0)

lineup_data = load_latest_lineups()
lineup_data = lineup_data[lineup_data["round"] == ROUND_NAME].copy()
if datetime.now(timezone.utc) < FIRST_GAME_KICKOFF:
    lineup_data = lineup_data[lineup_data["submission_time"] <= FIRST_GAME_KICKOFF.isoformat()]

lineup_data = lineup_data.merge(
    players_df[["player_id", "name", "ppr_points"]],
    left_on="qb_id",
    right_on="player_id",
    how="left"
).rename(columns={"name": "QB", "ppr_points": "QB pts"}).drop(columns=["player_id"])
lineup_data = lineup_data.merge(
    players_df[["player_id", "name", "ppr_points"]],
    left_on="wr_id",
    right_on="player_id",
    how="left"
).rename(columns={"name": "WR", "ppr_points": "WR pts"}).drop(columns=["player_id"])
lineup_data = lineup_data.merge(
    players_df[["player_id", "name", "ppr_points"]],
    left_on="rb_id",
    right_on="player_id",
    how="left"
).rename(columns={"name": "RB", "ppr_points": "RB pts"}).drop(columns=["player_id"])
lineup_data = lineup_data.merge(
    players_df[["player_id", "name", "ppr_points"]],
    left_on="te_id",
    right_on="player_id",
    how="left"
).rename(columns={"name": "TE", "ppr_points": "TE pts"}).drop(columns=["player_id"])
lineup_data["total_points"] = (
    lineup_data["QB pts"].fillna(0) +
    lineup_data["WR pts"].fillna(0) +
    lineup_data["RB pts"].fillna(0) +
    lineup_data["TE pts"].fillna(0)
)   
lineup_data = lineup_data.sort_values(
    by=["total_points", "submission_time"],
    ascending=[False, True]
).reset_index(drop=True)
lineup_data.index += 1
lineup_data["To 1st"] = lineup_data["total_points"].max() - lineup_data["total_points"]
if datetime.now(timezone.utc) < FIRST_GAME_KICKOFF:
    lineup_data[["QB","WR","RB","TE"]] = "-"
champion_set = set(leagues["champion"].str.lower())

coc_data = lineup_data[
    lineup_data["sleeper_username"].str.lower().isin(champion_set)
].reset_index(drop=True)

coc_data.index += 1
n_participants = len(coc_data)
st.markdown("#### 👑 :yellow[Champ of Champs Rangliste]")
st.write(f":blue[Aktuell nehmen {n_participants} von {n_winner} Champions aus {n_leagues} Ligen am Tippspiel teil.]")
st.dataframe(coc_data[["total_points","sleeper_username", "To 1st", "QB", "QB pts","WR","WR pts",
                "RB","RB pts","TE","TE pts"]],
                column_config={
                "total_points": "Punkte",
                "sleeper_username": "Sleeper"
                })
st.markdown("#### 🏅 :red[Offene Runde]")
st.write(f":blue[Insgesamt wurde{'' if len(lineup_data) == 1 else 'n'} {len(lineup_data)} Lineup{'' if len(lineup_data) == 1 else 's'} eingereicht.]")
st.dataframe(lineup_data[["total_points","sleeper_username", "To 1st", "QB", "QB pts","WR","WR pts",
                "RB","RB pts","TE","TE pts"]],
                column_config={
                "total_points": "Punkte",
                "sleeper_username": "Sleeper"
                })

# player_chart = st.expander("Spielerpunkte Übersicht")
rows = []

for position in ["QB", "WR", "RB", "TE"]:
    row = {"Position": position}

    for price in [5, 3, 1, 0]:
        pts = players_df[
            (players_df["position"] == position) &
            (players_df["price"] == price)
        ]

        if not pts.empty:
            top = pts.loc[pts["ppr_points"].idxmax()]
            row[f"${price}"] = (
                f"<div style='text-align:center'>"
                f"<strong>{top['name']}</strong><br>"
                f"{pts['ppr_points'].sum():.2f}"
                f"</div>"
            )
        else:
            row[f"${price}"] = "–"

    rows.append(row)

df = pd.DataFrame(rows)
html = df.to_html(
    escape=False,
    index=False
)

html = html.replace(
    "<table",
    "<table style='margin-left:auto;margin-right:auto;text-align:center'"
)
if datetime.now(timezone.utc) >= FIRST_GAME_KICKOFF:
    points_chart.markdown(html, unsafe_allow_html=True)

st.markdown("---")
st.write("© 2026 Stoned Lack Army")