import streamlit as st

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

def metric_box(label, value):
    st.markdown(
        f"""
        <style>
        /* Standard (Lightmode) */
        .metric-box .label {{
            color: #333; /* dunkelgrau */
            font-size: 10px;
        }}
        .metric-box .value {{
            color: #000; /* schwarz */
            font-size: 14px;
            font-weight: bold;
        }}

        /* Darkmode */
        [data-theme="dark"] .metric-box .label {{
            color: #aaa; /* hellgrau */
        }}
        [data-theme="dark"] .metric-box .value {{
            color: #ccc; /* etwas helleres Grau */
        }}

        .metric-box {{
            text-align: center;
            padding: 0.5rem;
        }}
        </style>
        <div class="metric-box">
            <div class="label">{label}</div>  
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )