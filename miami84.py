import streamlit as st
import duckdb
import requests
import pandas as pd
import os

# --- Einstellungen ---
GITHUB_RAW_URL = "https://github.com/markusv269/StonedLack_pydantic_duckDB/raw/main/data/sleeper.duckdb"
LOCAL_DB_PATH = "sleeper.duckdb"

# --- DuckDB herunterladen, falls nicht lokal vorhanden ---
if not os.path.exists(LOCAL_DB_PATH):
    st.info("Lade DuckDB-Datenbank von GitHub...")
    r = requests.get(GITHUB_RAW_URL)
    if r.status_code == 200:
        with open(LOCAL_DB_PATH, "wb") as f:
            f.write(r.content)
        st.success("Datenbank erfolgreich heruntergeladen!")
    else:
        st.error(f"Fehler beim Herunterladen der Datenbank: {r.status_code}")

# --- Verbindung zu DuckDB ---
conn = duckdb.connect(LOCAL_DB_PATH)

# --- Tabellenauswahl ---
tables = conn.execute("SHOW TABLES").fetchall()
tables = [t[0] for t in tables]

selected_table = st.selectbox("Wähle eine Tabelle aus", tables)

# --- Daten anzeigen ---
if selected_table:
    df = conn.execute(f"SELECT * FROM {selected_table} LIMIT 100").fetchdf()
    st.dataframe(df)

# --- Optional: SQL-Abfrage ---
st.subheader("SQL-Abfrage ausführen")
user_query = st.text_area("SQL-Abfrage:", f"SELECT * FROM {selected_table} LIMIT 10")

if st.button("Abfrage ausführen"):
    try:
        query_result = conn.execute(user_query).fetchdf()
        st.dataframe(query_result)
    except Exception as e:
        st.error(f"Fehler bei der Abfrage: {e}")