import pandas as pd
import requests
import os

# Angenommen, dein DataFrame sieht so aus
player_list = ['7564', '9509', '4866', '6786', '6794', '9221', '7547', '4034', '3198', '9493', '11632', '12527', '7569', '11631', '9226', '8112', '11604', '5850', '5859', '11635', '9224', '11584', '6813', '4984', '8150', '3321', '8130', '4881', '9488', '12507', '6801', '8138', '4035', '8151', '11566', '4217', '8146', '11628', '2216', '2133', '5927', '8155', '6904', '12529', '4137', '7594', '5846', '10229', '5045', '4983', '8205', '12489', '12526', '5967', '6770', '4981', '7525', '11624', '6790', '5892', '9997', '8137', '7526', '4199', '10859', '8148', '12530', '12504', '8144', '6783', '5947', '5844', '2449', '11655', '7543', '12501', '4018', '11620', '12514', '1466', '11638', '8228', '5872', '8408', '9756', '9753', '6806', '12512', '4066', '8154', '4046', '4039', '7588', '12518', '8134', '11563', '5012', '4033', '12481', '7049', '5849', '12533', '4663', '9500', '4037', '11637', '12517', '4892', '6819', '12457', '12484', '7611', '10222', '4988', '9225', '1479', '9484', '11576', '8183', '11589', '10236', '4950', '8676', '7553', '6803', '8136', '7528', '3294', '8132', '12509', '7090', '11533', '9494', 'DEN', '11564', '1689', '9508', '11560', '7591', '8143', '12469', '12519', '3163', '6797', '8110', 'PHI', '12490', '11575', 'PIT', '12495', '5022', '12547', '7021', 'BAL', '8259', 'HOU', 'MIN', '11539', 'BUF', '1945', '6650']

# Ordner zum Speichern der Bilder
output_folder = 'images'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Basis-URL
base_url = "https://sleepercdn.com/content/nfl/players/thumb/"

# Schleife durch die DataFrame-Zeilen
for player_id in player_list:
    image_url = f"{base_url}{player_id}.jpg"
    image_path = os.path.join(output_folder, f"{player_id}.jpg")

    # Bild herunterladen und speichern
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_path, 'wb') as f:
                f.write(response.content)
            print(f"{player_id}.jpg erfolgreich heruntergeladen und gespeichert.")
        else:
            print(f"Fehler beim Herunterladen von {player_id}.jpg: Statuscode {response.status_code}")
    except Exception as e:
        print(f"Fehler beim Herunterladen von {player_id}.jpg: {e}")
