import csv
import json

# Datei-Pfad anpassen
csv_datei = "coc.csv"

# Dictionary erstellen
data_dict = {"WC": {}, "DR": {}, "CF": {}, "SB": {}}

# CSV-Datei einlesen und in das Dictionary umwandeln
with open(csv_datei, mode="r", encoding="utf-8") as file:
    reader = csv.reader(file)  # Falls Tab als Trennzeichen

    for row in reader:
        name = row[0]  # Spielername als Key im Dictionary
        data_dict["WC"][name] = {"QB": row[1], "RB": row[2], "WR": row[3], "TE": row[4]}
        data_dict["DR"][name] = {"QB": row[5], "RB": row[6], "WR": row[7], "TE": row[8]}
        data_dict["CF"][name] = {"QB": row[9], "RB": row[10], "WR": row[11], "TE": row[12]}
        data_dict["SB"][name] = {"Player1": row[13], "Player2": row[14], "Player3": row[15]}

print(data_dict)