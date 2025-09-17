import requests
from typing import List, Dict, Optional

# --- Sleeper API Endpoints ---
SLEEPER_STATE_URL = "https://api.sleeper.app/v1/state/nfl"
SLEEPER_LEAGUE_URL = "https://api.sleeper.app/v1/league/{}"
SLEEPER_ROSTER_URL = "https://api.sleeper.app/v1/league/{}/rosters"
SLEEPER_MATCHUPS_URL = "https://api.sleeper.app/v1/league/{}/matchups/{}"
SLEEPER_DRAFTS_URL = "https://api.sleeper.app/v1/league/{}/drafts"

BATCH_SIZE = 500


# --- NFL STATE ---
def get_current_nfl_week(fallback: int = 1) -> int:
    """Aktuelle NFL Woche abrufen, Fallback bei Fehler."""
    try:
        resp = requests.get(SLEEPER_STATE_URL)
        resp.raise_for_status()
        week = resp.json().get("week")
        if not week:
            raise ValueError("Week not found in response")
        return week
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der NFL-Woche: {e}")
        print(f"⚠️ Fallback auf Woche {fallback}")
        return fallback


# --- LEAGUES ---
def fetch_league(league_id: str) -> Dict:
    """Einzelne Liga abrufen"""
    resp = requests.get(SLEEPER_LEAGUE_URL.format(league_id))
    resp.raise_for_status()
    return resp.json()


# --- ROSTERS ---
def fetch_league_rosters(league_id: str) -> List[Dict]:
    """Alle Rosters einer Liga abrufen"""
    resp = requests.get(SLEEPER_ROSTER_URL.format(league_id))
    resp.raise_for_status()
    return resp.json()


def transform_roster_data(matchups: List[Dict], league_id: str, week: int) -> List[Dict]:
    """Rosters für Supabase transformieren"""
    batch = []
    for m in matchups:
        batch.append({
            "league_id": league_id,
            "roster_id": str(m["roster_id"]),
            "fpts_for": round(m.get("settings", {}).get("fpts", 0) +
                              m.get("settings", {}).get("fpts_decimal", 0)/100, 2),
            "fpts_against": round(m.get("settings", {}).get("fpts_against", 0) +
                                  m.get("settings", {}).get("fpts_against_decimal", 0)/100, 2),
            "ppts": round(m.get("settings", {}).get("ppts", 0) +
                          m.get("settings", {}).get("ppts_decimal", 0)/100, 2),
            "week": week,
            "wins": m.get("settings", {}).get("wins", 0),
            "losses": m.get("settings", {}).get("losses", 0),
            "ties": m.get("settings", {}).get("ties", 0),
            "json_data": m
        })
    return batch


# --- MATCHUPS ---
def fetch_league_matchups(league_id: str, week: int) -> List[Dict]:
    """Alle Matchups einer Liga abrufen"""
    resp = requests.get(SLEEPER_MATCHUPS_URL.format(league_id, week))
    resp.raise_for_status()
    return resp.json()


# --- DRAFTS ---
def fetch_league_drafts(league_id: str) -> List[Dict]:
    """Drafts einer Liga abrufen"""
    resp = requests.get(SLEEPER_DRAFTS_URL.format(league_id))
    resp.raise_for_status()
    return resp.json()


# --- Hilfsfunktion: Batch-Processing für Supabase ---
def batch_upsert(supabase_client, table: str, records: List[Dict], batch_size: int = BATCH_SIZE):
    """
    Daten in Batches in Supabase upserten
    """
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            supabase_client.table(table).upsert(batch).execute()
            print(f"✅ Batch von {len(batch)} Datensätzen in Tabelle {table} gespeichert.")
        except Exception as e:
            print(f"❌ Fehler beim Speichern in Tabelle {table}: {e}")
