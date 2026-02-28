# trainingDataLoader.py
import streamlit as st
from models.trainingDataEntry import TrainingDataEntry
from services.trainingDataService import TrainingDataService

@st.cache_data
def load_training_data() -> list[TrainingDataEntry]:
    """Load all training entries from MongoDB.
    Returns a list of :class:`TrainingDataEntry` objects used for matchmaking.
    """
    service = TrainingDataService()
    return service.fetch_training_data()