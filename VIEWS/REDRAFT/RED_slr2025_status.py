import streamlit as st
from pyairtable import Table
import pandas as pd

AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
BASE_ID = st.secrets["airtable"]["base_id"]
TABLE_NAME = "SLR2025"

st.write("## Verfolge hier den Anmeldestatus")

def load_from_airtable():
    table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
    records = table.all()
    
    if not records:
        return pd.DataFrame(columns=["Sleeper", "Discord", "Commish", "Mitspieler", "Anmeldezeit"])

    # DataFrame erstellen
    df = pd.DataFrame([record["fields"] for record in records])

    # Anmeldezeit umwandeln in datetime
    df["Anmeldezeit"] = pd.to_datetime(df["Anmeldezeit"], errors="coerce")

    # Mitspieler in Liste umwandeln (falls es ein String ist)
    if "Mitspieler" in df.columns:
        df["Mitspieler"] = df["Mitspieler"].apply(lambda x: x if isinstance(x, list) else [s.strip() for s in str(x).split(",")] if pd.notna(x) else [])

    # Sortieren und den jeweils neuesten Eintrag je Sleeper behalten
    df = df.sort_values(by=["Sleeper", "Anmeldezeit"], ascending=[True, False])
    df = df.drop_duplicates(subset=["Sleeper"], keep="first")

    return df
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

