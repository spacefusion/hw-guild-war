import streamlit as st
from services.trainingDataService import TrainingDataService
from config.constants import HEROES, TEAM_NAMES


def show_training_ui():
    st.title("Trainingsdaten speichern")
    service = TrainingDataService()

    player = st.selectbox("Dein Name", TEAM_NAMES)
    ownTeam = st.multiselect("Dein Team (5 Helden)", HEROES, max_selections=5)
    ownStrength = st.number_input("Deine Stärke (k)", min_value=0, value=0)
    wins = st.number_input("Siege", min_value=0, value=0)
    losses = st.number_input("Niederlagen", min_value=0, value=0)

    enemyTeam = st.multiselect(
        "Gegnerisches Team (5 Helden)", HEROES, max_selections=5, key="enemy_training"
    )

    enemyStrength = st.number_input("Gegnerische Stärke (k)", min_value=0, value=0)

    if st.button("Daten absenden"):
        if len(ownTeam) != 5 or len(enemyTeam) != 5:
            st.error("Beide Teams müssen genau 5 Helden enthalten.")
            return

        insertedEntry = service.save_training_data(
            player=player,
            ownTeam=ownTeam,
            ownStrength=ownStrength,
            wins=wins,
            losses=losses,
            enemyTeam=enemyTeam,
            enemyStrength=enemyStrength,
        )

        st.success("Daten erfolgreich gespeichert")
        st.write(f"Eintrag: {insertedEntry}")
