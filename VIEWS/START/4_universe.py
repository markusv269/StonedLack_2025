import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import requests
from config import DYNLEAGUES, REDLEAGUES

# Vorgegebene Ligen
LEAGUE_IDS = DYNLEAGUES + REDLEAGUES
st.title("Das StonedLack Universum")
st.write("_Das Laden des Ligen-Netzwerkes dauert ein wenig!_")

# Funktion zum Abrufen der Ligadaten (mit Caching)
@st.cache_data
def get_league_data(league_id):
    url = f"https://api.sleeper.app/v1/league/{league_id}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {}

@st.cache_data
def get_users_from_league(league_id):
    url = f"https://api.sleeper.app/v1/league/{league_id}/users"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []

# Erstelle Knoten und Kanten
def prepare_data(selected_leagues=None, search_query=None):
    nodes, edges = [], []
    errors = []

    for league_id in LEAGUE_IDS:
        if selected_leagues and league_id not in selected_leagues:
            continue  # Nur ausgewählte Ligen laden

        league_info = get_league_data(league_id)
        if not league_info:
            errors.append(f"Liga {league_id} konnte nicht geladen werden.")
            continue

        league_name = league_info.get('name', 'Unbekannte Liga')
        draft_id = league_info.get('draft_id', 'keine')
        users = get_users_from_league(league_id)

        nodes.append({"data": {"id": f"league_{league_id}", "label": "LEAGUE", "name": league_name, "Draft-ID": draft_id}})
        
        for user in users:
            if search_query and search_query.lower() not in user['display_name'].lower():
                continue  
            user_id, display_name = user['user_id'], user['display_name']
            nodes.append({"data": {"id": f"user_{user_id}", "label": "USER", "name": display_name}})
            edges.append({"data": {"id": f"edge_{league_id}_{user_id}", "label": "PARTICIPATES", "source": f"league_{league_id}", "target": f"user_{user_id}"}})
    
    if errors:
        st.error("\n".join(errors))  # Zeigt alle Fehler gesammelt an

    return {"nodes": nodes, "edges": edges}

# UI für die Auswahl der Ligen
league_names = [get_league_data(league_id).get('name', 'Unbekannte Liga') for league_id in LEAGUE_IDS]
st.markdown("### Wähle eine oder mehrere Ligen aus:")
selected_league_names = st.multiselect("Ligen auswählen", options=league_names)

# Umwandlung der Namen in IDs
selected_leagues_ids = [
    LEAGUE_IDS[league_names.index(name)] for name in selected_league_names if name in league_names
]

# UI für die Benutzersuche
search_query = st.text_input("Benutzer suchen (Teil des Namens)")

# Bereite die Daten basierend auf den Benutzerangaben vor
elements = prepare_data(selected_leagues_ids, search_query)

# Node- & Edge-Styling
node_styles = [
    NodeStyle("LEAGUE", "#FF7F3E", "name", "league"),
    NodeStyle("USER", "#2A629A", "name", "user"),
]

edge_styles = [EdgeStyle("PARTICIPATES", directed=False)]

# Graph rendern
st_link_analysis(elements, "cose", node_styles, edge_styles)
