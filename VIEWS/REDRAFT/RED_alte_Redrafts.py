import streamlit as st
import pandas as pd
import requests
import json

# Basis-URL für Sleeper API
SLEEPER_API_BASE = "https://api.sleeper.app/v1/league/"

# Airtable Konfiguration
AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
BASE_ID = st.secrets["airtable"]["base_id"]
TABLE_NAME = st.secrets["airtable"]["table_leagues"]

# Funktion zum Laden der Daten aus Airtable
def load_from_airtable():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        records = response.json().get("records", [])
        if records:
            return pd.DataFrame([rec["fields"] for rec in records])
    
    return pd.DataFrame(columns=["Autor", "League-ID", "Liga-Name"])  # Sicherstellen, dass die Spalten existieren

# Funktion zum Speichern in Airtable
def save_to_airtable(author, league_id, league_name):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "records": [
            {"fields": {"Autor": author, "League-ID": league_id, "Liga-Name": league_name}}
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.status_code == 200

# Funktion zur Überprüfung der league_id
def check_league_id(league_id):
    try:
        response = requests.get(f"{SLEEPER_API_BASE}{league_id}")
        if response.status_code == 200:
            league_data = response.json()
            return True, league_data.get("name", "Unbekannte Liga")
        else:
            return False, None
    except requests.RequestException:
        return False, None

def main():
    st.title("Alte Redraftligen")

    st.write(
        """
        Jedes Jahr werden Redraftligen, welche über StonedLack gegründet wurden, weiter gespielt.
        Die Ligen nachzuvollziehen, ist verständlicherweise schwierig. 
        Solltet ihr noch Ligen haben, die aus den StonedLack Redrafts entstanden sind und diese hier berücksichtigt werden sollen, 
        dann füllt einfach das Formular unten aus und lasst mich von Eurer Liga wissen.
        """
    )

    st.write("### Melde Deine SLR-Liga")

    df = load_from_airtable()  # Lade gespeicherte Ligen vorab

    with st.form("league_form"):
        author = st.text_input("Dein Name auf Sleeper/Discord")
        league_id = st.text_input("League-ID deiner Liga")

        submitted = st.form_submit_button("Absenden")

        if submitted:
            if not league_id:
                st.error("Bitte eine League-ID eingeben.")
            else:
                # Prüfen, ob die Spalte existiert, bevor darauf zugegriffen wird
                if "League-ID" in df.columns and league_id in df["League-ID"].astype(str).values:
                    st.warning("Die Liga wurde bereits eingetragen.")
                else:
                    checked, league_name = check_league_id(league_id)
                    if not checked:
                        st.error("League-ID existiert nicht, bitte erneut eingeben.")
                    else:
                        if save_to_airtable(author, league_id, league_name):
                            st.success(f"**{league_name}** erfolgreich eingetragen!")
                            df = load_from_airtable()  # Tabelle nach erfolgreichem Eintrag aktualisieren
                        else:
                            st.error("Fehler beim Speichern in Airtable.")

    # Gespeicherte Ligen anzeigen
    if not df.empty:
        st.subheader("Gespeicherte Ligen")
        st.dataframe(df[['Liga-Name', 'Autor']], hide_index=True)
    else:
        st.info("Noch keine Ligen gespeichert.")

main()
