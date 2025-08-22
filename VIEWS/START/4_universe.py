import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
from supabase import create_client, Client
from config import DYNLEAGUES_2025

# --- Supabase Setup ---
url: str = st.secrets["supabase"]["url"]
key: str = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

LEAGUE_IDS = DYNLEAGUES_2025

st.title("Das StonedLack Universum")
st.write("_Das Laden des Ligen-Netzwerks erfolgt aus der Supabase-Datenbank_")

# --- Daten aus Supabase laden ---
@st.cache_data(ttl=3600*24, show_spinner=True)
def get_league_data(league_ids=None):
    query = supabase.table("leagues").select("*")
    if league_ids:
        query = query.in_("league_id", league_ids)
    resp = query.execute()
    return resp.data or []

@st.cache_data(ttl=3600*24, show_spinner=True)
def get_managers_all(league_ids=None):
    all_managers = []
    offset = 0
    batch_size = 1000

    while True:
        query = supabase.table("managers").select("*").range(offset, offset + batch_size - 1)
        if league_ids:
            query = query.in_("league_id", league_ids)
        resp = query.execute()
        batch = resp.data or []

        if not batch:
            break

        all_managers.extend(batch)
        offset += batch_size

    return all_managers

# --- Knoten & Kanten vorbereiten ---
@st.cache_data(ttl=3600*24, show_spinner=True)
def prepare_data(selected_leagues=None, search_query=None):
    nodes, edges = [], []

    leagues_data = get_league_data(selected_leagues)
    managers_data = get_managers_all(selected_leagues)

    # Knoten für Ligen
    for league in leagues_data:
        nodes.append({
            "data": {
                "id": league["league_id"],
                "label": "LEAGUE",
                "name": league.get("league_name", "Unbekannte Liga")
            }
        })

    # Knoten für Manager + Kanten
    for manager in managers_data:
        if search_query and search_query.lower() not in (manager.get("display_name") or "").lower():
            continue
        user_id = manager["user_id"]
        roster_id = manager["roster_id"]
        league_id = manager["league_id"]
        display_name = manager.get("display_name") or f"Roster {roster_id}"

        nodes.append({
            "data": {
                "id": user_id,
                "label": "USER",
                "name": display_name
            }
        })
        edges.append({
            "data": {
                "id": f"edge_{league_id}_{user_id}",
                "label": "PARTICIPATES",
                "source": league_id,
                "target": user_id
            }
        })

    return {"nodes": nodes, "edges": edges}

# --- UI ---
league_names = [l["league_name"] for l in get_league_data(LEAGUE_IDS)]
st.markdown("### Wähle eine oder mehrere Ligen aus:")
selected_league_names = st.multiselect("Ligen auswählen", options=league_names)

# Namen → IDs
selected_leagues_ids = [
    LEAGUE_IDS[league_names.index(name)] for name in selected_league_names if name in league_names
]

search_query = st.text_input("Benutzer suchen (Teil des Namens)")

elements = prepare_data(selected_leagues_ids, search_query)

node_styles = [
    NodeStyle("LEAGUE", "#FF7F3E", "name", "league"),
    NodeStyle("USER", "#2A629A", "name", "user"),
]

edge_styles = [EdgeStyle("PARTICIPATES", directed=False)]

st_link_analysis(elements, "cose", node_styles, edge_styles)
