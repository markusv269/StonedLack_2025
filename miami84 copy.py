from config import REDLEAGUES_2025
from sleeper_wrapper import League, User

for league_id in list(REDLEAGUES_2025.keys()):
    league = League(league_id)
    rosters = league.get_rosters()
    for roster in rosters:
        owner_id = roster.get("owner_id")
        if not owner_id:
            print(f"Fehlender Manager in {league.get_league_name()}.")
            continue