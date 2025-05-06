from sleeper_wrapper import League

DYNLEAGUES = [
        "1075126001023164416", # Stoned Lack Dynastie #1
        "1051603386442850304", # SLL 2 Dynasty
        "1048238093331042304", # Stoned Lack Dynastie 3
        "1076219332172095488", # SLA DYNASTY 4
        "1053143294668029952", # STONED LACK DYNASTY 5
        "1181844911174176768", # Stoned Lack Dynasty 5 (2025)
        "1048631053662920704", # StonedLack Dynasty Liga 6 🔥🔥🔥
        "1086037365413478400", # Stoned Lack Dynasty 7
        "1049344212866576384", # SLL 8 DYNASTY
        "1048538535227244544", # Stoned Lack Dynasty League #9 (Let's Go!)
        "1049045384082980864", # Stoned Lack Dynasty 10
        "1077351625959788544", # SSL 11 IDP Dynasty
        "1070848563929825280", # SLL 12 IDP Dynasty 
        "1048364311787290624", # STONED LACK DYNASTY 13 IDP
        "1051213152895045632", # SLL 14 Dynasty
        "1048210596396675072", # SLL15
        "1066086639572795392", # SLL #16 Dynasty
        "1065679769796173824", # Sons of Rivers #SLL17
        "1050484015217627136", # Stoned Lack Dynasty 18
        "1062567367819075584", # SLL #19 Dynasty
        "1050132283480522752", # Stoned Lack Dynastie #20 
        "1073663420957835264", # Stoned Lack Dynasty 21
        "1048511690419064832", # Stoned Lack Dynasty 22
        "1066442549130309632", # Stoned Lack Dynasty 23
        "1194741490742648832", # Stoned Lack Dynasty 24
        "1075864670105399296", # Stoned Lack Dynasty 24
        "1090714203226267648", # Stoned Lack Dynasty 25
        "1101960833485221888", # Stoned Lack Dynasty 26
        "1109910619613929472", # Stoned Lack Dynasty 27
        "1127689977992757248", # Stoned Lack Dynasty 28
        "1129857732640841728", # Stoned Lack Dynasty 29
        "1132013019371802624", # Stoned Lack Dynasty 30
        "1198377313197117440", # Stoned Lack Dynasty 31
        "1109910972271075328", # Stoned Lack Dynasty IDP Only
        "1207100721535655936", # Stoned Lack Dynasty 32
        "1208531949958742016", # Stoned Lack  IDP Dynasty 33
        "1222678226208296960", # Stoned Lack Dynasty 34
    ] 

for league_id in DYNLEAGUES:
    league = League(league_id)
    league_data = league.get_league()
    print(f"\"{league_id}\", # {league_data['name']}")