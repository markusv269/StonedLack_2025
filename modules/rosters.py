import pandas as pd
import os
import json

def get_rosters(weeks,id_list):
    roster_df = pd.DataFrame()
    for league_id in id_list:
        for week in weeks:
            file_path = f"league_stats/rosters/{week}/{league_id}.json"
            
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    roster_data = json.load(file)
                    
                    # Falls JSON-Daten eine Liste enthalten, direkt in DataFrame umwandeln
                    if isinstance(roster_data, list):
                        temp_df = pd.DataFrame(roster_data)
                    else:
                        temp_df = pd.DataFrame([roster_data])
                    temp_df['week'] = week
                    temp_df['league_id'] = league_id
                    # DataFrame mergen
                    roster_df = pd.concat([roster_data, temp_df], ignore_index=True)
    return roster_df