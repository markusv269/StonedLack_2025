import streamlit as st
import pandas as pd
import requests
import json
from pyairtable import Table
from collections import defaultdict

# Basis-URL für Sleeper API
SLEEPER_API_BASE = "https://api.sleeper.app/v1/league/"

# Airtable Konfiguration
AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
BASE_ID = st.secrets["airtable"]["base_id"]
TABLE_NAME = "Ligen"

# Funktion zum Laden der Daten aus Airtable
@st.cache_data(ttl=300)
def load_from_airtable():
    table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
    records = table.all()
    if records:
        return pd.DataFrame([rec["fields"] for rec in records])
    return pd.DataFrame(columns=["Autor", "League-ID", "Liga-Name"])  # Fallback bei leeren Tabellen

# Funktion zum Speichern in Airtable
def save_to_airtable(author, league_id, league_name):
    table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
    try:
        table.create({"Autor": author, "League-ID": league_id, "Liga-Name": league_name})
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern in Airtable: {e}")
        return False

# Funktion zur Überprüfung der league_id
def check_league_id(league_id):
    try:
        response = requests.get(f"{SLEEPER_API_BASE}{league_id}")
        if response.status_code == 200:
            league_data = response.json()
            return True, league_data.get("name", "Unbekannte Liga")
        else:
            return False, None
    except requests.RequestException as e:
        st.error(f"Fehler bei der Verbindung zur Sleeper API: {e}")
        return False, None

def main():
    st.title("Alte Redraftligen")

    st.write("""
        Jedes Jahr werden Redraftligen, welche über StonedLack gegründet wurden, weiter gespielt.
        Die Ligen nachzuvollziehen, ist verständlicherweise schwierig. 
        Solltet ihr noch Ligen haben, die aus den StonedLack Redrafts entstanden sind und diese hier berücksichtigt werden sollen, 
        dann füllt einfach das Formular unten aus und lasst mich von Eurer Liga wissen.
    """)

    st.write("### Melde Deine SLR-Liga")

    df = load_from_airtable()

    with st.form("league_form"):
        author = st.text_input("Dein Name auf Sleeper/Discord").strip() or "Unbekannt"
        league_id = st.text_input("League-ID deiner Liga").strip()

        submitted = st.form_submit_button("Absenden")

        if submitted:
            if not league_id:
                st.error("Bitte eine League-ID eingeben.")
            elif "League-ID" in df.columns and league_id in df["League-ID"].astype(str).str.strip().values:
                st.warning("Die Liga wurde bereits eingetragen.")
            else:
                checked, league_name = check_league_id(league_id)
                if not checked:
                    st.error("League-ID existiert nicht, bitte erneut eingeben.")
                else:
                    if save_to_airtable(author, league_id, league_name):
                        st.success(f"**{league_name}** erfolgreich eingetragen!")
                        df = load_from_airtable()
                    else:
                        st.error("Fehler beim Speichern in Airtable.")

    # Gespeicherte Ligen anzeigen
    if not df.empty:
        st.subheader("Gespeicherte Ligen")
        st.dataframe(df[['Liga-Name', 'Autor']], hide_index=True)
    else:
        st.info("Noch keine Ligen gespeichert.")

    # # Optional: Debug-Ansicht
    # if st.checkbox("Rohdaten anzeigen"):
    #     st.write(df)

main()
