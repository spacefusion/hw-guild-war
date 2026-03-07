import streamlit as st
from services.trainingDataService import TrainingDataService
from config.constants import HEROES, TEAM_NAMES
from common.trainingDataLoader import load_training_data, load_existing_player_teams


def show_training_ui():
    st.title("Trainingsdaten speichern")
    service = TrainingDataService()

    player = st.selectbox("Dein Name", [""] + TEAM_NAMES)

    # when player changes we might need to reset the aggregated team selection
    if player != st.session_state.get("_last_player"):
        st.session_state.pop("aggregated_choice", None)
        # also clear any previously filled team/strength so user can pick new values
        st.session_state.pop("ownTeam", None)
        st.session_state.pop("ownStrength", None)
        st.session_state.pop("_last_aggregated_choice", None)
        st.session_state["_last_player"] = player

    # load aggregated teams for this player and let user pick one to pre-fill values
    if player:
        aggregated_list = load_existing_player_teams(player)
        if aggregated_list:
            options = [""] + [
                f"{', '.join(t.ownTeam)} (max {t.maxOwnStrength}k)"
                for t in aggregated_list
            ]
            aggregated_choice = st.selectbox(
                "Vorhandenes Team wählen", options, key="aggregated_choice"
            )
            # only prefill values if the aggregated choice has changed, 
            # so that we are still able to change the ownStrength and ownTeam inputs without them being overridden by the aggregated team selection on every rerun
            if aggregated_choice and aggregated_choice != st.session_state.get("_last_aggregated_choice"):
                idx = options.index(aggregated_choice) - 1
                selected = aggregated_list[idx]
                # update the session state so the following inputs show these values
                st.session_state["ownTeam"] = selected.ownTeam
                st.session_state["ownStrength"] = selected.maxOwnStrength
                st.session_state["_last_aggregated_choice"] = aggregated_choice
            elif not aggregated_choice:
                # if choice is cleared, track that change too
                st.session_state["_last_aggregated_choice"] = aggregated_choice

    # user-specified team and strength (possibly overridden above)
    ownTeam = st.multiselect(
        "Dein Team (5 Helden)", HEROES, max_selections=5, key="ownTeam"
    )
    # the value is managed via session state (could be set by aggregated team selection)
    ownStrength = st.number_input(
        "Deine Stärke (k)", min_value=0, key="ownStrength"
    )
    wins = st.number_input("Siege", min_value=0, value=1)
    losses = st.number_input("Niederlagen", min_value=0, value=0)

    enemyTeam = st.multiselect(
        "Gegnerisches Team (5 Helden)", HEROES, max_selections=5, key="enemy_training"
    )

    enemyStrength = st.number_input("Gegnerische Stärke (k)", min_value=0, value=0)

    def teams_equal(t1: list, t2: list) -> bool:
        # compare as unordered sets so [A,B,...] equals [B,A,...]
        return set(t1) == set(t2)

    def perform_save() -> None:
        """Helper that actually writes the entry to the database."""
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
        load_training_data.clear()
        load_existing_player_teams.clear()
        st.session_state.pop("pending_duplicate", None)

    # handle first submission
    if st.button("Daten absenden"):
        if len(ownTeam) != 5 or len(enemyTeam) != 5:
            st.error("Beide Teams müssen genau 5 Helden enthalten.")
            return
        if player == "":
            st.error("Spielername muss eingegeben werden!")
            return

        existing = load_training_data()
        similar = [
            e for e in existing
            if e.player == player and teams_equal(e.enemyTeam, enemyTeam)
        ]
        if similar:
            # record that we're waiting for confirmation and show warning
            st.session_state["pending_duplicate"] = True
            st.warning(
                f"Es gibt bereits {len(similar)} Einträge für dich mit diesem Gegnerteam."
            )
            for e in similar[:4]:
                st.write(
                    f"Eigene Stärke:{e.ownStrength} | GegnerStärke: {e.enemyStrength} | Siege: {e.wins} |Niederlagen: {e.losses} |Siegesteam: {e.ownTeam}"
                )
            # do not save yet, wait for explicit confirmation
        else:
            perform_save()

    # if user previously hit submit and duplicates were found, show confirm button
    if st.session_state.get("pending_duplicate"):
        if st.button("Trotzdem speichern", key="confirm_button"):
            perform_save()
