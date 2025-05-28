import streamlit as st
import requests
from pyairtable import Table
from pyairtable.formulas import match
from collections import defaultdict
import math
import pandas as pd

# Airtable-Zugangsdaten
AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
BASE_ID = st.secrets["airtable"]["base_id"]
TABLE_NAME = "WaitingRoom"

# UI-Text
st.write("# Dynasty Waiting Room")
st.write("Bock auf eine StonedLack Dynasty-Liga? Hier kannst du dich eintragen.")
st.write("Die Liga wird erst eröffnet, wenn genug Leute zusammenkommen. Also sag deinen Freunden Bescheid!")

# Eingaben
league_options = st.multiselect(
    "Welchen Ligentyp möchtest du spielen?",
    options=["1QB Dynasty", "IDP", "IDP only", "Best Ball", "Best Ball IDP"],
    placeholder="Wähle mindestens eine Option"
)
sleeper_name = st.text_input("Trage deinen sleeper-Namen ein")

# Funktion zum Speichern
def save_to_airtable(sleeper, options):
    table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
    for option in options:
        index_value = f"{sleeper}-{option}"
        existing = table.first(formula=match({"index": index_value}))
        if existing:
            st.warning(f"Du bist bereits im Warteraum für {option} registriert.")
        else:
            table.create({
                "index": index_value,
                "sleeper": sleeper,
                "options": option
            })
            st.success(f"Du bist jetzt im Warteraum für {option} registriert.")

# Verarbeitung der Eingaben
if sleeper_name:
    user_url = f"https://sleeper.app/v1/user/{sleeper_name}"
    response = requests.get(user_url)
    
    if response.json() != None:
        user_data = response.json()
        user_id = user_data.get("user_id")
        st.success(f"✅ User ID: {user_id} gefunden.")

        if league_options:
            # Nur wenn alles erfüllt ist, zeige den Button
            if st.button("Beitreten"):
                save_to_airtable(sleeper_name, league_options)
        else:
            st.warning("❗ Bitte wähle mindestens einen Ligatyp aus.")
    else:
        st.error("❌ User nicht gefunden. Bitte überprüfe deinen Namen.")

def display_waiting_lists():
    table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
    records = table.all()

    # Gruppieren nach Ligentyp
    waitlist = defaultdict(list)
    for record in records:
        fields = record.get("fields", {})
        league_type = fields.get("options")
        sleeper = fields.get("sleeper")
        if league_type and sleeper:
            waitlist[league_type].append(sleeper)

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
                df = pd.DataFrame(sorted(waitlist[league]), columns=[f"{league} ({len(waitlist[league])})"])
                st.dataframe(df,hide_index=True)
# Am Ende der App anzeigen
display_waiting_lists()