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
        schluessel = uuid.uuid4().hex[:8]
        eintrag = {
            "index": index_value + "_DOPPEL",
            "Sleeper": display_name,
            "Discord": discord,
            "Commish": commish,
            "Mitspieler": ", ".join(mitspieler),
            "Email": email,
            "Anmeldezeit": datetime.utcnow().isoformat(),
            "Schlüssel": schluessel,
            "Doppelanmeldung": True
        }
        supabase.table("SLR2025").insert(eintrag).execute()
        st.success("✅ Du bist ein zweites Mal für die SLR2025 registriert.")
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
    # st.markdown(f'''
    # ### 📝 Anmeldung zu den **Stoned Lack Redraft Ligen 2025**  
    # #### **<span style="color: red;">Anmeldeschluss: 15. August 2025, 20:00 Uhr</span>**
            
    # Willkommen zur Anmeldung für die allseits beliebten **Stoned Lack Redraft Ligen**! 🏈
            
    # Gespielt wird auf [Sleeper](https://sleeper.com/). Die Zuteilung zu einer Liga erfolgt per **Live-Auslosung am 15. August 2025** im Stream von Stoned Lack!
    
    # **🔹 Wichtige Infos zur Anmeldung:**
    # - Tragt eure **Kontakt-Daten** ein, mit denen euch der Commissioner nach der Auslosung einladen kann.
    # - Achtet auf die **genaue Schreibweise eurer Namen in Sleeper & Discord**.
    # - **Der Sleeper-Name ist zwingend erforderlich** und wird überprüft, da dieser für die Zuteilung und die Mitspielerwünsche genutzt wird.
    # - Falls ihr noch keinen Sleeper-Account habt, erstellt euch einen unter: [Sleeper-Registrierung](https://sleeper.com/create).
    
    # **⏳ Ablauf:**
    # - Nach der **Auslosung** erhaltet ihr eine **Einladung** über Sleeper oder Discord.
    # - Bitte schaut regelmäßig in **Sleeper & Discord**, damit die Liga zügig zustande kommt und der Draft starten kann.
    
    # ---
    
    # #### 🙌 Werde Commissioner!
    
    # Eine Liga ist nur so gut wie ihr Commissioner! Falls du Lust hast, eine Liga zu leiten, trau Dich, es kann nichts schief gehen! 🏆
    # - **Erfahrung ist nicht nötig** – Unterstützung gibt’s im **Stoned Lack Army Discord oder direkt in der sleeper-Liga**.
    # - Ohne freiwillige Commissioner gibt es keine Ligen – also trau dich! 💪
    
    # ---
    
    # #### ℹ️ Datenschutz & Anmeldestatus
    
    # _Die hier erhobenen Daten werden ausschließlich zur Durchführung der Stoned Lack Redraft Ligen gespeichert und nach Ende der Saison gelöscht._
    
    # - **Datenaktualisierung**  
    # Falls ihr eure Anmeldung überschreiben wollt, meldet euch einfach mit dem **gleichen Sleeper-Namen** erneut an. Es zählt immer der letzte Eintrag.
    # Bei der Anmeldung erhaltet ihr einen **Anmeldeschlüssel** (per Mail oder als Anzeige), den ihr für zukünftige Änderungen benötigt.
    # Die Anmeldezeit bleibt bei einer Änderung unverändert zum ersten Eintrag, ihr müsst also keine Angst haben, dass ihr aus der Reihe rutscht und wieder hinten ansteht.
                
    # - **Anmeldeschlüssel**  
    # Der Anmeldeschlüssel ist ein **einmalig erstellter Code**, der euch hilft, eure Anmeldung zu aktualisieren. Er wird bei der Anmeldung generiert und Euch entweder per Mail zugesandt oder nach der Anmeldung angezeigt.
    # Bewahrt ihn sicher auf, da ihr ihn benötigt, um eure Anmeldung zu ändern oder zu aktualisieren.
    
    # - **Status prüfen**  
    # Seht unten nach, ob eure Anmeldung erfasst wurde.
    
    # Wir freuen uns auf euch! **Let’s go! 🚀**

    # ---

    # ''', unsafe_allow_html=True)

    st.write('''
    ### 📝 Anmeldung für die SLR 2025 abgeschlossen
             
    Die Anmeldung für die Stoned Lack Redraft Ligen 2025 ist nun abgeschlossen.
    Vielen Dank an alle, die sich angemeldet haben! 
             
    Viel Erfolg in der Saison 2025.🙌
    ''')

    # # mode = st.radio("Möchtest du dich neu anmelden oder eine bestehende Anmeldung ändern?", ["Anmeldung", "Aktualisierung"])
    # commish = st.checkbox("Ich übernehme einen Commish-Posten!")
    # # mitspieler = st.checkbox("Ich möchte mit jemandem zusammenspielen")

    # with st.form("SLR 2025 Anmeldung/Aktualisierung"):
    #     sleeper_name = st.text_input("🌙 Dein Sleeper-Name (Pflichtfeld)", key="sleeper")
    #     discord_name = st.text_input("💬 Dein Discord-Name (Pflichtfeld)", key="discord")

    #     mitspieler_names = []
    #     # if mitspieler:
    #     #     st.write("Trage bis zu 3 Mitspieler ein:")
    #     #     col1, col2, col3 = st.columns(3)
    #     #     mitspieler_inputs = [
    #     #         col1.text_input("Mitspieler 1"),
    #     #         col2.text_input("Mitspieler 2"),
    #     #         col3.text_input("Mitspieler 3")
    #     #     ]
    #     #     mitspieler_names = [name.strip() for name in mitspieler_inputs if name.strip()]

    #     email = ""
    #     schluessel_input = ""
    #     # if mode == "Anmeldung":
    #     #     email = st.text_input("✉️ Deine E-Mail-Adresse für Schlüsselzusendung (Optional)", key="email")
    #     # else:
    #     #     schluessel_input = st.text_input("🔐 Anmeldeschlüssel", help="Nur erforderlich bei Änderung.")

    #     submitted = st.form_submit_button("Absenden")

    #     if submitted:
    #         if not sleeper_name or not discord_name:
    #             st.error("Bitte fülle alle Pflichtfelder aus!")
    #         elif not get_user_id(sleeper_name):
    #             st.error("Der angegebene Sleeper-Name ist ungültig oder existiert nicht.")
    #         elif any(not get_user_id(m) for m in mitspieler_names):
    #             st.error("Bitte gib gültige Mitspieler-Namen an.")
    #         else:
    #             anmeldung_slr(sleeper_name, discord_name, commish, mitspieler_names, email, schluessel_input)

    # # --- Statusanzeige ---

    # st.write("## Anmeldestatus SLR2025")
    # result = supabase.table("SLR2025").select("*").order("Anmeldezeit", desc=True).execute()
    # records = result.data

    # if records:
    #     st.write("Hier siehst du die aktuell angemeldeten Teilnehmenden.")
    #     n_leagues = 46
    #     n_waiters = len(records) - n_leagues*12
    #     n_commish = sum(1 for r in records if r.get("Commish") is True)
    #     # Graue Box mit Markdown und CSS
    #     text = f"Anzahl der Anmeldungen gesamt: {len(records)} Manager, {n_commish} Commishs"
    #     st.markdown(
    #         f"""
    #         <div style="
    #             padding: 1rem;
    #             background-color: #f0f0f0;
    #             border-radius: 0.5rem;
    #             color: #333;
    #             margin-bottom: 1rem;
    #             ">
    #             {text}
    #         </div>
    #         """,
    #         unsafe_allow_html=True
    #     )

    #     left, right = st.columns(2)
    #     with left:
    #         st.success(f"Anzahl SLR aktuell: {n_leagues}")
    #     with right:
    #         st.info(f"Nachrücker: {n_waiters}")
            
    #     # Farb-Funktion
    #     def style_row(row):
    #         if row.name < n_waiters:
    #             return [  # Blau wie st.info
    #                 'background-color: #e6f2ff; color: #004085'  # heller Hintergrund, dunklere Schrift
    #             ] * len(row)
    #         else:
    #             return [  # Grün wie st.success
    #                 'background-color: #e6ffe6; color: #155724'  # heller Hintergrund, grüne Schrift
    #             ] * len(row)

    #     df = pd.DataFrame(records)
    #     df["Commish"] = df.get("Commish", False)
    #     df["Mitspieler"] = df.get("Mitspieler", "")
    #     df_cut = df.iloc[:-12*n_leagues]   # alles außer die letzten 12*n_leagues
    #     st.dataframe(df_cut[["Sleeper", "Discord", "Commish", "Mitspieler", "Doppelanmeldung"]].style.apply(style_row, axis=1),
    #                 use_container_width=True,
    #                 hide_index=True,
    #                 column_config={"Mitspieler": st.column_config.TextColumn("Gewünschte Mitspieler")})
    # else:
    #     st.warning("Noch keine Anmeldungen vorhanden.")

    # # wunsch_dict = {}
    # # commish_df = pd.DataFrame()
    # # player_df = pd.DataFrame()

    # # # Iteration über alle Zeilen des DataFrames
    # # for index, row in df.iterrows():
    # #     spieler = row["index"]

    # #     # Wunsch-Mitspieler extrahieren
    # #     mitspieler_liste = row["Mitspieler"]
    # #     if pd.notna(mitspieler_liste):
    # #         for mitspieler in mitspieler_liste.split(","):
    # #             mitspieler = mitspieler.lower().strip()
    # #             if mitspieler:  # nur nicht-leere Strings
    # #                 wunsch_dict.setdefault(spieler, []).append(mitspieler)

    # #     # Aufteilen in Commishs und normale Spieler
    # #     if row.get("Commish", False):
    # #         commish_df = pd.concat([commish_df, row.to_frame().T], ignore_index=True)
    # #     else:
    # #         player_df = pd.concat([player_df, row.to_frame().T], ignore_index=True)

    # # # Gegenseitige Wunschgruppen finden (nur 2er-Gruppen)
    # # mutual_groups = set()
    # # for spieler, wünsche in wunsch_dict.items():
    # #     for gewünschter in wünsche:
    # #         if gewünschter in wunsch_dict and spieler in wunsch_dict[gewünschter]:
    # #             gruppe = tuple(sorted([spieler, gewünschter]))
    # #             mutual_groups.add(gruppe)

    # # # Umwandlung in Listen
    # # verified_groups = [list(gruppe) for gruppe in mutual_groups]

    # # # einseitige Erwähnung reicht
    # # group_to_merge = verified_groups.copy()

    # # def merge_groups(groups):
    # #     merged = []

    # #     for group in groups:
    # #         added = False
    # #         for mgroup in merged:
    # #             if any(elem in mgroup for elem in group):
    # #                 mgroup.update(group)
    # #                 added = True
    # #                 break
    # #         if not added:
    # #             merged.append(set(group))

    # #     return [list(mgroup) for mgroup in merged]

    # # merged_groups = merge_groups(group_to_merge)
    # # with st.expander("Gegenseitige Wunschgruppen", icon=":material/group:", expanded=False):
    # #     # st.write("#### Verifizierte Gruppen")
    # #     st.write('''*Es werden alle sleeper-Namen in Kleinbuchstaben angezeigt.*  ''')
    # #     if merged_groups:
    # #         # st.write("Hier sind die Spieler, die sich gegenseitig als Mitspieler wünschen:")
    # #         for gruppe in merged_groups:
    # #             st.write("*", " -- ".join(gruppe))
    # #     else:
    # #         st.write("Keine gegenseitigen Wunschgruppen gefunden.")