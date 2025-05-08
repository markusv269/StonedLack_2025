import streamlit as st
import requests
from typing import Union
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo

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

def get_draft_status(draft_data):
    if draft_data["status"] == "complete":
        st.success("Draft abgeschlossen")
    elif draft_data["status"] == "pre_draft":   
        st.error("Draft noch nicht gestartet")
    elif draft_data["status"] == "drafting":   
        st.warning("Draft läuft")
    elif draft_data["status"] == "paused":
        st.warning(f"Draft pausiert (bis {int(draft_data['settings']['autopause_end_time']/60 +2)} Uhr)")
    else:
        st.warning(draft_data["status"])

def get_draft_time(draft_time):
    draft_time /= 1000  # Millisekunden in Sekunden
    draft_time_utc = datetime.fromtimestamp(draft_time, tz=timezone.utc)  # UTC-Zeit
    draft_time_mesz = draft_time_utc.astimezone(ZoneInfo("Europe/Berlin"))  # In MESZ umwandeln
    draft_time_show = draft_time_mesz.strftime("%d.%m.%Y %H:%M")
    return draft_time_show

def get_draft_type(draft_type):
    if draft_type == 1:
        draft_typ = "Rookie Draft"
    elif draft_type == 2:
        draft_typ = "Veteran Draft"
    else:
        draft_typ = "Draft"
    return draft_typ