import requests
import os
from sleeper_wrapper import League
import json


league_ids = [
    '1127181027346161664', 
    '1127182827986018304', 
    '1127186511226687488', 
    '1127186794254057472', 
    '1127187487081742336', 
    '1127311654766727168', 
    '1127311983902126080', 
    '1127320431490367488', 
    '1127320700513087488', 
    '1127320941060698112', 
    '1127627836090593280', 
    '1127628155113627648', 
    '1127628421636497408', 
    '1127628613802758144', 
    '1127628823345991680', 
    '1127629014883041280', 
    '1127629219200221184', 
    '1127629396468277248', 
    '1127629571702091776', 
    '1127629772399456256', 
    '1127630307857006592', 
    '1127630509913296896', 
    '1131188813214248960', 
    '1131189247203053568', 
    '1131189607904813056', 
    '1131189850369273856', 
    '1131190226912858112', 
    '1131190465321123840', 
    '1131190678035271680', 
    '1131190923725221888', 
    '1131609815362621440', 
    '1131610154457165824', 
    '1131892079992414208', 
    '1132672171618217984', 
    '1134223442955550720',
    "1075126001023164416",
    "1051603386442850304",
    "1048238093331042304",
    "1076219332172095488",
    "1053143294668029952",
    "1048631053662920704",
    "1086037365413478400",
    "1049344212866576384",
    "1048538535227244544",
    "1049045384082980864",
    "1077351625959788544",
    "1070848563929825280",
    "1048364311787290624",
    "1051213152895045632",
    "1048210596396675072",
    "1066086639572795392",
    "1065679769796173824",
    "1050484015217627136",
    "1062567367819075584",
    "1050132283480522752",
    "1073663420957835264",
    "1048511690419064832",
    "1066442549130309632",
    "1075864670105399296",
    "1090714203226267648",
    "1101960833485221888",
    "1109910619613929472",
    "1127689977992757248",
    "1129857732640841728",
    "1132013019371802624",
    "1198377313197117440",
    "1109910972271075328",# IDP only
    ]

drafts_dir = "drafts"
picks_dir = "picks"

# Verzeichnisse erstellen, falls sie nicht existieren
os.makedirs(drafts_dir, exist_ok=True)
os.makedirs(picks_dir, exist_ok=True)

for league_id in league_ids:
    league = League(league_id)
    drafts = league.get_all_drafts()
    
    if drafts:
        draft_id = drafts[0]['draft_id']
        # draft_url = f'https://api.sleeper.app/v1/draft/{draft_id}'
        pick_url = f'https://api.sleeper.app/v1/draft/{draft_id}/picks'
        
        # draft_data = requests.get(draft_url).json()
        pick_data = requests.get(pick_url).json()
        
        # JSON-Dateien speichern
        # with open(f"{drafts_dir}/{draft_id}.json", "w", encoding="utf-8") as draft_file:
        #     json.dump(draft_data, draft_file, indent=4)
        
        with open(f"{picks_dir}/{draft_id}.json", "w", encoding="utf-8") as pick_file:
            json.dump(pick_data, pick_file, indent=4)
        
        print(f"Daten für Draft {draft_id} gespeichert.")
    else:
        print(f"Keine Drafts für League ID {league_id} gefunden.")

