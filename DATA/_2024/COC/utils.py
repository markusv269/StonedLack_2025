import json
import pandas as pd

# Benutzerdefinierte Sortierreihenfolge für Positionen
POSITION_ORDER = ["QB", "RB", "WR", "TE"]

def load_json(file_path):
    """ Lädt JSON-Datei und gibt sie als Dictionary zurück. """
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Fehler beim Laden der Datei {file_path}: {e}")
        return {}

def add_price(player_id, round_player_data):
    """ Gibt den Preis des Spielers zurück, wenn vorhanden. """
    return next((p["price"] for p in round_player_data.values() if p["player_id"] == player_id), 0)

def calculate_fantasy_points(player, scoring_settings):
    """ Berechnet Fantasy-Punkte für einen Spieler. """
    return sum(player.get("stats", {}).get(key, 0) * multiplier for key, multiplier in scoring_settings.items())

def process_players(stats_data, round_player_data, scoring_settings):
    """ Verarbeitet die Spieler-Daten und berechnet Fantasy-Punkte. """
    valid_player_ids = {p["player_id"] for p in round_player_data.values()}
    
    data = [
        {
            "player_id": player["player_id"],
            "Spieler": f"{player['player'].get('first_name', '')} {player['player'].get('last_name', '')}".strip(),
            "Position": player["player"]["position"],
            "Gruppe": player["team"],
            "Preis": add_price(player["player_id"], round_player_data),
            "FFP": round(calculate_fantasy_points(player, scoring_settings), 2),
        }
        for player in stats_data if player["player_id"] in valid_player_ids
    ]

    df = pd.DataFrame(data)

    # Sortieren nach Position und Preis
    df["Position"] = pd.Categorical(df["Position"], categories=POSITION_ORDER, ordered=True)
    df = df.sort_values(by=["Position", "Preis"], ascending=[True, False])

    return df.set_index("player_id")
