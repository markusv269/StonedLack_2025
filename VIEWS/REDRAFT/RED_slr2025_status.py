import streamlit as st
import pandas as pd
import requests
from utils import AIRTABLE_API_KEY, BASE_ID

TABLE_NAME = "SLR2025"

st.write("## Verfolge hier den Anmeldestatus")

def load_from_airtable():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        records = response.json().get("records", [])
        return pd.DataFrame([rec["fields"] for rec in records])
    return pd.DataFrame(columns=["Sleeper", "Discord", "Commish", "Mitspieler", "Anmeldezeit"])


anmeldungen = load_from_airtable()
anmeldungen['sleeper_lower'] = anmeldungen['Sleeper'].str.lower()
anmeldungen = anmeldungen.sort_values(by="Anmeldezeit").drop_duplicates(subset="sleeper_lower", keep="last")
anmeldungen['Anmeldezeit'] = pd.to_datetime(anmeldungen['Anmeldezeit']).dt.strftime('%d.%m.%Y %H:%M')
anz_anmeldungen = len(anmeldungen)
anz_ligen = int(anz_anmeldungen / 12)

col1, col2 = st.columns([1,1])
col1.write("Anmeldungen total")
col2.write(anz_anmeldungen)

col1, col2 = st.columns([1,1])
col1.write("Volle 12er-Ligen")
col2.write(anz_ligen)

col1, col2 = st.columns([1,1])
col1.write("Auslosung")
col2.write("Ende August 2025 live im Podcast")


st.dataframe(
    anmeldungen[["Sleeper", "Mitspieler", "Anmeldezeit"]].set_index("Anmeldezeit"),
    column_config={
        "Sleeper": st.column_config.Column(
            "Sleepername",
            width="medium"
        ),
        "Mitspieler": st.column_config.Column(
            "Wunschmitspieler",
            width="large")
    },
)

