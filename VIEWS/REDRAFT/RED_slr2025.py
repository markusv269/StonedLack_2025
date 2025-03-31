import streamlit as st
from sleeper_wrapper import User
from utils import AIRTABLE_API_KEY, BASE_ID 
import datetime, time
from datetime import datetime
import requests
import json

AIRTABLE_API_KEY = AIRTABLE_API_KEY
BASE_ID = BASE_ID
TABLE_NAME = "SLR2025"

def save_to_airtable(sleeper, discord, commish, mitspieler):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "records": [
            {"fields": {"Sleeper": sleeper, "Discord": discord, "Commish": commish, "Mitspieler": ", ".join(map(str, mitspieler)), "Anmeldezeit": datetime.now().isoformat()}}
             ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Debugging-Ausgabe
    if response.status_code != 200:
        print(f"Fehler: {response.status_code}")
        print(response.text)

    return response.status_code == 200

@st.cache_data
def get_user_id(username):
    """Cached function to fetch Sleeper user ID."""
    try:
        user = User(username)
        return user.get_user_id() is not None
    except Exception:
        return False
st.markdown(f'''
    #### 📝 Anmeldung zu den **Stoned Lack Redraft Ligen 2025**
            
    Willkommen zur Anmeldung für die allseits beliebten **Stoned Lack Redraft Ligen**! 🏈
            
    Gespielt wird auf [Sleeper](https://sleeper.com/). Die Zuteilung zu einer Liga erfolgt per **Live-Auslosung Ende August 2025** im Stream von Stoned Lack!
    
    **🔹 Wichtige Infos zur Anmeldung:**
    - Tragt eure **Kontakt-Daten** ein, mit denen euch der Commissioner nach der Auslosung einladen kann.
    - Achtet auf die **genaue Schreibweise eurer Namen in Sleeper & Discord**.
    - **Der Sleeper-Name ist zwingend erforderlich** und wird überprüft, da dieser für die Zuteilung und die Mitspielerwünsche genutzt wird.
    - Falls ihr noch keinen Sleeper-Account habt, erstellt euch einen unter: [Sleeper-Registrierung](https://sleeper.com/create).
    
    **⏳ Ablauf:**
    - Nach der **Auslosung** erhaltet ihr eine **Einladung** über Sleeper oder Discord.
    - Bitte schaut regelmäßig in **Sleeper & Discord**, damit die Liga zügig zustande kommt und der Draft starten kann.
    
    ---
    
    #### 🙌 Werde Commissioner!
    
    Eine Liga ist nur so gut wie ihr Commissioner! Falls du Lust hast, eine Liga zu leiten, melde dich gerne. 🏆
    - **Erfahrung ist nicht zwingend nötig** – Unterstützung gibt’s im **Stoned Lack Army Discord oder direkt in der sleeper-Liga**.
    - Ohne freiwillige Commissioner gibt es keine Ligen – also trau dich! 💪
    
    ---
    
    #### ℹ️ Datenschutz & Anmeldestatus
    
    _Die hier erhobenen Daten werden ausschließlich zur Durchführung der Stoned Lack Redraft Ligen gespeichert und nach Ende der Saison gelöscht._
    
    - **Datenaktualisierung**  
    Falls ihr eure Anmeldung überschreiben wollt, meldet euch einfach mit dem **gleichen Sleeper-Namen** erneut an. Es zählt immer der letzte Eintrag.
    - **Status prüfen**  
    Seht unter SLR2025 Anmeldestatus nach, ob eure Anmeldung erfasst wurde.
    
    Wir freuen uns auf euch! **Let’s go! 🚀**
''')
st.write("## Melde Dich hier für die StonedLack Redraftligen 2025 an")
commish = st.checkbox("Ich übernehme einen Commish-Posten!")
mitspieler = st.checkbox("Ich möchte mit jemandem zusammenspielen")

with st.form("Anmeldung SLR 2025"):
    sleeper_name = st.text_input("Dein Sleeper-Name", key="sleeper")
    discord_name = st.text_input("Dein Discord-Name", key="discord")

    mitspieler_names = []
    if mitspieler:
        st.write("Trage bis zu 3 Mitspieler ein:")
        col1, col2, col3 = st.columns(3)
        mitspieler_inputs = [
            col1.text_input("Mitspieler 1"),
            col2.text_input("Mitspieler 2"),
            col3.text_input("Mitspieler 3")
        ]
        mitspieler_names = [name.strip() for name in mitspieler_inputs if name.strip()]
    
    submitted = st.form_submit_button("Anmelden!")

    if submitted:
        errors = []
        
        if not sleeper_name:
            errors.append("Bitte gib deinen Sleeper-Namen an.")
        elif not get_user_id(sleeper_name):
            errors.append(f"Sleeper-Name '{sleeper_name}' nicht gefunden. Bitte überprüfe deine Eingabe. Noch keinen sleeper-Account? Dann melde über https://sleeper.com/create an.")
        
        # if not discord_name:
        #     errors.append("Bitte gib deinen Discord-Namen an.")
        
        for name in mitspieler_names:
            if not get_user_id(name):
                errors.append(f"Mitspieler '{name}' nicht gefunden. Bitte überprüfe den Sleeper-Namen.")
        
        if errors:
            st.error("\n".join(errors))
        else:
            st.success("Anmeldung erfolgreich!")
            save_to_airtable(sleeper_name, discord_name, commish, mitspieler=mitspieler_names)