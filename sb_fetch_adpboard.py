from supabase import create_client, Client
import requests
import streamlit as st
from datetime import datetime, timezone
import pandas as pd

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

ltype = "redraft"  # Beispiel: redraft, dynasty, keeper
# Beispiel: redraft
def get_adpboard(ltype: str):
    data = supabase.rpc("get_player_stats_by_league_type", {"ltype": ltype}).execute()
    df = pd.DataFrame(data.data)
    df["adp_round"] = (df.index)// 12 +1
    df["adp_pick"] = (df.index) % 12 +1
    df["adp_overall_pick"] = df.index + 1
    df["adp_roundpick"] = df["adp_round"].astype(str) + "." + df["adp_pick"].astype(str)
    # Beispiel: dynasty
    # dynasty_data = supabase.rpc("get_player_stats_by_league_type", {"ltype": "dynasty"}).execute()

    # print(redraft_data_df[['name', 'adp_roundpick']].head(50))
    df.drop(columns=["player_id", "adp_round", "adp_pick"]).to_csv(f"adpboard_{ltype}_2025.csv", index=False)
    return df