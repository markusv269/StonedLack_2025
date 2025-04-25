import streamlit as st

st.write('''
## Community Mock Draft 2025
         
Der Community Mock Draft 2025 ist Geschichte. 
Für jedes Team wurden Mitglieder aus der Community aufgerufen, ihre Picks für die Franchise abzugeben.
Das Ergebnis der ersten Draftrunde gemäß der StonedLack-Community seht ihr im unten stehenden Bild.  

Mit dem in der Nacht von Donnerstag auf Freitag verlaufendem Draft der 2025er-Klasse wird sich zeigen, welche Picks der Realität entsprechen. 
''')

st.image("Pictures/pff_mock_results.png", width=500)

st.write('''Überraschungen sorgten vor allem die Picks, die klar auf Fantasy ausgelegt waren.
McMillan an #3, gepickt von Stonie, war sicherlich der erste Kracher.
Auch Matthew Golden an #8 sorgte für eine Überraschung und steht so sicherlich nicht auf vielen Draft Boards der Experten.
Dass ganze 7 Running Backs in der ersten Runde vom Board gehen, ist auch eher unwahrscheinlich und dem Fantasy-Blickwinkel der Community geschuldet.
Dennoch war es wieder ein großes Spektakel und ein riesen Spaß.  
''')

picks = {
        "TEN": {
            "name": "C. Ward",
            "pos": ["QB"],
            "marks": ":white_check_mark:"
        },
        "JAX": {
            "name": "T. Hunter",
            "pos": ["WR", "CB"],
            "marks": ":white_check_mark: :fire::fire::fire: :arrow_double_up: _CLE #5_"
        },
        "NYG": {
            "name": "A. Carter",
            "pos": ["ED"]
        },
        "NE": {
            "name": "W. Campbell",
            "pos": ["T"]
        }, 
        "CLE": {
            "name": "M. Graham",
            "pos" : ["DT"],
            "marks": ":white_check_mark: :arrow_double_down: _JAX #2_"
        },
        "LV": {
            "name": "A. Jeanty", 
            "pos": ["RB"], 
            "marks": ":white_check_mark: :fire::fire::fire:"
        },
        "NYJ": {
            "name": "A. Membou", 
            "pos": ["T"]
        },
        "CAR": {"name": "T. McMillan", "pos": ["WR"], "marks": ":fire:"},
        "NO": {"name": "K. Banks", "pos": ["T"]},
        "CHI": {"name": "C. Loveland", "pos": ["TE"], "marks": ":fire:"},
        "SF": {"name": "M. Williams", "pos": ["ED"]},
        "DAL": {"name": "T. Booker", "pos": ["G"]},
        "MIA": {"name": "K. Grant", "pos": ["DT"]},
        "IND": {"name": "T. Warren", "pos": ["TE"]},
        "ATL": {"name": "", "pos": []},
        "ARI": {"name": "", "pos": []},
        "CIN": {"name": "", "pos": []},
        "SEA": {"name": "", "pos": []},
        "TB": {"name": "", "pos": []},
        "DEN": {"name": "", "pos": []},
        "PIT": {"name": "", "pos": []},
        "LAC": {"name": "", "pos": []},
        "GB": {"name": "", "pos": []},
        "MIN": {"name": "", "pos": []},
        "HOU": {"name": "", "pos": []},
        "LAR": {"name": "", "pos": []},
        "BAL": {"name": "", "pos": []},
        "DET": {"name": "", "pos": []},
        "WAS": {"name": "", "pos": []},
        "BUF": {"name": "", "pos": []},
        "KC": {"name": "", "pos": []},
        "PHI": {"name": "", "pos": []},
}

def count_positions(picks):
    offense_positions = {"QB", "RB", "WR", "TE", "T", "G", "C"}
    defense_positions = {"DT", "ED", "CB", "S", "LB"}

    offense_count = 0
    defense_count = 0
    unknown_positions = set()

    for team, data in picks.items():
        positions = data.get("pos", [])
        if not positions or not isinstance(positions, list):
            continue
        for pos in positions:
            if pos in offense_positions:
                offense_count += 1
            elif pos in defense_positions:
                defense_count += 1
            else:
                unknown_positions.add(pos)

    return {
        "off": offense_count,
        "def": defense_count
    }

st.write("## NFL Draft 2025")
st.markdown('''
        Nachfolgend die NFL Draftpicks der ersten Runde im Draft 2025:  

        :white_check_mark:: richtiger Community Pick  
        :arrow_double_up:: traded up  
        :arrow_double_down:: traded down  
        :fire:: Fantasy Gold
                                    
        ---

        ''')
counter = count_positions(picks)
st.write(f"DEF-Players: {counter['def']}, OFF-Players: {counter['off']}")
for team, items in picks.items():
        st.write(f"**{team}:** {items['name']} ({'/'.join(items['pos'])}) {items.get('marks','')}")
        