import streamlit as st
from config.constants import HEROES, TEAM_NAMES


def show_training_ui():
    st.title("Trainingsdaten speichern")

    name = st.selectbox("Dein Name", TEAM_NAMES)
    own_team = st.multiselect(
        "Dein Team (5 Helden)", HEROES, max_selections=5
    )
    own_strength = st.number_input(
        "Deine Stärke (k)", min_value=0, value=0
    )
    siege = st.number_input("Siege", min_value=0, value=0)
    niederlagen = st.number_input("Niederlagen", min_value=0, value=0)

    enemy_team = st.multiselect(
        "Gegnerisches Team (5 Helden)", HEROES, max_selections=5, key="enemy_training"
    )

    enemy_strength = st.number_input(
        "Gegnerische Stärke (k)", min_value=0, value=0
    )

    if st.button("Daten absenden"):
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
