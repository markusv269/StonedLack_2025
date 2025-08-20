
import streamlit as st
from supabase import create_client, Client
import pandas as pd
from config import REDLEAGUES_2025
import requests
from sleeper_wrapper import League, User

leagues = REDLEAGUES_2025
name_link_dict = {league["name"]: league["invitelink"] for league in leagues.values()}

def sendgrid_mail(to_email, sleeper_name, league, draftpos, invitelink, commish):
    url = "https://api.sendgrid.com/v3/mail/send"
    api_key = st.secrets["sendgrid"]["api_key"]
    from_email = st.secrets["sendgrid"]["from_email"]
    commish_text = "Du bist Commish der Liga, bitte beachte die einleitenden Hinweise, die im Liga-Chat hinterlegt sind."
    email_text = f"""
Hallo {sleeper_name},

die Auslosung der SLR2025 ist erfolgt! 🏈

Du wurdest in die Liga "{league}" gelost. Deine Draftposition ist #{draftpos}.
Bitte tritt der Liga bei, indem du auf den folgenden Link klickst:
{invitelink}

{commish_text if commish else ""}

Danke und viel Erfolg in der Saison!

Viele Grüße  
Dein Stoned Lack Team
"""

    data = {
        "personalizations": [{
            "to": [{"email": to_email}],
            "subject": "Auslosung der Stoned Lack Redraft Ligen für 2025    "
        }],
        "from": {"email": from_email, "name": "Stoned Lack Redraft"},
        "content": [{"type": "text/plain", "value": email_text}]
    }

    response = requests.post(url, json=data, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    })

    return response.status_code == 202

# Supabase-Konfiguration
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

auslosung = supabase.table("Auslosung").select("*").execute()
auslosung_df = pd.DataFrame(auslosung.data)

anmeldung = supabase.table("SLR2025").select("*").execute()
anmeldung_df = pd.DataFrame(anmeldung.data)

auslosung_df_long = auslosung_df.melt(id_vars=["league_name"], var_name="draft_pos", value_name="sleeper_name")

mail_df = auslosung_df_long.merge(anmeldung_df, left_on="sleeper_name", right_on="Sleeper", how="left")
mail_df["invite_link"] = mail_df["league_name"].map(name_link_dict)
mail_df["Email"] = "markus.voerkel@googlemail.com"
def sendgrid_mail_multi_bcc(to_emails, league, players, invitelink):
    """
    Sendet eine Mail an mehrere Owner einer Liga (alle im BCC).
    
    to_emails: Liste von Emails (Strings)
    league: Name der Liga
    players: Liste von Dicts [{sleeper_name, draftpos, commish}]
    invitelink: Sleeper Invite-Link
    """
    url = "https://api.sendgrid.com/v3/mail/send"
    api_key = st.secrets["sendgrid"]["api_key"]
    from_email = st.secrets["sendgrid"]["from_email"]

    # E-Mail Text vorbereiten
    player_lines = []
    for p in players:
        line = f"- {p['sleeper_name']} (Draftpos #{p['draftpos']})"
        if p["commish"]:
            line += " [Commish]"
        player_lines.append(line)
    
    email_text = f"""
Hallo zusammen,

die Auslosung der SLR2025 ist erfolgt! 🏈

Ihr wurdet in die Liga "{league}" gelost.
Hier sind die Draftpositionen:

{chr(10).join(player_lines)}

Bitte tretet der Liga bei, indem ihr auf den folgenden Link klickt:
{invitelink}

Viel Erfolg in der Saison und viel Spaß!

Viele Grüße  
Euer Stoned Lack Team
"""

    data = {
        "personalizations": [{
            "to": [{"email": from_email}],  # Dummy-To (wird benötigt)
            "bcc": [{"email": e} for e in to_emails],
            "subject": f"Auslosung der Stoned Lack Redraft Liga {league} für 2025"
        }],
        "from": {"email": from_email, "name": "Stoned Lack Redraft"},
        "content": [{"type": "text/plain", "value": email_text}]
    }

    response = requests.post(url, json=data, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    })

    return response.status_code == 202


# # --- Aufruf pro Liga ---
for league_name, group in mail_df.groupby("league_name"):
    group = group[group["Email"].notna()]  # Nur mit Email

    if group.empty:
        continue

    to_emails = group["Email"].tolist()
    players = group[["Sleeper", "draft_pos", "Commish"]].rename(
        columns={"Sleeper": "sleeper_name", "draft_pos": "draftpos", "Commish": "commish"}
    ).to_dict("records")
    invitelink = group["invite_link"].iloc[0]

    sendgrid_mail_multi_bcc(to_emails, league_name, players, invitelink)
    # print(group, to_emails, league_name, players, invitelink)
    print(f"Mail an Liga {league_name} gesendet ({len(to_emails)} Empfänger, BCC)")