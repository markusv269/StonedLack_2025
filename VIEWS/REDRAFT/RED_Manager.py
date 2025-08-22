import streamlit as st
from supabase import create_client, Client
from collections import defaultdict

# Supabase Credentials
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

st.title("Fantasy Football Manager Übersicht")

# --- Ligen abrufen ---
leagues_res = supabase.table("leagues").select("league_id, league_name").execute()
leagues = leagues_res.data if leagues_res.data else []

if not leagues:
    st.warning("Keine Ligen gefunden!")
    st.stop()

# Sidebar: Liga auswählen
league_names = [l["league_name"] for l in leagues]
selected_league = st.selectbox("Liga auswählen", league_names)

# Liga-ID für ausgewählte Liga finden
league_id = next(l["league_id"] for l in leagues if l["league_name"] == selected_league)

# --- Manager für die Liga abrufen ---
managers_res = (
    supabase.table("managers")
    .select("user_id, roster_id, display_name, team_name")
    .eq("league_id", league_id)
    .order("roster_id")
    .limit(2000)  # z.B. 5000 statt 1000
    .execute()
)

managers = managers_res.data if managers_res.data else []

if not managers:
    st.info(f"Keine Manager für die Liga '{selected_league}' gefunden.")
else:
    st.subheader(f"Manager in Liga: {selected_league}")
    
    # Tabelle anzeigen
    st.dataframe(
        [
            {
                # "Roster ID": m["roster_id"],
                "Manager": m.get("display_name") or "-",
                "Teamname": m.get("team_name") or "-",
                # "User ID": m.get("user_id") or "-",
            }
            for m in managers
        ]
    )
