from sleeper import SleeperLeague, SleeperDraft
from config import DYNLEAGUES

for league_id in DYNLEAGUES:
    league_data = SleeperLeague(league_id)
    print(f"{league_data.get_league_info().get('name')}")

    for draft in league_data.get_draft_ids():
        draft_data = SleeperDraft(draft)
        draft_info = draft_data.get_draft_info()
        print(f"Draft ID: {draft_info.get('draft_id')}")
        print(f"Draft-Order: {draft_info.get('draft_order')}")
        print(f"Draft-Settings: {draft_info.get('settings')}")
        print()

# user_id = "miami84"
# user_data = SleeperUser(user_id)
# user_leagues = user_data.get_all_leagues(season=2025)
# for league in user_leagues:
#     print(f"\"{league['league_id']}\", # {league['name']}")