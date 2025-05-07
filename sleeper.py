import requests
from typing import Union

class SleeperLeague:
    def __init__(self, league_id):
        self._league_id = league_id
        self._base_url = "https://api.sleeper.app/v1/league"

    def get_league_info(self):
        league_info = requests.get("{}/{}".format(self._base_url, self._league_id)).json()
        return league_info

    def get_rosters(self):
        rosters = requests.get("{}/{}/{}".format(self._base_url, self._league_id, "rosters")).json()
        return rosters
    
    def get_matchups(self, week=None):
        if week:
            url = f"{self._base_url}/{self._league_id}/matchups/{week}"
            matchups = requests.get(url).json()
            return matchups
        else:
            return None
    
    def get_draft_ids(self):
        draft_ids = []
        drafts = requests.get("{}/{}/{}".format(self._base_url, self._league_id, "drafts")).json()
        for draft in drafts:
            draft_ids.append(draft["draft_id"])
        return draft_ids

class SleeperDraft:
    def __init__(self, draft_id):
        self._draft_id = draft_id
        self._base_url = "https://api.sleeper.app/v1/draft"

    def get_draft_info(self):
        draft_info = requests.get("{}/{}".format(self._base_url, self._draft_id)).json()
        return draft_info
    
    def get_all_picks(self):
        picks = requests.get("{}/{}/{}".format(self._base_url, self._draft_id, "picks")).json()
        return picks

class SleeperUser:
    def __init__(self, initial_user_input: Union[str, int]):
        self._base_url = "https://api.sleeper.app/v1/user"
        self._user = requests.get("{}/{}".format(self._base_url, initial_user_input)).json()
        self._username = self._user["username"]
        self._user_id = self._user["user_id"]
    
    def get_user_info(self):
        user_info = requests.get("{}/{}".format(self._base_url, self._user_id)).json()
        return user_info

    def get_all_leagues(self, sport="nfl", season=None):
        user_leagues = requests.get("{}/{}/{}/{}/{}".format(self._base_url, self._user_id, "leagues", sport, season)).json()
        return user_leagues