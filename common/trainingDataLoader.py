# trainingDataLoader.py
import streamlit as st
from models.trainingDataEntry import TrainingDataEntry
from models.aggregatedTeam import AggregatedTeam
from services.trainingDataService import TrainingDataService


@st.cache_data
def load_training_data() -> list[TrainingDataEntry]:
    """Load all training entries from MongoDB.
    Returns a list of :class:`TrainingDataEntry` objects used for matchmaking.
    """
    service = TrainingDataService()
    return service.fetch_training_data()

@st.cache_data
def load_existing_player_teams(player: str) -> list[AggregatedTeam]:
    """Load all training entries from MongoDB that are assigned to a specific player and extract a unique list of AggregatedTeams.
    Returns a list of :class:`AggregatedTeams` objects.
    """
    service = TrainingDataService()
    return service.get_unique_player_teams_with_max_strength(player)
