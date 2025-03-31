import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, date

# Airtable Konfiguration
AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
BASE_ID = st.secrets["airtable"]["base_id"]
TABLE_NAME = st.secrets["airtable"]["table_name"]

# Funktion zum Speichern in Airtable
def save_to_airtable(option, option_wo, text, date_value=None):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Falls date ein datetime-Objekt ist, umwandeln in String
    if isinstance(date_value, (datetime, date)):
        date_value = date_value.strftime("%Y-%m-%d")

    data = {
        "records": [
            {"fields": {"Quelle": option, "Wo": option_wo, "Text": text, "Datum": date_value}}
             ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Debugging-Ausgabe
    if response.status_code != 200:
        print(f"Fehler: {response.status_code}")
        print(response.text)

    return response.status_code == 200

# Funktion zum Laden der Daten aus Airtable
def load_from_airtable():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        records = response.json().get("records", [])
        return pd.DataFrame([rec["fields"] for rec in records])
    return pd.DataFrame(columns=["Quelle", "Wo", "Aussage", "Datum"])

def main():
    st.title("Die StonedLack Hot Takes Sammlung")

    with st.form("quote_form"):
        option = st.radio("Wähle eine Option:", ["Stoni sagt", "Lack sagt"])
        option_wo = st.radio("Wo wurde der Hot Take gedroppt?", ["Montags-Podcast", "Start&Sit", "Discord", "Social Media", "Sonstiges"])
        date = st.date_input("Datum", format="DD.MM.YYYY")
        text = st.text_area("Gib deinen Text ein:")
        submitted = st.form_submit_button("Absenden")

        if submitted and text.strip():
            if save_to_airtable(option, option_wo, text, date):
                st.success(f"**{option}:** {text}")
            else:
                st.error("Fehler beim Speichern in Airtable!")

    df = load_from_airtable()
    # Gespeicherte Ligen anzeigen
    if not df.empty:
        st.subheader("Gespeicherte Hot Takes")
        st.dataframe(df)
    else:
        st.info("Noch keine Hot Takes gespeichert.")

main()