def position_color(pos):
    return {
        "QB": "#b26186",
        "RB": "#87c2a5",
        "WR": "#669dcb",
        "TE": "#c0914a",
        "K":  "#af3fc5",
        "DEF": "#a1481f",
        "DL": "#999999",
        "LB": "#999999",
        "DB": "#999999"
    }.get(pos.upper(), "#dddddd")

def player_box(name, team, position, color, round, pick_in_round, count):
    picks = f"Ø {count}"
    if len(list(name)) > 20:
        name = name[:15] + "..." 
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