import streamlit as st
from ui.matchmaking import show_matchmaking_ui
from ui.trainingData import show_training_ui
st.set_page_config(page_title="Team Matcher", layout="wide")

# Read query param once
query_params = st.query_params
current_page = query_params.get("page", "training")

if current_page not in ["matchmaking", "training"]:
    current_page = "training"

PAGES = {
    "matchmaking": "Matchmaking",
    "training": "Trainingsdaten einfügen",
}

REVERSE_PAGES = {v: k for k, v in PAGES.items()}

# Initialize session state once
if "page" not in st.session_state:
    st.session_state.page = current_page

# Sidebar radio bound directly to session state
selected_label = st.sidebar.radio(
    "Funktion auswählen",
    options=list(PAGES.values()),
    key="page_label",
    index=list(PAGES.keys()).index(st.session_state.page),
)

selected_page = REVERSE_PAGES[selected_label]

# If changed, update session state and URL
if selected_page != st.session_state.page:
    st.session_state.page = selected_page
    st.query_params["page"] = selected_page
    #ensures immediate correct rendering
    st.rerun()

# Render UI
if st.session_state.page == "matchmaking":
    show_matchmaking_ui()
else:
    show_training_ui()
