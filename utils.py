import streamlit as st
from sleeper import SleeperLeague, SleeperDraft, get_draft_status, get_draft_time, get_draft_type
from styles import metric_box
import concurrent.futures

@st.cache_data(ttl=900)
def load_draft_infos_parallel(league_id):
    league = SleeperLeague(league_id)
    draft_ids = league.get_draft_ids()

    def fetch_draft(draft_id):
        draft = SleeperDraft(draft_id)
        return draft_id, draft.get_draft_info()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        draft_infos = list(executor.map(fetch_draft, draft_ids))

    return league.get_league_info(), draft_infos

def display_draft(league_id):
    league_data, draft_infos = load_draft_infos_parallel(league_id)
    st.write(f"#### {league_data['name']}")

    for draft_id, draft_data in draft_infos:
        draft = SleeperDraft(draft_id)
        draft_data = draft.get_draft_info()
        draft_time = draft_data.get("start_time", None)
        draft_type = draft_data["settings"].get("player_type")

        st.write(f"**{get_draft_type(draft_type)} {draft_data['season']}**")

        col1, col2, col3, col4 = st.columns([2,2,2,3])
        if draft_time:
            draft_time_show = get_draft_time(draft_time)
        else:
            draft_time_show = "TBD"
        with col1:
            metric_box("Start", draft_time_show)

        with col2:
            get_draft_status(draft_data)

        draft_mode = draft_data["type"]
        with col3:
            metric_box("Draftmodus", draft_mode) 

        with col4: 
            metric_box("Draft-ID/Link zu sleeper.com", f'<a href="https://sleeper.com/draft/nfl/{draft_id}" target="_blank">{draft_id}</a>')