import streamlit as st
from sleeper_wrapper import User
import datetime
from datetime import datetime
from pyairtable import Table
from pyairtable.formulas import match
import pandas as pd

@st.cache_data
def get_user_id(username):
    """Cached function to fetch Sleeper user ID."""
    try:
        user = User(username)
        return user.get_user_id() is not None
    except Exception:
        return False

AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
BASE_ID = st.secrets["airtable"]["base_id"]
TABLE_NAME = "SLR2025"

import uuid

def anmeldung_slr(sleeper, discord, commish, mitspieler, schluessel_input=None):
    table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
    index_value = sleeper.lower()
    user = User(index_value)
    display_name = user.get_display_name() or index_value
    existing = table.first(formula=match({"index": index_value}))

    if existing:
        gespeicherter_schluessel = existing['fields'].get("Schlüssel", "")
        if schluessel_input != gespeicherter_schluessel:
            st.error("Falscher Schlüssel! Deine Anmeldung kann nicht geändert werden.")
            return

        first_checkin_time = existing['fields'].get('Anmeldezeit', None)
        table.update(existing['id'], {
            "Sleeper": display_name,
            "Discord": discord,
            "Commish": commish,
            "Mitspieler": ", ".join(map(str, mitspieler)),
            "Anmeldezeit": first_checkin_time if first_checkin_time else datetime.now().isoformat()
        })
        st.success("✅ Deine Anmeldung wurde erfolgreich aktualisiert.")
    else:
        schluessel = uuid.uuid4().hex[:8]  # Einfacher 8-stelliger Schlüssel
        table.create({
            "index": index_value,
            "Sleeper": display_name,
            "Discord": discord,
            "Commish": commish,
            "Mitspieler": ", ".join(map(str, mitspieler)),
            "Anmeldezeit": datetime.now().isoformat(),
            "Schlüssel": schluessel
        })
        st.success("✅ Du bist jetzt für die StonedLack Redraftligen 2025 registriert.")
        st.info(f"🔐 **Wichtiger Schlüssel: `{schluessel}`\nBitte speichere diesen Schlüssel sicher. Du brauchst ihn, um deine Anmeldung zu ändern!**")

left, right = st.columns([2,6])
with left:
    st.image("Pictures/SL_logo.png", width=200)
with right:
    st.markdown(f'''
    ### 📝 Anmeldung zu den **Stoned Lack Redraft Ligen 2025**
            
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
    
    Eine Liga ist nur so gut wie ihr Commissioner! Falls du Lust hast, eine Liga zu leiten, trau Dich, es kann nichts schief gehen! 🏆
    - **Erfahrung ist nicht nötig** – Unterstützung gibt’s im **Stoned Lack Army Discord oder direkt in der sleeper-Liga**.
    - Ohne freiwillige Commissioner gibt es keine Ligen – also trau dich! 💪
    
    ---
    
    #### ℹ️ Datenschutz & Anmeldestatus
    
    _Die hier erhobenen Daten werden ausschließlich zur Durchführung der Stoned Lack Redraft Ligen gespeichert und nach Ende der Saison gelöscht._
    
    - **Datenaktualisierung**  
    Falls ihr eure Anmeldung überschreiben wollt, meldet euch einfach mit dem **gleichen Sleeper-Namen** erneut an. Es zählt immer der letzte Eintrag.
    Bei der Anmeldung erhaltet ihr einen **Anmeldeschlüssel**, den ihr für zukünftige Änderungen benötigt.
    Die Anmeldezeit bleibt bei einer Änderung unverändert zum ersten Eintrag, ihr müsst also keine Angst haben, dass ihr aus der Reihe rutscht und wieder hinten ansteht.
                
    - **Anmeldeschlüssel**
    Der Anmeldeschlüssel ist ein **einmaliger Code**, der euch hilft, eure Anmeldung zu aktualisieren. Er wird bei der Anmeldung generiert und angezeigt.
    Bewahrt ihn sicher auf, da ihr ihn benötigt, um eure Anmeldung zu ändern oder zu aktualisieren.
    
    - **Status prüfen**  
    Seht unter SLR2025 Anmeldestatus nach, ob eure Anmeldung erfasst wurde.
    
    Wir freuen uns auf euch! **Let’s go! 🚀**
    ''')
    st.write("## Melde Dich hier für die StonedLack Redraftligen 2025 an")
    commish = st.checkbox("Ich übernehme einen Commish-Posten!")
    mitspieler = st.checkbox("Ich möchte mit jemandem zusammenspielen")

    with st.form("Anmeldung SLR 2025"):
        sleeper_name = st.text_input("🌙 Dein Sleeper-Name (Pflichtfeld)", key="sleeper")
        discord_name = st.text_input("💬 Dein Discord-Name (Pflichtfeld)", key="discord")

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
        
        schluessel_input = st.text_input("🔐 Dein Anmeldeschlüssel (nur bei Änderung)", help="Nur erforderlich, wenn du eine bestehende Anmeldung ändern möchtest.")
        submitted = st.form_submit_button("Anmeldung absenden")

        if submitted:
            if not sleeper_name or not discord_name:
                st.error("Bitte fülle alle Pflichtfelder aus!")
            elif not get_user_id(sleeper_name):
                st.error("Der angegebene Sleeper-Name ist ungültig oder existiert nicht.")
            elif any(not get_user_id(mitspieler) for mitspieler in mitspieler_names):
                st.error("Bitte gib gültige Mitspieler-Namen an.")
            else:
                anmeldung_slr(sleeper_name, discord_name, commish, mitspieler_names, schluessel_input)
    st.write("## Anmeldestatus SLR2025")
    table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
    records = table.all(sort=["-Anmeldezeit"])
    if records:
        st.write("Hier siehst du die aktuell angemeldeten Teilnehmenden für die SLR 2025.")
        st.success(f"Anzahl der Anmeldungen: {len(records)}")
        n_leagues = len(records) // 12
        n_waiters = len(records) % 12
        left, right = st.columns(2)
        with left:
            if n_leagues > 0:
                st.success(f"Anzahl volle Ligen: {n_leagues} :fire:")
            else:
                st.error("Noch keine volle Liga!")
        with right:
            if n_waiters > 0:
                st.warning(f"Nachrücker: {n_waiters}")
            else:
                st.success(f"Nachrücker: {n_waiters}")
        df = pd.DataFrame([record["fields"] for record in records])
        if "Commish" not in df.columns:
            df["Commish"] = df.get("Commish", False)
        if "Mitspieler" not in df.columns:
            df["Mitspieler"] = df.get("Mitspieler", "")
        st.dataframe(df[["Sleeper", "Discord", "Commish", "Mitspieler"]],
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Mitspieler": st.column_config.TextColumn("Gewünschte Mitspieler",)
                    })
    else:
        st.error("Keine Anmeldungen gefunden.")
