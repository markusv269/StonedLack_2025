import requests
import os
from sleeper_wrapper import League, Drafts
import json
from config import REDLEAGUES, DYNLEAGUES


league_ids = REDLEAGUES + DYNLEAGUES

drafts_dir = "DATA/_{}/DRAFT_COMP"
# matchup_dir = "DATA/_{}/MATCHUPS/{}"
picks_dir = "DATA/_{}/PICKS"
# roster_dir = "DATA/_{}/ROSTERS/{}"

# get NFL-State
state_url = "https://api.sleeper.app/v1/state/nfl"
state_data = requests.get(state_url).json()

nfl_week = state_data.get("week")
nfl_season_type = state_data.get("season_type")
nfl_season = state_data.get("season")

# Verzeichnisse erstellen, falls sie nicht existieren
# os.makedirs(matchup_dir.format(nfl_season, nfl_week), exist_ok=True)
# os.makedirs(roster_dir.format(nfl_season, nfl_week), exist_ok=True)

for league_id in league_ids:
    league = League(league_id)
    drafts = league.get_all_drafts()
    
    
    if drafts:
        draft_id = drafts[0]["draft_id"]
        draft = Drafts(draft_id)
        draft_data = draft.get_specific_draft()
        status = draft_data["status"]
        draft_season = draft_data["season"]
        if draft_season == nfl_season:
            # JSON-Dateien speichern
            os.makedirs(drafts_dir.format(nfl_season), exist_ok=True)
            with open(f"{drafts_dir.format(nfl_season)}/{draft_id}.json", "w", encoding="utf-8") as draft_file:
                json.dump(draft_data, draft_file, indent=4)

            all_picks = draft.get_all_picks()
            os.makedirs(picks_dir.format(nfl_season), exist_ok=True)
            with open(f"{picks_dir.format(nfl_season)}/{draft_id}.json", "w", encoding="utf-8") as pick_file:
                json.dump(all_picks, pick_file, indent=4)
        
