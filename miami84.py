import requests
import numpy as np
from config import DYNLEAGUES_2024

# Beispiel: Liste mit mehreren Ligen
LEAGUE_IDS = DYNLEAGUES_2024

weeks = range(1, 4)  # Wochen 1–3

# Ergebnisse pro Liga speichern
league_results = {}

for league_id in LEAGUE_IDS:
    roster_ids_all = set()
    weekly_data = []

    # --- Daten holen ---
    for week in weeks:
        url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
        data = requests.get(url).json()

        week_points = {}
        for matchup in data:
            roster_id = matchup["roster_id"]
            points = matchup["points"]
            week_points[roster_id] = points
            roster_ids_all.add(roster_id)

        weekly_data.append(week_points)

    # --- Konsistente Team-Reihenfolge ---
    roster_ids_sorted = sorted(roster_ids_all)

    # --- Matrix: Wochen × Teams ---
    points_matrix = np.zeros((len(weeks), len(roster_ids_sorted)))

    for week_idx, week_points in enumerate(weekly_data):
        for col_idx, roster_id in enumerate(roster_ids_sorted):
            points_matrix[week_idx, col_idx] = week_points.get(roster_id, 0.0)

    # --- Statistiken ---
    total_points = np.sum(points_matrix, axis=0)
    avg_per_team = np.mean(points_matrix, axis=0)
    best_week_points = np.max(points_matrix, axis=0)

    best_team_idx = np.argmax(total_points)

    league_results[league_id] = {
        "roster_ids": roster_ids_sorted,
        "matrix": points_matrix,
        "total_points": total_points,
        "avg_points": avg_per_team,
        "best_week_points": best_week_points,
        "best_team_idx": best_team_idx
    }

# --- Ausgabe ---
for league_id, res in league_results.items():
    print(f"\n📊 Liga {league_id}")
    for rid, total, avg in zip(res["roster_ids"], res["total_points"], res["avg_points"]):
        print(f"Roster {rid}: Gesamt {total:.1f} | Schnitt {avg:.2f}")

    best_team_rid = res["roster_ids"][res["best_team_idx"]]
    print(f"🏆 Bestes Team: Roster {best_team_rid} "
          f"mit {res['total_points'][res['best_team_idx']]:.1f} Punkten")