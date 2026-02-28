import streamlit as st
import pandas as pd  # still needed for template CSV parsing
from services.greedyMatchmaking import greedy_matchmaking
from services.trainingDataService import TrainingDataService
from models.trainingDataEntry import TrainingDataEntry
from config.constants import GK_POSITIONS, HEROES
from common.trainingDataLoader import load_training_data

def prettify_assignments(assignments):
    """Render the results returned by :func:`greedy_matchmaking`.
    The new assignment structure contains the original training entry along
    with the building position (previously ``enemy_team``) and the strength
    that was searched for.
    """
    for assign in assignments:
        building = assign.get("buildingPosition")
        searched_power = assign.get("searchedEnemyStrength", 0)
        entry = assign["entry"] 

        enemyTeam = ", ".join(entry.enemyTeam)
        enemyStrength = entry.enemyStrength

        player = entry.player
        playerStrength = entry.ownStrength
        ownTeam = ", ".join(entry.ownTeam)

        # Format powers with k and handle NaN
        enemyStrengthString = f"{int(enemyStrength)}k" if pd.notna(enemyStrength) else "?"
        searchedStrengthString = f"{int(searched_power)}k" if pd.notna(searched_power) else "?"
        playerStrengthString = f"{int(playerStrength)}k" if pd.notna(playerStrength) else "?"

        st.subheader(f"{building} ({searchedStrengthString})")
        st.write(f"Gegner:({enemyStrengthString}) {enemyTeam}")
        st.write(f"Sieger laut Trainingsdaten:")
        st.markdown(
            f"<span style='color:green'>{player} ({playerStrengthString}) : </span>"
            f"<span style='color:green'>{ownTeam}</span>",
            unsafe_allow_html=True,
        )
        st.markdown("---")


@st.cache_data
def load_templates():
    df = pd.read_csv("templates.csv")

    df["Power"] = pd.to_numeric(df["Power"], errors="coerce").fillna(0)

    hero_cols = ["Enemy 1", "Enemy 2", "Enemy 3", "Enemy 4", "Enemy 5"]

    df["Guild"] = df["Guild"].astype(str).str.strip()

    df["enemy_team"] = df[hero_cols].apply(
        lambda row: [h for h in row if pd.notna(h)], axis=1
    )

    return df


def show_matchmaking_ui():
    templates_df = load_templates()

    guilds = sorted(templates_df["Guild"].dropna().unique())

    selected_guild = st.selectbox(
        "Wähle eine Beispiel Gilde aus", options=["Leer"] + guilds, index=0
    )
    prefill_clicked = st.button("Mit Alianzdaten befüllen")

    st.title("Gegnerische Teams")

    if prefill_clicked:

        if selected_guild == "Leer":
            # Remove only relevant keys
            keys_to_delete = [
                key
                for key in st.session_state.keys()
                if key.startswith(("name_", "power_", "heroes_"))
            ]

            for key in keys_to_delete:
                del st.session_state[key]

            st.rerun()

        else:
            guild_templates = templates_df[templates_df["Guild"] == selected_guild]

            prefill_teams = []

            for _, row in guild_templates.iterrows():
                prefill_teams.append(
                    {
                        "team_name": row["Building"],
                        "heroes": row["enemy_team"],
                        "power": row["Power"],
                    }
                )

            # IMPORTANT: store template size
            st.session_state["num_teams"] = len(prefill_teams)

            for i, team in enumerate(prefill_teams):
                st.session_state[f"name_{i}"] = team["team_name"]
                st.session_state[f"power_{i}"] = int(team["power"])
                st.session_state[f"heroes_{i}"] = team["heroes"]

            st.rerun()

    if "num_teams" not in st.session_state:
        st.session_state["num_teams"] = 1

    num_teams = st.number_input(
        "Anzahl gegnerischer Teams", min_value=1, max_value=20, key="num_teams"
    )

    enemy_teams = []
    selected_names = []

    training_entries = load_training_data()

    power_offset = st.number_input(
        "Erlaubter Stärkeunterschied (k)",
        min_value=0,
        value=10,
        step=1,
        help="k=1000. Beispiel: 10 is equivalent zu 10k.",
    )
    # If no training data yet, warn the user and skip calculation
    if not training_entries:
        st.warning("Keine Trainingsdaten gefunden. Bitte zuerst Daten im Trainings‑Tab einfügen.")
    
    # Create enemy team input sections
    for i in range(num_teams):
        st.subheader(f"Gegner {i+1}")

        col1, col2 = st.columns([1, 3])

        # Only show names that are not already selected
        available_names = [name for name in GK_POSITIONS if name not in selected_names]

        with col1:
            team_name = st.selectbox(
                "Position", options=available_names, key=f"name_{i}"
            )

            enemy_power = st.number_input(
                "Gegnerstärke (k, optional)",
                min_value=0,
                value=0,
                step=1,
                key=f"power_{i}",
                help="k=1000. Beispiel: 10 is equivalent zu 10k.",
            )

            selected_names.append(team_name)

        with col2:
            selected_heroes = st.multiselect(
                "Wähle exakt 5 Helden", HEROES, max_selections=5, key=f"heroes_{i}"
            )

        enemy_teams.append(
            {
                "team_name": team_name,
                "heroes": selected_heroes,
                "specified_power": enemy_power,
            }
        )

    # Move the calculate button below the enemy inputs
    st.markdown("<br><br>", unsafe_allow_html=True)

    if st.button("Berechnen"):

        if not training_entries:
            st.error("Keine Trainingsdaten vorhanden – Bitte erst Trainingsdaten anlegen.")
            return

        # Validation
        incomplete_teams = [
            t["team_name"] or f"Team {idx+1}"
            for idx, t in enumerate(enemy_teams)
            if len(t["heroes"]) != 5
        ]

        if incomplete_teams:
            st.error("Jedes Team muss aus exakt 5 Helden bestehen.")
        else:
            assignments, unassigned_enemies = greedy_matchmaking(
                enemy_teams,
                training_entries,
                power_offset,
            )

            if assignments:
                st.success("Zuteilungen:")
                prettify_assignments(assignments)

                if unassigned_enemies:
                    st.warning(
                        "Keine passenden Zuteilungen für folgende Teams:"
                    )

                    for enemy in unassigned_enemies:
                        name = enemy["team_name"]
                        heroes = ", ".join(enemy["heroes"])
                        specified_power = enemy.get("specified_power", 0)

                        if specified_power:
                            st.write(f"- {name} ({specified_power}k)")
                        else:
                            st.write(f"- {name}")

                        st.write(f"Helden: {heroes}")
            else:
                st.warning("Keine passenden Zuweisungen gefunden")
