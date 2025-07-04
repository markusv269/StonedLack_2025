import streamlit as st

select_season = st.selectbox(    "Wähle eine Saison aus",
    options=[f"Season {i}" for i in range(2017, 2026)],
    index=0,
    key="select_season"
)
season = int(select_season.split(" ")[1])  # Extrahiere die Saison aus der Auswahl
select_week = st.selectbox(    "Wähle eine Woche aus",
    options=[f"Week {i}" for i in range(1, 19)],
    index=0,
    key="select_week"
)
week = int(select_week.split(" ")[1])  # Extrahiere die Woche aus der Auswahl

def get_nfl_schedule(season, week):
    # Hier sollte die Logik zum Abrufen des NFL-Spielplans für die angegebene Saison und Woche implementiert werden
    week_url = f"https://api.sleeper.app/v1/schedule/nfl/{season}/week/{week}"

st.markdown(f"### Du hast Woche {week} in der Saison {season} ausgewählt.")