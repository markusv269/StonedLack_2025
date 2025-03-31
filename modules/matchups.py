import pandas as pd
import os
import json

def get_matchups(weeks,id_list):
    matchups_df = pd.DataFrame()
    for league_id in id_list:
        for week in weeks:
            file_path = f"league_stats/matchups/{week}/{league_id}.json"
            
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    matchup_data = json.load(file)
                    
                    # Falls JSON-Daten eine Liste enthalten, direkt in DataFrame umwandeln
                    if isinstance(matchup_data, list):
                        temp_df = pd.DataFrame(matchup_data)
                    else:
                        temp_df = pd.DataFrame([matchup_data])
                    temp_df['week'] = week
                    temp_df['league_id'] = league_id
                    # DataFrame mergen
                    matchups_df = pd.concat([matchups_df, temp_df], ignore_index=True)
    return matchups_df