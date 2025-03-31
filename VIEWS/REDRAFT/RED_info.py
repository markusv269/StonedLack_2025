import streamlit as st
import pandas as pd

st.write(
    '''
    # Die Stoned Lack Redraft Ligen 2024
    ## Settings
    ### Roster uns sonstige Einstellungen
    Die SLR Ligen werden mit 12 Managern gespielt. Jedes Team besteht aus 15 Spielern.
    Das Starting Lineup besteht aus

    - 1 Quarterback (QB),
    - 2 Running Backs (RB), 
    - 2 Wide Receiver (WR), 
    - 1 Tight End (TE),
    - 1 Flexposition (WR/RB),
    - 1 Kicker (K),
    - 1 Defense/Special Teams (DST).
    
    Jeder Manager erhält zu Beginn der Saison 100 $ FAAB (Waiver Budget). 
    Mit diesem Budget können über die Saison hinweg Spieler vom Waiver geholt werden.
    Dabei gilt das Prinzip einer versteckten Auktion. Der Manager, der am meisten auf einen Spieler gesetzt hat,
    bekommt den Spieler vom Waiver (vorausgesetzt er darf ihn erhalten).
    
    ## Scoring
    Das Scoring entspricht dem PPR-Scoring (1 Punkt je Reception) mit den üblichen Einstellungen. 
    Die gesamten Scoring-Settings können den nachfolgenden Tabellen entnommen werden''')

# Kategorien definieren
categories = {
    "Passing": ["pass_yd", "pass_td", "pass_2pt", "pass_int"],
    "Rushing": ["rush_yd", "rush_td", "rush_2pt"],
    "Receiving": ["rec_yd", "rec_td", "rec_2pt", "rec"],
    "Special Teams": ["st_td", "st_fum_rec", "st_ff", "kr_yd", "pr_yd"],
    "Defense": ["sack", "int", "ff", "fum_rec", "fum_rec_td", "def_td", "safe", "blk_kick", "def_st_ff", "def_st_fum_rec", "def_st_td"],
    "Kicking": ["fgm_0_19", "fgm_20_29", "fgm_30_39", "fgm_40_49", "fgm_50p", "fgmiss", "xpm", "xpmiss"],
}

# Beschreibungen der Stats
descriptions = {
    "pass_yd": "Passing Yards (pro Yard)",
    "pass_td": "Passing Touchdown",
    "pass_2pt": "2-Punkt-Conversion (Pass)",
    "pass_int": "Interception geworfen",
    "rush_yd": "Rushing Yards (pro Yard)",
    "rush_td": "Rushing Touchdown",
    "rush_2pt": "2-Punkt-Conversion (Rush)",
    "rec_yd": "Receiving Yards (pro Yard)",
    "rec_td": "Receiving Touchdown",
    "rec_2pt": "2-Punkt-Conversion (Receiving)",
    "rec": "Reception (gefangener Pass)",
    "st_td": "Special Teams Touchdown",
    "st_fum_rec": "Special Teams Fumble Recovery",
    "st_ff": "Special Teams Forced Fumble",
    "sack": "Quarterback Sack",
    "int": "Interception gefangen",
    "ff": "Forced Fumble",
    "fum_rec": "Fumble Recovery",
    "fum_rec_td": "Fumble Recovery Touchdown",
    "def_td": "Defensive Touchdown",
    "safe": "Safety",
    "blk_kick": "Blocked Kick",
    "def_st_ff": "Defense/Special Teams Forced Fumble",
    "def_st_fum_rec": "Defense/Special Teams Fumble Recovery",
    "def_st_td": "Defense/Special Teams Touchdown",
    "fgm_0_19": "Field Goal (0-19 Yards) verwandelt",
    "fgm_20_29": "Field Goal (20-29 Yards) verwandelt",
    "fgm_30_39": "Field Goal (30-39 Yards) verwandelt",
    "fgm_40_49": "Field Goal (40-49 Yards) verwandelt",
    "fgm_50p": "Field Goal (50+ Yards) verwandelt",
    "fgmiss": "Field Goal verschossen",
    "xpm": "Extra Punkt verwandelt",
    "xpmiss": "Extra Punkt verschossen",
    "pts_allow_0": "Gegnerische Punkte: 0",
    "pts_allow_1_6": "Gegnerische Punkte: 1-6",
    "pts_allow_7_13": "Gegnerische Punkte: 7-13",
    "pts_allow_14_20": "Gegnerische Punkte: 14-20",
    "pts_allow_21_27": "Gegnerische Punkte: 21-27",
    "pts_allow_28_34": "Gegnerische Punkte: 28-34",
    "pts_allow_35p": "Gegnerische Punkte: 35+",
}

# Daten für die Tabelle sammeln
for category, keys in categories.items():
    data = []
    for key in keys:
        if key in st.session_state["session_data"]["scoring"]:
            data.append({
                "Beschreibung": descriptions.get(key, "Keine Beschreibung verfügbar"),
                "Punkte": st.session_state["session_data"]["scoring"][key]
            })

    if data:
        df = pd.DataFrame(data)
        df["Punkte"] = df["Punkte"].astype("float")
        st.subheader(category)
        st.table(df.set_index("Beschreibung").style.format("{:.2}"))
