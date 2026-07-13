from supabase import create_client, Client
import requests
import os

# Supabase Credentials aus Environment Variables
url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# True = Initialimport (alle Wochen 1-18)
# False = Nur aktuelle NFL-Woche
INITIAL_IMPORT = True

# Aktuelle NFL-Woche abrufen
try:
    state_resp = requests.get("https://api.sleeper.app/v1/state/nfl")
    state_resp.raise_for_status()
    current_week = state_resp.json().get("week")

    if not current_week:
        raise ValueError("Woche konnte aus dem State-Response nicht gelesen werden.")

    print(f"Aktuelle NFL-Woche erkannt: Woche {current_week}")
except Exception as e:
    print(f"❌ Fehler beim Abrufen der aktuellen Woche: {e}")
    current_week = 1
    print("⚠️ Fallback auf Woche 1.")

# Zu verarbeitende Wochen festlegen
weeks = range(1, 19) if INITIAL_IMPORT else [current_week]

# Alle league_ids aus der leagues-Tabelle holen
leagues_response = supabase.table("leagues").select("league_id").execute()
league_ids = [l["league_id"] for l in leagues_response.data]

SLEEPER_URL_TEMPLATE = "https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
BATCH_SIZE = 500

for league_id in league_ids:
    for week in weeks:

        url = SLEEPER_URL_TEMPLATE.format(
            league_id=league_id,
            week=week
        )

        resp = requests.get(url)

        if resp.status_code != 200:
            print(f"❌ Fehler beim Abrufen Liga {league_id} Woche {week}: {resp.status_code}")
            continue

        matchups = resp.json()

        # Leere Wochen überspringen
        if not matchups:
            print(f"ℹ️ Keine Matchups für Liga {league_id} Woche {week}.")
            continue

        batch = []

        for idx, matchup in enumerate(matchups, start=1):
            batch.append({
                "league_id": league_id,
                "matchup_id": matchup.get("matchup_id"),
                "roster_id": str(matchup["roster_id"]),
                "points": matchup.get("points", 0),
                "json_data": matchup,
                "week": week
            })

            if len(batch) == BATCH_SIZE or idx == len(matchups):
                try:
                    supabase.table("matchup_week_stats").upsert(batch).execute()
                    print(
                        f"✅ Batch von {len(batch)} Matchups "
                        f"Liga {league_id} Woche {week} gespeichert."
                    )
                except Exception as e:
                    print(
                        f"❌ Fehler beim Speichern "
                        f"Liga {league_id} Woche {week}: {e}"
                    )

                batch = []
