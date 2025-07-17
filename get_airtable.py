from pyairtable import Table
import pandas as pd
import streamlit as st

api_key = st.secrets["airtable"]["api_key"]
base_id = st.secrets["airtable"]["base_id"]

table_name = "Waitingroom"

def get_airtable_records():
    airtable = Table(api_key, base_id, table_name)
    records = airtable.all()
    return records

records = get_airtable_records()

# Flache Liste von Feldern plus createdTime
df = pd.DataFrame([
    {**record['fields'], 'createdTime': record['createdTime']}
    for record in records
])

df = df.sort_values(by=['option', 'createdTime'], ascending=True)

dyn_df = df[df['option'] == 'Best Ball Dynasty'].copy()
for index, row in dyn_df.head(12).iterrows():
    print(row['sleeper'])