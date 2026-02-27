import streamlit as st
from config.constants import HEROES, TEAM_NAMES


def show_training_ui():
    st.title("Insert Training Data")

    name = st.selectbox("Your Name", TEAM_NAMES)
    own_team = st.multiselect(
        "Your Team (5 heroes)", HEROES, max_selections=5
    )

    siege = st.number_input("Siege", min_value=0, value=0)
    niederlagen = st.number_input("Niederlagen", min_value=0, value=0)

    enemy_team = st.multiselect(
        "Enemy Team (5 heroes)", HEROES, max_selections=5, key="enemy_training"
    )

    own_strength = st.number_input(
        "Your Team Strength (k)", min_value=0, value=0
    )
    enemy_strength = st.number_input(
        "Enemy Team Strength (k)", min_value=0, value=0
    )

    if st.button("Submit Training Data"):
        submitted = {
            "name": name,
            "own_team": own_team,
            "siege": siege,
            "niederlagen": niederlagen,
            "enemy_team": enemy_team,
            "own_strength": own_strength,
            "enemy_strength": enemy_strength,
        }
        st.write("Training data submitted:")
        st.write(submitted)
