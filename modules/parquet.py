import pandas as pd
import json
import os
import pyarrow.parquet as pq
import pyarrow as pa

actual_week = 17

slr_league_ids = ['1127181027346161664', 
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
                  '1134223442955550720']
weeks = list(range(1,actual_week + 1))

matchups_df = pd.DataFrame()
for league_id in slr_league_ids:
    for week in weeks:
        file_path = f"league_stats/rosters/{week}/{league_id}.json"
        
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

table = pa.Table.from_pandas(matchups_df)
pq.write_table(table, 'league_stats/rosters/rosters.parquet')
