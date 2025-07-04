# from sleeper_wrapper import League, Drafts, User
# from config import DYNLEAGUES

# stoned_lack_roster = {}

# for league_id in DYNLEAGUES:
#     league_data = League(league_id)

#     for roster in league_data.get_rosters():
#         if roster['owner_id'] not in stoned_lack_roster:
#             stoned_lack_roster[roster['owner_id']] = {
#                 "roster_id": roster['roster_id'],
#                 # "display_name": roster['display_name'],
#                 "count" : 1
#             }
#         else:
#             stoned_lack_roster[roster['owner_id']]['count'] += 1

# print("StonedLack Roster:")
# sort_roster = sorted(stoned_lack_roster.items(), key=lambda x: x[1]['count'], reverse=True)
# for owner_id, data in stoned_lack_roster.items():
#     user_name = User(owner_id).get_display_name()
#     print(f"{user_name}: {data['count']} Rosters")
        

# # user_id = "miami84"
# # user_data = SleeperUser(user_id)
# # user_leagues = user_data.get_all_leagues(season=2025)
# # for league in user_leagues:
# #     print(f"\"{league['league_id']}\", # {league['name']}")

