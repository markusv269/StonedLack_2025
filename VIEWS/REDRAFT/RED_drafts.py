from config import REDLEAGUES_2025
from utils import display_draft

red_leagues = list(reversed(REDLEAGUES_2025.keys()))
for league_id in red_leagues[:-4]:  # Exclude last 3 leagues
    display_draft(league_id)