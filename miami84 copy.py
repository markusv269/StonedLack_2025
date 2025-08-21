import streamlit as st
from sleeper_wrapper import League, User
from supabase import create_client, Client
import pandas as pd
from config import REDLEAGUES_2025

league_ids = list(REDLEAGUES_2025.keys())

# Supabase-Konfiguration


from supabase import create_client
from sleeper_wrapper import User

# 🔑 Supabase Verbindung
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Tabellenname
TABLE = "SLR2025"

# # 1️⃣ Alle Einträge mit sleeper-Namen laden
# rows = supabase.table(TABLE).select("index, Sleeper").execute().data

# for row in rows:
#     sleeper_name = row["Sleeper"]
#     record_id = row["index"]

#     if not sleeper_name:
#         continue

#     try:
#         # 2️⃣ Sleeper-API: user_id abrufen
#         sleeper_user = User(sleeper_name).get_user()
#         user_id = sleeper_user.get("user_id")

#         if user_id:
#             # 3️⃣ Update in Supabase
#             supabase.table(TABLE).update({"user_id": user_id}).eq("index", record_id).execute()
#             print(f"✅ {sleeper_name} → {user_id}")
#         else:
#             print(f"⚠️ Keine user_id für {sleeper_name} gefunden")

#     except Exception as e:
#         print(f"❌ Fehler bei {sleeper_name}: {e}")


# # Tabellenname in Supabase
# TABLE = "signups"


VALID_SIGNUPS = 12 * 48  # 552

# 1️⃣ Letzte 552 Anmeldungen laden
rows = (
    supabase.table(TABLE)
    .select("user_id, Email, Discord, Anmeldezeit")
    .order("Anmeldezeit", desc=False)
    .execute()
    .data
)

# Map user_id → email, discord
registered_users = {
    row["user_id"]: {"email": row.get("Email"), "discord": row.get("Discord")}
    for row in rows
    if row.get("user_id")
}

registered_user_ids = set(registered_users.keys())

# 2️⃣ Alle User aus den Sleeper-Leagues sammeln
league_user_ids = set()
for league_id in REDLEAGUES_2025:
    league = League(league_id)
    rosters = league.get_rosters()
    for roster in rosters:
        owner_id = roster.get("owner_id")
        if owner_id:
            league_user_ids.add(owner_id)

# 3️⃣ Fehlende User = registriert, aber nicht in den Ligen
missing_users_leagues = registered_user_ids - league_user_ids
mising_users_registration = league_user_ids - registered_user_ids

# 4️⃣ Ausgabe mit Display Name + Email + Discord
for user_id in missing_users_leagues:
    sleeper_user = User(user_id).get_user()
    display_name = sleeper_user.get("display_name")
    email = registered_users[user_id].get("email", "—")
    discord = registered_users[user_id].get("discord", "—")
    print(f"❌ Fehlend: {display_name} ({user_id}) | Email: {email} | Discord: @{discord}")

for user_id in mising_users_registration:
    sleeper_user = User(user_id).get_user()
    display_name = sleeper_user.get("display_name")
    print(f"❌ Fehlend: {display_name} ({user_id})")