import streamlit as st
import random
from pyairtable import Table
import networkx as nx

# Airtable Setup
AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
BASE_ID = st.secrets["airtable"]["base_id"]
TABLE_NAME = "SLR2025"

def lade_teilnehmer():
    table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
    records = table.all()
    teilnehmer = []
    for rec in records:
        f = rec['fields']
        teilnehmer.append({
            "name": f.get("Sleeper"),
            "is_commish": f.get("Commish", False),
            "wunschmitspieler": f.get("Mitspieler", [])
        })
    return teilnehmer

def finde_wunschgruppen(teilnehmer):
    G = nx.Graph()
    for person in teilnehmer:
        G.add_node(person["name"])
    name_to_wishes = {p["name"]: set(p.get("wunschmitspieler", [])) for p in teilnehmer}
    for name, wishes in name_to_wishes.items():
        for wished_name in wishes:
            if wished_name in name_to_wishes and name in name_to_wishes[wished_name]:
                G.add_edge(name, wished_name)
    return [list(gruppe) for gruppe in nx.connected_components(G)]

def bilde_ligen(teilnehmer, gruppen):
    name_to_teilnehmer = {p["name"]: p for p in teilnehmer}
    alle_namen = [p["name"] for p in teilnehmer]
    random.shuffle(gruppen)

    commishs = [p["name"] for p in teilnehmer if p["is_commish"]]
    random.shuffle(commishs)

    anzahl_ligen = len(teilnehmer) // 12
    ligen = [[] for _ in range(anzahl_ligen)]
    warteliste = []

    # Commishs verteilen
    for i, commish in enumerate(commishs[:anzahl_ligen]):
        ligen[i].append(commish)

    belegte_namen = set(commishs[:anzahl_ligen])

    # Wunschgruppen zuweisen
    for gruppe in gruppen:
        if any(n in belegte_namen for n in gruppe):
            continue  # wurde schon verteilt (z.B. Commish)
        zugewiesen = False
        random.shuffle(ligen)
        for liga in ligen:
            if len(liga) + len(gruppe) <= 12:
                liga.extend(gruppe)
                belegte_namen.update(gruppe)
                zugewiesen = True
                break
        if not zugewiesen:
            warteliste.extend(gruppe)

    # Restliche Einzelspieler zufällig verteilen
    rest = [n for n in alle_namen if n not in belegte_namen]
    random.shuffle(rest)
    for name in rest:
        for liga in ligen:
            if len(liga) < 12:
                liga.append(name)
                break
        else:
            warteliste.append(name)

    # Rückgabe: Liste von Ligen + Warteliste
    return [[name_to_teilnehmer[n] for n in liga] for liga in ligen], [name_to_teilnehmer[n] for n in warteliste]

# Streamlit UI
st.title("Fantasy Sleeper Ligen Auslosung")

if st.button("Auslosung starten"):
    teilnehmer = lade_teilnehmer()
    gruppen = finde_wunschgruppen(teilnehmer)
    ligen, warteliste = bilde_ligen(teilnehmer, gruppen)

    for i, liga in enumerate(ligen):
        st.subheader(f"Liga {i+1}")
        for p in liga:
            name = p['name']
            is_commish = " (Commish)" if p.get("is_commish") else ""
            st.write(f"- {name}{is_commish}")

    if warteliste:
        st.subheader("Warteliste")
        for p in warteliste:
            st.write(f"- {p['name']}")