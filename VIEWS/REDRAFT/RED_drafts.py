from config import REDLEAGUES_2025
from utils import display_draft
from sleeper_wrapper import League

red_leagues = list(reversed(REDLEAGUES_2025.keys()))
drafting_leagues = []
for league_id in red_leagues:  # Last 3 leagues are drafting leagues
    league = League(league_id)
    data = league.get_league()
    if data['status'] != 'pre_draft':
        drafting_leagues.append(league_id)
for league_id in drafting_leagues:  # Exclude last 3 leagues
    display_draft(league_id)