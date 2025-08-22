import requests
import pandas as pd

DYNLEAGUES_2025 = [ # 2025
    "1209233140317425664", # Stoned Lack Dynastie #1
    "1180230346197667840", # SLL 2 Dynasty
    "1195778937733513216", # Stoned Lack Dynastie 3
    "1209607849928302592", # SLA DYNASTY 4
    "1181844911174176768", # STONED LACK DYNASTY 5
    "1180582953490542592", # StonedLack Dynasty Liga 6 🔥🔥🔥
    "1181536975269736448", # Stoned Lack Dynasty 7
    "1180311821918916608", # SLL 8 DYNASTY
    "1180603162834702336", # Stoned Lack Dynasty League #9 (Let's Go!)
    "1187105219732697088", # Stoned Lack Dynasty 10
    "1182287035210129408", # SSL 11 IDP Dynasty
    "1206707252904333312", # SLL 12 IDP Dynasty 
    "1182673834217238528", # STONED LACK DYNASTY 13 IDP
    "1210606508199383040", # SLL 14 Dynasty
    "1194726230783582208", # SLL15
    "1204157997916360704", # SLL #16 Dynasty
    "1182681844257095680", # Sons of Rivers #SLL17
    "1198654756378132480", # Stoned Lack Dynasty 18
    "1184247769674326016", # SLL #19 Dynasty
    "1186799276489707520", # Stoned Lack Dynastie #20 
    "1206997313344520192", # Stoned Lack Dynasty 21
    "1186321340412182528", # Stoned Lack Dynasty 22
    "1204822524987195392", # Stoned Lack Dynasty 23
    "1194741490742648832", # Stoned Lack Dynasty 24
    "1183111980349202432", # Stoned Lack Dynasty 25
    "1196774145552044032", # Stoned Lack Dynasty 26
    "1180590776307220480", # Stoned Lack Dynasty 27
    "1180196379875319808", # Stoned Lack Dynasty 28
    "1205588222306947072", # Stoned Lack Dynasty 29
    "1207817141764493312", # Stoned Lack Dynasty 30
    "1198377313197117440", # Stoned Lack Dynasty 31
    "1207100721535655936", # Stoned Lack Dynasty 32
    "1208531949958742016", # Stoned Lack IDP Dynasty 33
    "1222678226208296960", # Stoned Lack Dynasty 34
    "1225880660946718720", # Stoned Lack Dynasty 35
    "1225905709284085760", # Stoned Lack Dynasty 36 IDP
    "1227032788637601792", # Stoned Lack Dynasty 37
    "1229353710618939392", # Stoned Lack Dynasty 38
    "1240076840060600320", # Stoned Lack Dynasty 39 IDP
    "1231019902408601601", # Stoned Lack Dynasty 40
    "1238115967473553408", # Stoned Lack Dynasty 41
    "1250933984330780672", # Stoned Lack Dynasty 42
    "1255594465335185408", # Stoned Lack Dynasty 43
    "1257891475950161920", # Stoned Lack IDP Dynasty 44
    "1257833708308676608", # Stoned Lack Dynasty 45
    "1259259629091684352", # Stoned Lack Dynasty 46
    "1201660025227976704", # Stoned Lack Dynasty IDP Only
    "1196950328071704576", # Stoned Lack Bestball Dynasty
    "1227724436963069952", # Stoned Lack Bestball Dynasty 2
    "1228114533256544256", # Stoned Lack Bestball Dynasty 3
    "1250931611524927488", # Stoned Lack Bestball Dynasty 4
]

DYNLEAGUES_2024 = [
        "1075126001023164416", # Stoned Lack Dynastie #1
        "1051603386442850304", # SLL 2 Dynasty
        "1048238093331042304", # Stoned Lack Dynastie 3
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
        "1194741490742648832", # Stoned Lack Dynasty 24
        "1075864670105399296",
        "1090714203226267648",
        "1101960833485221888",
        "1109910619613929472",
        "1127689977992757248",
        "1129857732640841728",
        "1132013019371802624",
        "1198377313197117440",
        "1109910972271075328",# IDP only
        "1207100721535655936",# Stoned Lack Dynasty 32
        "1208531949958742016",# Stoned Lack Dynasty IDP 33
        "1222678226208296960", # Stoned Lack Dynasty 34
    ]     

REDLEAGUES = [ # 2024
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
        # '1127628155113627648', # aufgelöst
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
        '1134223442955550720'
    ]

SCORINGSETTINGS = {
        "sack": 1,
        "fgm_40_49": 4,
        "pass_int": -1,
        "pts_allow_0": 10,
        "pass_2pt": 2,
        "st_td": 6,
        "rec_td": 6,
        "fgm_30_39": 3,
        "xpmiss": -1,
        "rush_td": 6,
        "rec_2pt": 2,
        "st_fum_rec": 1,
        "fgmiss": -1,
        "ff": 1,
        "rec": 1,
        "pts_allow_14_20": 1,
        "fgm_0_19": 3,
        "int": 2,
        "def_st_fum_rec": 1,
        "fum_lost": -2,
        "pts_allow_1_6": 7,
        "kr_yd": 0,
        "fgm_20_29": 3,
        "pts_allow_21_27": 0,
        "xpm": 1,
        "rush_2pt": 2,
        "fum_rec": 2,
        "def_st_td": 6,
        "fgm_50p": 5,
        "def_td": 6,
        "safe": 2,
        "pass_yd": 0.04,
        "blk_kick": 2,
        "pass_td": 4,
        "rush_yd": 0.1,
        "pr_yd": 0,
        "fum": -1,
        "pts_allow_28_34": -1,
        "pts_allow_35p": -4,
        "fum_rec_td": 6,
        "rec_yd": 0.1,
        "def_st_ff": 1,
        "pts_allow_7_13": 4,
        "st_ff": 1
    }


mockdrafts_2025_discord = [
    "1247655959350747136",
    "1248963110648168448",
    "1248997420017135616",
    "1249452643655352320",
    "1249821406087090176",
    "1250153170227712000",
    "1250167538738802688",
    "1250217184701984768",
    "1250799312997195776",
    "1250854682419544064",
]

mockdrafts_2025_stream = [
    "1250593319285702656", #514
    "1248025402572537856", #513
    "1245492771041595392", #512
]


REDLEAGUES_2025 = {
    '1259474814326804480': {'invitelink': 'https://sleeper.com/i/zE10M78gmGPxq', 'name': 'SLR2025 - Liga 50'},
    '1259474730402983936': {'invitelink': 'https://sleeper.com/i/zE10M7jD17bkX', 'name': 'SLR2025 - Liga 49'},
    '1259474649956229120': {'invitelink': 'https://sleeper.com/i/E8oVn0qNeVGA3', 'name': 'SLR2025 - Liga 48'},
    '1259474519244935168': {'invitelink': 'https://sleeper.com/i/m78PXKX5Bd5E5', 'name': 'SLR2025 - Liga 47'},
    '1259474432758398976': {'invitelink': 'https://sleeper.com/i/0NL6nX6aYdknW', 'name': 'SLR2025 - Liga 46'},
    '1259474320795652096': {'invitelink': 'https://sleeper.com/i/LV9YBna4RwYkm', 'name': 'SLR2025 - Liga 45'}, 
    '1259474226784518144': {'invitelink': 'https://sleeper.com/i/Y2GY7xAMj8B6R', 'name': 'SLR2025 - Liga 44'}, 
    '1259474146023182336': {'invitelink': 'https://sleeper.com/i/zE10MeQ0W4mwB', 'name': 'SLR2025 - Liga 43'}, 
    '1259456880581812224': {'invitelink': 'https://sleeper.com/i/m78PMql9wl29G', 'name': 'SLR2025 - Liga 42'}, 
    '1259456793621307392': {'invitelink': 'https://sleeper.com/i/j7Oj2BOnggaaV', 'name': 'SLR2025 - Liga 41'}, 
    '1259456679792103424': {'invitelink': 'https://sleeper.com/i/m78PMw2bnzkww', 'name': 'SLR2025 - Liga 40'}, 
    '1259456554017492992': {'invitelink': 'https://sleeper.com/i/j7Oj2wjLoV5n0', 'name': 'SLR2025 - Liga 39'}, 
    '1259456415743877120': {'invitelink': 'https://sleeper.com/i/E8oV4MxxQn0QG', 'name': 'SLR2025 - Liga 38'}, 
    '1259456303575609344': {'invitelink': 'https://sleeper.com/i/Y2GYNPL97qmQW', 'name': 'SLR2025 - Liga 37'}, 
    '1253003762222497792': {'invitelink': 'https://sleeper.com/i/j7Ogm79mPxjDV', 'name': 'SLR2025 - Liga 36'}, 
    '1253003689942061056': {'invitelink': 'https://sleeper.com/i/kM8n2MRmPAMWk', 'name': 'SLR2025 - Liga 35'}, 
    '1253003588548968448': {'invitelink': 'https://sleeper.com/i/j7Ogm7ooAQ9Xw', 'name': 'SLR2025 - Liga 34'}, 
    '1253003494361677824': {'invitelink': 'https://sleeper.com/i/m78jogOzxLx83', 'name': 'SLR2025 - Liga 33'}, 
    '1253003422249005056': {'invitelink': 'https://sleeper.com/i/kM8n2zjWGa3j7', 'name': 'SLR2025 - Liga 32'}, 
    '1253002628053356544': {'invitelink': 'https://sleeper.com/i/Y2G5Rk8OMZ7xj', 'name': 'SLR2025 - Liga 31'}, 
    '1253002535396982784': {'invitelink': 'https://sleeper.com/i/QB2GJmk2qKwZP', 'name': 'SLR2025 - Liga 30'}, 
    '1253002452240703488': {'invitelink': 'https://sleeper.com/i/Y2G5R0xwDLXOD', 'name': 'SLR2025 - Liga 29'}, 
    '1253001282537394176': {'invitelink': 'https://sleeper.com/i/0NLGQD1JZRdxX', 'name': 'SLR2025 - Liga 28'}, 
    '1253001211578171392': {'invitelink': 'https://sleeper.com/i/j7OgXl9DBmVO0', 'name': 'SLR2025 - Liga 27'}, 
    '1253001133438291968': {'invitelink': 'https://sleeper.com/i/m78jGnWnXdYGw', 'name': 'SLR2025 - Liga 26'}, 
    '1253001055621349376': {'invitelink': 'https://sleeper.com/i/0NLGQDjPm7g92', 'name': 'SLR2025 - Liga 25'}, 
    '1253000976617439232': {'invitelink': 'https://sleeper.com/i/0NLGQDbYZQl75', 'name': 'SLR2025 - Liga 24'}, 
    '1253000893956100096': {'invitelink': 'https://sleeper.com/i/LV96Om3xGQ8mX', 'name': 'SLR2025 - Liga 23'}, 
    '1253000818538323968': {'invitelink': 'https://sleeper.com/i/m78jGeRxob79e', 'name': 'SLR2025 - Liga 22'}, 
    '1253000733360402432': {'invitelink': 'https://sleeper.com/i/0NLGQaYmOMJXw', 'name': 'SLR2025 - Liga 21'}, 
    '1253000648966819840': {'invitelink': 'https://sleeper.com/i/QB2GJKxGkb5J3', 'name': 'SLR2025 - Liga 20'}, 
    '1253000445379477504': {'invitelink': 'https://sleeper.com/i/j7OgXaq7BZEGW', 'name': 'SLR2025 - Liga 19'}, 
    '1253000346901417984': {'invitelink': 'https://sleeper.com/i/QB2GJKBNXLOzE', 'name': 'SLR2025 - Liga 18'}, 
    '1253000245189541888': {'invitelink': 'https://sleeper.com/i/Y2G5RoZMJ7zLa', 'name': 'SLR2025 - Liga 17'}, 
    '1253000171831173120': {'invitelink': 'https://sleeper.com/i/E8oRWPz1dZwaw', 'name': 'SLR2025 - Liga 16'}, 
    '1253000079652954112': {'invitelink': 'https://sleeper.com/i/kM8nK9GB58BLx', 'name': 'SLR2025 - Liga 15'}, 
    '1252999351161069568': {'invitelink': 'https://sleeper.com/i/m78jG23dqQqbY', 'name': 'SLR2025 - Liga 14'}, 
    '1252998690872758272': {'invitelink': 'https://sleeper.com/i/V9EPGAB7aDnW6', 'name': 'SLR2025 - Liga 13'}, 
    '1252998625206730752': {'invitelink': 'https://sleeper.com/i/LV96OA0bLeDB8', 'name': 'SLR2025 - Liga 12'}, 
    '1252998547037507584': {'invitelink': 'https://sleeper.com/i/QB2GJAWZ1xAl0', 'name': 'SLR2025 - Liga 11'}, 
    '1252998484617863168': {'invitelink': 'https://sleeper.com/i/m78jGBEa0Ponx', 'name': 'SLR2025 - Liga 10'}, 
    '1252998313972604928': {'invitelink': 'https://sleeper.com/i/V9EPG0A4Wm4n6', 'name': 'SLR2025 - Liga 9'},
    '1252998212189425664': {'invitelink': 'https://sleeper.com/i/E8oRW0ML8Bm50', 'name': 'SLR2025 - Liga 8'}, 
    '1252998131948204032': {'invitelink': 'https://sleeper.com/i/0NLGQXQlz2JmX', 'name': 'SLR2025 - Liga 7'}, 
    '1252998048309592064': {'invitelink': 'https://sleeper.com/i/E8oRWgwd11j13', 'name': 'SLR2025 - Liga 6'}, 
    '1252997844055371776': {'invitelink': 'https://sleeper.com/i/0NLGQOR83DkAw', 'name': 'SLR2025 - Liga 5'}, 
    '1252997476521099264': {'invitelink': 'https://sleeper.com/i/E8oRW28YjkRJQ', 'name': 'SLR2025 - Liga 4'}, 
    '1252997374859563008': {'invitelink': 'https://sleeper.com/i/LV96OBeQ3GLXX', 'name': 'SLR2025 - Liga 3'}, 
    '1252997295608180736': {'invitelink': 'https://sleeper.com/i/zE1YbMqZ9nwEq', 'name': 'SLR2025 - Liga 2'}, 
    '1252997207154491392': {'invitelink': 'https://sleeper.com/i/j7OgXAo1Kqd08', 'name': 'SLR2025 - Liga 1'}
}