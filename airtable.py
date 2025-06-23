import requests
import json
from datetime import datetime, date
import streamlit as st
# import pyairtable
from pyairtable import Table
from pyairtable.formulas import match
# Airtable Konfiguration


BASE_ID = st.secrets["airtable"]["base_id"]
AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
TABLE_NAME = "default"

def save_to_airtable(**kwargs):
    if not BASE_ID or not API_KEY or not TABLE_NAME:
        print("❌ Fehler: BASE_ID, API_KEY oder TABLE_NAME fehlt.")
        return False

    table = Table(API_KEY, BASE_ID, TABLE_NAME)

    # Datums- und Listenbehandlung
    fields = {}
    for key, value in kwargs.items():
        if isinstance(value, (datetime, date)):
            fields[key] = value.strftime("%Y-%m-%d")
        elif isinstance(value, list):
            fields[key] = ", ".join(str(v) for v in value)
        else:
            fields[key] = value

    try:
        table.create(fields)
        print("✅ Erfolgreich gespeichert in Airtable!")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Speichern in Airtable: {e}")
        return False

def waitinglist_airtable(sleeper, discord, options):
    table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
    for option in options:
        index_value = f"{sleeper.lower()}-{option}"
        existing = table.first(formula=match({"index": index_value}))
        if existing:
            st.warning(f"Du bist bereits im Warteraum für {option} registriert.")
        else:
            table.create({
                "index": index_value,
                "sleeper": sleeper,
                "discord": discord,
                "option": option
            })
            st.success(f"Du bist jetzt im Warteraum für {option} registriert.")
