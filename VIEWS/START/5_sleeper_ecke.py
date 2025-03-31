import streamlit as st
import requests

with st.expander("Sleeper Trending Players"):
    # Setze den Titel der App
    col1, col2 = st.columns(2)
    with col1:
        hours = st.slider("Zeitraum angeben (h)", min_value=6, step=6, max_value=7*24)
    with col2:
        player = st.slider("Anzahl der angezeigten Spieler", min_value=5, max_value=25)

    # Einbetten des Sleeper-Widgets mit einem IFrame
    sleeper_url = "https://sleeper.app/embed/players/nfl/trending/{}?lookback_hours={}&limit={}"
    add_url = sleeper_url.format("add", hours, player)
    drop_url = sleeper_url.format("drop", hours, player)
    col1, col2 = st.columns(2)
    with col1:
        st.components.v1.iframe(add_url, width=300, height=20+player*50, scrolling=False)
    with col2:
        st.components.v1.iframe(drop_url, width=300, height=20+player*50, scrolling=False)

with st.expander("NFL State"):
    state_url = "https://api.sleeper.app/v1/state/nfl"
    response = requests.get(state_url)
    sleeper_state = response.json() if response.status_code == 200 else {}
    col1, col2 = st.columns(2)
    with col1:
        st.write('''
        Saison  
        Saisonstatus   
        Woche''')
    with col2:
        st.write(f'''
        {sleeper_state["season"]}  
        {sleeper_state["season_type"]}  
        {sleeper_state["week"]}''')
    # st.write(sleeper_state)