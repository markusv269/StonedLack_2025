
import streamlit as st
from supabase import create_client, Client
import pandas as pd
from config import REDLEAGUES_2025
import requests

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

for _, row in mail_df[mail_df["Email"].notna()].head(50).iterrows():
    sendgrid_mail(
        # to_email=row["Email"],
        to_email="markus.voerkel@web.de",  # Temporarily hardcoded for testing
        sleeper_name=row["Sleeper"],
        league=row["league_name"],
        draftpos=row["draft_pos"],
        invitelink=row["invite_link"],
        commish=row["Commish"]
    )

# print(mail_df[mail_df["Email"].notna()].shape)