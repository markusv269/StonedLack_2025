def position_color(pos):
    return {
        "QB": "#b26186",
        "RB": "#87c2a5",
        "WR": "#669dcb",
        "TE": "#c0914a",
        "K":  "#fbbc05",
        "DEF": "#ea4335",
        "DL": "#999999",
        "LB": "#999999",
        "DB": "#999999"
    }.get(pos.upper(), "#dddddd")

def player_box(name, team, position, color, round, pick_in_round, count):
    if count == 1:
        picks = f"{count} Pick"
    else:
        picks = f"{count} Picks"
    if len(list(name)) > 12:
        name = name[:6] + "..." 
    return f"""
    <div style="
        font-size: 1em;
        background-color: {color};
        padding: 2px;
        border-radius: 5px;
        margin: 2px;
        color: white;
        font-weight: bold;
        text-align: left;
        min-height: 90px;
    ">
        <div>{name}</div>
        <div style="font-size: 0.7em;">{round}.{pick_in_round}</div>
        <div style="font-size: 0.6em;">{picks}</div>
        <div style="font-size: 0.6em;">{team} • {position}</div>
    </div>
    """