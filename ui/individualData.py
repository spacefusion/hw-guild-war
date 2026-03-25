import streamlit as st
from config.constants import HEROES, TEAM_NAMES
from common.trainingDataLoader import load_training_data
from services.trainingDataService import TrainingDataService
import pandas as pd

def show_individual_ui():
    """Search MongoDB training data for a specific player/enemy combo."""

    st.title("Einzelnen Eintrag suchen")

    # load cached entries once per session
    trainingDataList = load_training_data()

    player = st.selectbox("Spielername", [""] + TEAM_NAMES)
    enemy_team = st.multiselect(
        "Gegnerisches Team (5 Helden)", HEROES, max_selections=5
    )
    enemy_strength = st.number_input("Gegnerische Stärke (k)", min_value=0, value=0)
    offset = st.number_input(
        "Erlaubter Stärkeunterschied (k)", min_value=0, value=5, step=1
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

        results = []
        for trainingData in trainingDataList:
            if trainingData.player.lower() != player.lower():
                continue
            if sorted([h.lower() for h in trainingData.enemyTeam]) != normalized_enemy:
                continue
            if enemy_strength <= trainingData.enemyStrength + offset:
                results.append(trainingData)

        # persist results so they survive reruns triggered by the edit buttons
        st.session_state["search_results"] = [
            r.to_dict() if hasattr(r, "to_dict") else r.__dict__ for r in results
        ]
        st.session_state["search_enemy_strength"] = enemy_strength

    # always render from session state so results survive button-click reruns
    search_results = st.session_state.get("search_results")
    if search_results is not None:
        if search_results:
            st.success(f"{len(search_results)} Einträge gefunden")
            for display in search_results:
                prettify_training_data([display], st.session_state["search_enemy_strength"])
        else:
            st.warning("Keine passenden Einträge in der Datenbank gefunden.")



def prettify_training_data(trainingData, currentEnemyStrength):
    # support a single dictionary as well as a list
    if isinstance(trainingData, dict):
        trainingData = [trainingData]

    for data in trainingData:
        player = data["player"]
        ownTeam = data["ownTeam"]
        ownStrength = data["ownStrength"]
        wins = data["wins"]
        losses = data["losses"]
        enemyStrength = data["enemyStrength"]
        entry_id = data.get("_id", "")

        # Format powers with k and handle NaN
        enemyPowerStr = f"{int(enemyStrength)}k" if pd.notna(enemyStrength) else "?"
        playerPowerStr = f"{int(ownStrength)}k" if pd.notna(ownStrength) else "?"

        st.subheader(f"{player} [{playerPowerStr}] vs Gegner [{enemyPowerStr}]")
        st.write (f"Verwendetes Team: {ownTeam} ")
        st.write(f"Siege: {wins}, Niederlagen: {losses}")

        strengthDifference =enemyStrength-currentEnemyStrength
        if(strengthDifference<0):
            st.write(f"Derzeitiger Gegner ist {strengthDifference*-1}k stärker als in den Trainingsdaten!")
        elif(strengthDifference>0):
            st.write(f"Derzeitiger Gegner ist {strengthDifference}k schwächer als in den Trainingsdaten!")
        else:
            st.write(f"Derzeitiger Gegner ist gleich stark wie in den Trainingsdaten!")

        if entry_id:
            edit_key = f"edit_open_{entry_id}"
            if st.button("Bearbeiten", key=f"btn_edit_{entry_id}"):
                st.session_state[edit_key] = not st.session_state.get(edit_key, False)

            if st.session_state.get(edit_key, False):
                with st.form(key=f"form_edit_{entry_id}"):
                    new_wins = st.number_input("Siege", value=int(wins), min_value=0)
                    new_losses = st.number_input("Niederlagen", value=int(losses), min_value=0)
                    new_enemy_strength = st.number_input("Gegnerische Stärke (k)", value=int(enemyStrength), min_value=0)
                    new_own_strength = st.number_input("Eigene Stärke (k)", value=int(ownStrength), min_value=0)
                    if st.form_submit_button("Speichern"):
                        service = TrainingDataService()
                        service.update_training_data(
                            entry_id, new_wins, new_losses, new_enemy_strength, new_own_strength
                        )
                        load_training_data.clear()
                        # update the cached display dict so the re-render shows fresh values
                        for sr in st.session_state.get("search_results", []):
                            if sr.get("_id") == entry_id:
                                sr["wins"] = new_wins
                                sr["losses"] = new_losses
                                sr["enemyStrength"] = new_enemy_strength
                                sr["ownStrength"] = new_own_strength
                                break
                        st.session_state[edit_key] = False
                        st.success("Eintrag aktualisiert!")
                        st.rerun()

        st.markdown("---")
