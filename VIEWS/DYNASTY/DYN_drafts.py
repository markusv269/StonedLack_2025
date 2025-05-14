import streamlit as st
from config import DYNLEAGUES
from utils import display_draft

st.write("### Draftübersicht")
st.write('''Die Draftübersicht wurde auf die neue Saison 2025 umgestellt. 
Nur Ligen, die zur neuen Saison einen Draft eingestellt haben, werden nun angezeigt. 
Alle Ligen können den Ligenübersichten entnommen werden. 
''')
for league_id in DYNLEAGUES:
    display_draft(league_id)