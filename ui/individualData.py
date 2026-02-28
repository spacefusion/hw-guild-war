import streamlit as st
from config.constants import HEROES, TEAM_NAMES
from common.trainingDataLoader import load_training_data
import pandas as pd

def show_individual_ui():
    """Search MongoDB training data for a specific player/enemy combo."""

    st.title("Einzelnen Eintrag suchen")

    # load cached entries once per session
    entries = load_training_data()

    player = st.selectbox("Spielername", [""] + TEAM_NAMES)
    enemy_team = st.multiselect(
        "Gegnerisches Team (5 Helden)", HEROES, max_selections=5
    )
    enemy_strength = st.number_input("Gegnerische Stärke (k)", min_value=0, value=0)
    offset = st.number_input(
        "Erlaubter Stärkeunterschied (k)", min_value=0, value=0, step=1
    )

    if st.button("Suche starten"):
        # basic validation
        if player == "":
            st.error("Bitte wähle einen Spieler aus.")
            return
        if len(enemy_team) != 5:
            st.error("Das gegnerische Team muss genau 5 Helden enthalten.")
            return

        # normalize for matching
        normalized_enemy = sorted([h.lower() for h in enemy_team])
        max_allowed = enemy_strength + offset

        results = []
        for e in entries:
            if e.player.lower() != player.lower():
                continue
            if sorted([h.lower() for h in e.enemyTeam]) != normalized_enemy:
                continue
            if e.enemyStrength <= max_allowed:
                results.append(e)

        if results:
            st.success(f"{len(results)} Einträge gefunden")
            for r in results:
                # convert dataclass to a plain dict for nicer formatting
                try:
                    display = r.to_dict()
                except Exception:
                    display = r.__dict__
                # always hand prettify a list for consistency
                prettify_training_data([display])
        else:
            st.warning("Keine passenden Einträge in der Datenbank gefunden.")



def prettify_training_data(trainingData):
    # support a single dictionary as well as a list
    if isinstance(trainingData, dict):
        trainingData = [trainingData]

    for data in trainingData:
        player = data["player"]
        ownTeam = data["ownTeam"]
        ownStrength = data["ownStrength"]
        wins = data["wins"]
        losses = data["losses"]
        enemyTeam = ", ".join(data["enemyTeam"])
        enemyStrength = data["enemyStrength"]

        # Format powers with k and handle NaN
        enemyPowerStr = f"{int(enemyStrength)}k" if pd.notna(enemyStrength) else "?"
        playerPowerStr = f"{int(ownStrength)}k" if pd.notna(ownStrength) else "?"

        st.subheader(f"{player} [{playerPowerStr}] vs Gegner [{enemyPowerStr}]")
        st.write (f"Verwendetes Team: {ownTeam} ")
        st.write(f"Siege: {wins}, Niederlagen: {losses}")
        st.markdown("---")