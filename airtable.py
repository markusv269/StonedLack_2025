


BASE_ID = st.secrets["airtable"]["base_id"]
AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
TABLE_NAME = st.secrets["airtable"]["table_name"]

def save_to_airtable(**kwargs):
    if not BASE_ID or not AIRTABLE_API_KEY or not TABLE_NAME:
        print("❌ Fehler: BASE_ID, AIRTABLE_API_KEY oder TABLE_NAME fehlt.")
        return False

    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Konvertiere datetime/date-Werte zu Strings
    fields = {}
    for key, value in kwargs.items():
        if isinstance(value, (datetime, date)):
            fields[key] = value.strftime("%Y-%m-%d")
        elif isinstance(value, list):  
            fields[key] = ", ".join(value)  # Listen als kommagetrennten String speichern
        # elif key == "Commish":  
        #     fields[key] = bool(value)  # ✅ Boolean-Wert für Airtable-Kontrollkästchen
        else:
            fields[key] = value

    data = {"records": [{"fields": fields}]}

    try:
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()  # JSON-Response für Debugging

        if response.status_code in [200, 201]:
            print("✅ Erfolgreich gespeichert in Airtable!")
            return True
        else:
            print(f"❌ Fehler: {response.status_code}")
            print("🔍 Airtable-Fehlermeldung:", json.dumps(response_json, indent=2))
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Anfrage fehlgeschlagen: {e}")
        return False