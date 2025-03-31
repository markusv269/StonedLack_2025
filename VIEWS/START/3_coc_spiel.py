import streamlit as st


st.image("Pictures/WC.jfif", width=500)
# Define dictionary for players in each position with their associated cost
wc_round = {
    "QB": {"Jackson": 5, "Daniels": 3, "Nix": 1, "Herbert": 0},
    "RB": {"Barkley": 5, "Williams": 3, "Irving": 1, "Mixon": 0},
    "WR": {"Jefferson": 5, "Nacua": 3, "Sutton": 1, "McMillan": 0},
    "TE": {"Andrews": 5, "Freiermuth": 3, "Kraft": 1, "Kincaid": 0}
}

# Create a form to display positions and select players
with st.form(key='wc_form'):
    name = st.text_input("Name des Champs (Discord- oder sleeper-Name)")
    # Select player for each position
    qb = st.selectbox("QB", list(wc_round["QB"].keys()))
    rb = st.selectbox("RB", list(wc_round["RB"].keys()))
    wr = st.selectbox("WR", list(wc_round["WR"].keys()))
    te = st.selectbox("TE", list(wc_round["TE"].keys()))
    
    # Submit button for the form
    submit_button = st.form_submit_button(label='Tippabgabe')


# Display the selections if the button is pressed and total cost is within budget
if submit_button:
    # Calculate the total cost dynamically
    total_cost = wc_round["QB"][qb] + wc_round["RB"][rb] + wc_round["WR"][wr] + wc_round["TE"][te]
    if total_cost <= 9:
        st.write(f"Deine Auswahl wurde bestätigt:")
        st.write(f"QB: {qb}, RB: {rb}, WR: {wr}, TE: {te}.")
    else:
        st.write("Die Kosten überschreiten das Limit von $9. Bitte wähle andere Spieler und sende deine Tipps erneut.")