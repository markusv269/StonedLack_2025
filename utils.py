import streamlit as st
import pandas as pd
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
from sleeper_wrapper import League, Drafts, User  # Falls du diese API nutzt
import os
import json
import requests
from sleeper import SleeperLeague, SleeperUser, SleeperDraft


drafts_dir = "drafts"
picks_dir = "picks"

def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return None

def metric_box(label, value):
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="label">{label}</div>  
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
)

@st.cache_data(ttl=900)
def display_draft(league_id):
    league = SleeperLeague(league_id)
    league_data = league.get_league_info()
    st.write(f"#### {league_data['name']}")
    draft_ids = league.get_draft_ids()
    for draft_id in draft_ids:
        draft = SleeperDraft(draft_id)
        draft_data = draft.get_draft_info()
        picks = draft.get_all_picks()
        
        draft_order = draft_data.get("draft_order", {})
        draft_time = draft_data.get("start_time", None)
        draft_type = draft_data["settings"].get("player_type")
        draft_mode = draft_data["type"]

        if draft_type == 1:
            draft_typ = "Rookie Draft"
        elif draft_type == 2:
            draft_typ = "Veteran Draft"
        else:
            draft_typ = "Draft"

        if draft_time:
            draft_time /= 1000  # Millisekunden in Sekunden
            draft_time_utc = datetime.fromtimestamp(draft_time, tz=timezone.utc)  # UTC-Zeit
            draft_time_mesz = draft_time_utc.astimezone(ZoneInfo("Europe/Berlin"))  # In MESZ umwandeln
            draft_time_show = draft_time_mesz.strftime("%d.%m.%Y %H:%M")
        else:
            draft_time_show = "TBD"

        latest_pick = picks[-1] if picks else None
        
        if latest_pick:
            pick_data = [
                latest_pick["metadata"].get('first_name', 'Unknown'),
                latest_pick["metadata"].get('last_name', 'Unknown'),
                latest_pick["metadata"].get('position', 'Unknown'),
                latest_pick["metadata"].get('team', 'Unknown'),
                latest_pick["round"],
                latest_pick["draft_slot"],
                latest_pick["picked_by"]
            ]
        else:
            pick_data = None

        st.write(f"**{draft_typ} {draft_data['season']}**")

        col1, col2, col3, col4 = st.columns([2,2,2,3])
        with col1:
            metric_box("Start", draft_time_show)
        with col2:
            if draft_data["status"] == "complete":
                st.success("Draft abgeschlossen")
            elif draft_data["status"] == "pre_draft":   
                st.error("Draft noch nicht gestartet")
            elif draft_data["status"] == "drafting":   
                st.warning("Draft läuft")
            else:
                st.warning(draft_data["status"])
        with col3:
            metric_box("Draftmodus", draft_mode)   
        with col4: 
            metric_box("Draft-URL", f'https://sleeper.com/draft/nfl/{draft_id}')
        # with st.expander("Draftdetails anzeigen"):
        #     col5, col6 = st.columns([1, 4])
        #     with col5:
        #         st.write("Latest Pick")
        #     with col6:
        #         if pick_data:
        #             user = SleeperUser(pick_data[6])
        #             user_name = user.get_user_info()['display_name']
        #             st.write(f"**{user_name}:** {pick_data[0]} {pick_data[1]} ({pick_data[2]}, {pick_data[3]}), Pick {pick_data[4]}.{pick_data[5]} ")
        #         else:
        #             st.write("--")

            # # Draftorder in einer Tabelle anzeigen
            # if draft_order:
            #     draft_list = []
            #     for user_id, draft_pos in draft_order.items():
            #         user = SleeperUser(user_id)
            #         user_name = user.get_user_info()['display_name']
            #         draft_list.append({"Draft Position": draft_pos, "Manager": user_name})
            #     col9, col10 = st.columns([1,4])
            #     with col9:
            #         st.write("Draftorder")
            #     with col10:
            #         # Sortieren nach Draft-Position
            #         draft_df = pd.DataFrame(draft_list).sort_values(by="Draft Position")
            #         st.table(draft_df.set_index("Draft Position"))
            # else:
            #     st.write("No draft order available.")

BASE_ID = st.secrets["airtable"]["base_id"]
AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
TABLE_NAME = st.secrets["airtable"]["table_name"]

def save_to_airtable(**kwargs):
    if not BASE_ID or not AIRTABLE_API_KEY or not TABLE_NAME:
        print("❌ Fehler: BASE_ID, AIRTABLE_API_KEY oder TABLE_NAME fehlt.")
        return False

    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Konvertiere datetime/date-Werte zu Strings
    fields = {}
    for key, value in kwargs.items():
        if isinstance(value, (datetime, date)):
            fields[key] = value.strftime("%Y-%m-%d")
        elif isinstance(value, list):  
            fields[key] = ", ".join(value)  # Listen als kommagetrennten String speichern
        # elif key == "Commish":  
        #     fields[key] = bool(value)  # ✅ Boolean-Wert für Airtable-Kontrollkästchen
        else:
            fields[key] = value

    data = {"records": [{"fields": fields}]}

    try:
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()  # JSON-Response für Debugging

        if response.status_code in [200, 201]:
            print("✅ Erfolgreich gespeichert in Airtable!")
            return True
        else:
            print(f"❌ Fehler: {response.status_code}")
            print("🔍 Airtable-Fehlermeldung:", json.dumps(response_json, indent=2))
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Anfrage fehlgeschlagen: {e}")
        return False