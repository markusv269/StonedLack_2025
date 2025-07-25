import streamlit as st
from sleeper_wrapper import User
from datetime import datetime
from supabase import create_client, Client
import pandas as pd
import uuid
import requests

# Supabase-Konfiguration
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_data
def get_user_id(username):
    try:
        user = User(username)
        return user.get_user_id() is not None
    except Exception:
        return False

def sendgrid_mail(to_email, sleeper_name, schluessel):
    url = "https://api.sendgrid.com/v3/mail/send"
    api_key = st.secrets["sendgrid"]["api_key"]
    from_email = st.secrets["sendgrid"]["from_email"]

    email_text = f"""
Hallo {sleeper_name},

vielen Dank für deine Anmeldung zu den StonedLack Redraft Ligen 2025! 🏈

🔐 Dein persönlicher Anmeldeschlüssel:
{schluessel}

Bitte speichere diesen gut ab – du brauchst ihn, um deine Anmeldung später zu ändern.

Viele Grüße  
Dein StonedLack Team
"""

    data = {
        "personalizations": [{
            "to": [{"email": to_email}],
            "subject": "🔐 Dein SLR2025 Anmeldeschlüssel"
        }],
        "from": {"email": from_email, "name": "StonedLack Redraft"},
        "content": [{"type": "text/plain", "value": email_text}]
    }

    response = requests.post(url, json=data, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    })

    return response.status_code == 202

def anmeldung_slr(sleeper, discord, commish, mitspieler, email, schluessel_input=None):
    index_value = sleeper.lower()
    user = User(index_value)
    display_name = user.get_display_name() or index_value

    result = supabase.table("SLR2025").select("*").eq("index", index_value).execute()
    existing = result.data[0] if result.data else None

    if existing:
        gespeicherter_schluessel = existing.get("Schlüssel", "")
        if schluessel_input != gespeicherter_schluessel:
            st.error("Falscher Schlüssel! Deine Anmeldung kann nicht geändert werden.")
            return

        first_checkin_time = existing.get("Anmeldezeit")
        supabase.table("SLR2025").update({
            "Sleeper": display_name,
            "Discord": discord,
            "Commish": commish,
            "Mitspieler": ", ".join(mitspieler),
            "Anmeldezeit": first_checkin_time or datetime.utcnow().isoformat()
        }).eq("index", index_value).execute()
        st.success("✅ Deine Anmeldung wurde aktualisiert.")
    else:
        schluessel = uuid.uuid4().hex[:8]
        eintrag = {
            "index": index_value,
            "Sleeper": display_name,
            "Discord": discord,
            "Commish": commish,
            "Mitspieler": ", ".join(mitspieler),
            "Email": email,
            "Anmeldezeit": datetime.utcnow().isoformat(),
            "Schlüssel": schluessel
        }
        supabase.table("SLR2025").insert(eintrag).execute()
        st.success("✅ Du bist jetzt für die StonedLack Redraftligen 2025 registriert.")

        if email:
            if sendgrid_mail(email, display_name, schluessel):
                st.success(f"✅ Bestätigung wurde an {email} gesendet.")
            else:
                st.error("❌ Fehler beim Mailversand.")
        else:
            st.info(f"🔐 Dein Schlüssel: **{schluessel}**")

# --- UI START ---

left, right = st.columns([2,6])
with left:
    st.image("Pictures/SL_logo.png", width=200)

with right:
    st.markdown("""
    ### 📝 Anmeldung zu den **Stoned Lack Redraft Ligen 2025**
    
    Willkommen zur Anmeldung für die allseits beliebten **Stoned Lack Redraft Ligen**! 🏈  
    Gespielt wird auf [Sleeper](https://sleeper.com/). Die Zuteilung zu einer Liga erfolgt per **Live-Auslosung Ende August 2025** im Stream von Stoned Lack!

    **🔹 Infos:**
    - Sleeper & Discord müssen exakt angegeben werden.
    - Du kannst maximal **3 Wunsch-Mitspieler** angeben.
    - Nach Anmeldung bekommst du einen Schlüssel (per Mail oder angezeigt), mit dem du später deine Anmeldung ändern kannst.
    """)

    mode = st.radio("Möchtest du dich neu anmelden oder eine bestehende Anmeldung ändern?", ["Anmeldung", "Aktualisierung"])
    commish = st.checkbox("Ich übernehme einen Commish-Posten!")
    mitspieler = st.checkbox("Ich möchte mit jemandem zusammenspielen")

    with st.form("SLR 2025 Anmeldung/Aktualisierung"):
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

        email = ""
        schluessel_input = ""
        if mode == "Anmeldung":
            email = st.text_input("✉️ Deine E-Mail-Adresse für Schlüsselzusendung (Optional)", key="email")
        else:
            schluessel_input = st.text_input("🔐 Anmeldeschlüssel", help="Nur erforderlich bei Änderung.")

        submitted = st.form_submit_button("Absenden")

        if submitted:
            if not sleeper_name or not discord_name:
                st.error("Bitte fülle alle Pflichtfelder aus!")
            elif not get_user_id(sleeper_name):
                st.error("Der angegebene Sleeper-Name ist ungültig oder existiert nicht.")
            elif any(not get_user_id(m) for m in mitspieler_names):
                st.error("Bitte gib gültige Mitspieler-Namen an.")
            else:
                anmeldung_slr(sleeper_name, discord_name, commish, mitspieler_names, email, schluessel_input)

# --- Statusanzeige ---

st.write("## Anmeldestatus SLR2025")
result = supabase.table("SLR2025").select("*").order("Anmeldezeit", desc=True).execute()
records = result.data

if records:
    st.write("Hier siehst du die aktuell angemeldeten Teilnehmenden.")
    n_leagues = len(records) // 12
    n_waiters = len(records) % 12
    n_commish = sum(1 for r in records if r.get("Commish") is True)
    st.success(f"Anzahl der Anmeldungen: {len(records)} ({n_commish} Commishs)")
    
    left, right = st.columns(2)
    with left:
        st.success(f"Anzahl volle Ligen: {n_leagues}")
        # if n_commish > n_leagues:
        #     st.success(f"Aktuell mehr Commishs ({n_commish}) als Ligen.")
        # else:
        #     st.warning("Wir brauchen mehr Commishs!")
    with right:
        st.info(f"Nachrücker: {n_waiters}")
        

    df = pd.DataFrame(records)
    df["Commish"] = df.get("Commish", False)
    df["Mitspieler"] = df.get("Mitspieler", "")
    st.dataframe(df[["Sleeper", "Discord", "Commish", "Mitspieler"]],
                 use_container_width=True,
                 hide_index=True,
                 column_config={"Mitspieler": st.column_config.TextColumn("Gewünschte Mitspieler")})
else:
    st.warning("Noch keine Anmeldungen vorhanden.")
