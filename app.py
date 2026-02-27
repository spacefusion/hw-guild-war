import streamlit as st
from ui.matchmaking import show_matchmaking_ui
from ui.trainingData import show_training_ui

st.set_page_config(page_title="Team Matcher", layout="wide")

# Read current query params
query_params = st.query_params
current_page = query_params.get("page", "training")

# Normalize value
if current_page not in ["matchmaking", "training"]:
    current_page = "training"

# Sidebar selection synced with URL
page = st.sidebar.selectbox(
    "Choose page",
    ["Matchmaking", "Insert Training Data"],
    index=0 if current_page == "matchmaking" else 1,
)

# Update URL when selection changes
if page == "Matchmaking":
    st.query_params["page"] = "matchmaking"
    show_matchmaking_ui()
else:
    st.query_params["page"] = "training"
    show_training_ui()
