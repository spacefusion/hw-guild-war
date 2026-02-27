import streamlit as st
from ui.matchmaking import show_matchmaking_ui
from ui.training import show_training_ui

st.set_page_config(page_title="Team Matcher", layout="wide")

page = st.sidebar.selectbox("Choose page", ["Matchmaking","Insert Training Data"])

if page == "Matchmaking":
    show_matchmaking_ui()
else:
    show_training_ui()
