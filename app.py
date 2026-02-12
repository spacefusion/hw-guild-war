import streamlit as st
import pandas as pd

st.set_page_config(page_title="Team Matcher", layout="wide")

st.title("Enemy Teams Input")

HEROES = sorted([
    "Ginger","Iris","Isaac","Julius","Fafnir","Nebula","Dante","Richter",
    "Octavia","Polaris","Martha","Oya","Hackebeil","Yasmine","Jhu",
    "Artemis","Corvus","Kayla","Tempus","Maya","Aidan","Arachne",
    "Tristan","Dunkler Stern","Orion","Folio","Morrigan","Champi und Gnon",
    "Kai","Cornelius","Satori","Luther","Jorgen","Astrid","Lillith",
    "Soleil","Gesichtsloser","Astaroth","Alvanor","Chabba","Karkh",
    "Elmir","Lian","Quing Mao","Rufus","Ziri","Keira","Dorian",
    "Galahad","Mojo","Phobos","Heidi","Thea","XeSha","Aurora",
    "Amira","Celeste","Sebastian","Kaskade","Peppy","Draufgänger",
    "Markus","Ishmael","Electra","Guus","Krista","Byrna",
    "Ninja Turtles","Helios","Lars","Fuchs","Andvari","Peech",
    "Somna","Lara Croft","Jet","Drayne"
])

num_teams = st.number_input(
    "Number of Enemy Teams",
    min_value=1,
    max_value=20,
    value=5
)

enemy_teams = []

for i in range(num_teams):
    st.subheader(f"Enemy Team {i+1}")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        team_name = st.text_input(
            "Team Name",
            key=f"name_{i}"
        )
    
    with col2:
        selected_heroes = st.multiselect(
            "Select 5 Heroes",
            HEROES,
            max_selections=5,
            key=f"heroes_{i}"
        )
    
    enemy_teams.append({
        "team_name": team_name,
        "heroes": selected_heroes
    })

if st.button("Calculate Matchups"):
    
    # Validation
    incomplete_teams = [
        t["team_name"] or f"Team {idx+1}"
        for idx, t in enumerate(enemy_teams)
        if len(t["heroes"]) != 5
    ]
    
    if incomplete_teams:
        st.error(
            "Each team must have exactly 5 heroes selected."
        )
    else:
        st.success("Input valid. Ready for matching logic.")
        st.write(enemy_teams)