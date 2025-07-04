import streamlit as st
import requests
from pyairtable import Table, Api, Base
from pyairtable.formulas import match
import math
import pandas as pd
from airtable import waitinglist_airtable

# Airtable-Zugangsdaten
AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
BASE_ID = st.secrets["airtable"]["base_id"]
TABLE_NAME = "WaitingRoom"
api = Api(AIRTABLE_API_KEY)
base = Base(api, BASE_ID)

# UI-Text
st.write("# Dynasty Waiting Room")
st.write('''
Bock auf eine StonedLack Dynasty-Liga? Hier kannst du dich eintragen.  

---
                
**Wie funktionierts?!**  
Trage deinen sleeper-Namen und deinen Discord-Namen (auf dem StonedLack-Server) ein und wähle die Ligentypen, die du spielen möchtest.
Die Wartelisten je Liga werden automatisch aktualisiert. Sobald genug Leute für eine Liga bereitstehen, wird sie eröffnet und du bekommst eine Einladung über die sleeper-App.
         
---

**Bitte beachtet!**  
Die Liga wird erst eröffnet, wenn genug Leute zusammenkommen. Also bleibt auf dem Laufenden und informiert Euch regelmäßig auf dem StonedLack-Discord-Server!   
Es dürfen nur aktive Hörer des StonedLack-Podcasts teilnehmen.

--- 
         
''')

st.write("**Welchen Ligentyp möchtest du spielen (wähle mindestens einen)?**")
dynasty_checkbox = st.checkbox("Dynasty")
idp_checkbox = st.checkbox("Dynasty mit IDP")
best_ball_checkbox = st.checkbox("Best Ball Dynasty")

st.write("")
league_options = []
if dynasty_checkbox:
    league_options.append("Dynasty")
if idp_checkbox:
    league_options.append("Dynasty mit IDP")
if best_ball_checkbox:
    league_options.append("Best Ball Dynasty")


sleeper_name = st.text_input("**Trage deinen sleeper-Namen ein**", placeholder="Sleepername")
discord_name = st.text_input("**Trage deinen Discord-Namen ein**", placeholder="Discordname")

# Initialstatus
user_valid = False
user_id = None

# Verarbeitung der Eingaben
if sleeper_name:
    user_url = f"https://sleeper.app/v1/user/{sleeper_name}"
    response = requests.get(user_url)
    
    if response.json() != None:
        user_data = response.json()
        user_id = user_data.get("user_id")
        user_valid = True
        st.success(f"✅ User ID: {user_id} gefunden.")
    else:
        st.error("❌ User nicht gefunden. Bitte überprüfe deinen Namen. Noch nicht bei sleeper registriert? Dann [hier registrieren](https://sleeper.app).")

form_ready = user_valid and bool(discord_name.strip()) and len(league_options) > 0
button = st.button("Setz' mich auf die Warteliste(n)", disabled=not form_ready, key="join_button")
if button:
    waitinglist_airtable(sleeper_name, discord_name, league_options)

def display_waiting_lists():
    table = base.table(TABLE_NAME)
    records = table.all()

    # Gruppieren nach Ligentyp
    waitlist = {}
    for record in records:
        fields = record.get("fields", {})
        league_type = fields.get("option")
        sleeper = fields.get("sleeper")
        discord = fields.get("discord")
        if league_type and sleeper:
            waitlist.setdefault(league_type, []).append({
                "Sleeper": sleeper,
                "Discord": discord or "—"
            })

    if not waitlist:
        st.info("Noch keine Einträge in den Wartelisten.")
        return

    st.markdown("---")
    st.header("📋 Aktuelle Wartelisten")

    league_types = sorted(waitlist.keys())
    num_leagues = len(league_types)

    # Dynamische Spaltenanzahl: max. 4 Spalten pro Reihe
    max_cols = 4
    cols_per_row = min(max_cols, num_leagues)
    rows = math.ceil(num_leagues / cols_per_row)

    for r in range(rows):
        cols = st.columns(cols_per_row)
        for c in range(cols_per_row):
            idx = r * cols_per_row + c
            if idx >= num_leagues:
                break
            league = league_types[idx]
            with cols[c]:
                st.write(f"**{league} ({len(waitlist[league])}/12)**")
                df = pd.DataFrame(waitlist[league])
                st.dataframe(df, hide_index=True, use_container_width=True)

# Am Ende der App anzeigen
display_waiting_lists()