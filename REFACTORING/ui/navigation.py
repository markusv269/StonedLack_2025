import streamlit as st

def create_navigation():
    """Navigation erstellen für st-link-navigation"""
    from st_link_navigation import Navigation as Nav, Page
    return Nav({
        "Start": [
            Page(page="VIEWS/START/0_start.py", title="Startseite", icon=":material/home:", default=True),
            Page(page="VIEWS/START/4_universe.py", title="Das StonedLack Universum", icon=":material/planet:"),
            Page(page="VIEWS/START/5_sleeper_ecke.py", title="sleeper.com-Ecke", icon=":material/bedtime:"),
        ],
        "Redraft allgemein": [
            Page(page="VIEWS/REDRAFT/RED_info.py", title="Die Redraftligen", icon=":material/home:"),
            Page(page="VIEWS/REDRAFT/RED_Manager.py", title="Manager", icon=":material/groups:"),
        ],
        "SLR Ligen 2025": [
            Page(page="VIEWS/REDRAFT/RED_drafts.py", title="Drafts", icon=":material/target:"),
            Page(page="VIEWS/REDRAFT/RED_adp_board.py", title="ADP Draftboard", icon=":material/table:"),
            Page(page="VIEWS/REDRAFT/RED_Matchups.py", title="Matchups", icon=":material/sports_football:"),
            Page(page="VIEWS/REDRAFT/RED_Wochenstatistiken.py", title="Wochenstatistiken", icon=":material/calendar_month:"),
            Page(page="VIEWS/REDRAFT/RED_Standings.py", title="Standings", icon=":material/leaderboard:"),
        ],
        "SL Dynastys": [
            Page(page="VIEWS/DYNASTY/DYN_drafts.py", title="Drafts 2025", icon=":material/target:"),
            Page(page="VIEWS/DYNASTY/DYN_adp_board.py", title="Dynasty Draftboard 2025", icon=":material/table:"),
            Page(page="VIEWS/DYNASTY/DYN_Matchups.py", title="Matchups 2025", icon=":material/sports_football:"),
            Page(page="VIEWS/DYNASTY/DYN_Standings.py", title="Standings 2025", icon=":material/leaderboard:"),
        ]
    })