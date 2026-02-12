import streamlit as st
import pandas as pd
from greedyMatchmaking import greedy_matchmaking

@st.cache_data
def load_statistics():
    df = pd.read_csv("statistics.csv")

    own_cols = ["Own1", "Own2", "Own3", "Own4", "Own5"]
    enemy_cols = ["Enemy1", "Enemy2", "Enemy3", "Enemy4", "Enemy5"]

    # Normalize hero order so order does not matter
    df["own_team_sorted"] = df[own_cols].apply(
        lambda row: tuple(sorted(row.astype(str))), axis=1
    )

    df["enemy_team_sorted"] = df[enemy_cols].apply(
        lambda row: tuple(sorted(row.astype(str))), axis=1
    )

    return df

def get_my_team_members(statistics_df):
    members = []

    grouped = statistics_df.groupby("Player")

    for player_name, group in grouped:
        row = group.iloc[0]

        own_team = tuple(sorted([
            row["Own1"],
            row["Own2"],
            row["Own3"],
            row["Own4"],
            row["Own5"],
        ]))

        members.append({
            "name": player_name,
            "team": own_team,
            "power_own": row["Power Own"]
        })

    return members

def can_defeat(member, enemy):
    enemy_sorted = tuple(sorted(enemy["heroes"]))

    match = statistics_df[
        (statistics_df["Player"] == member["name"]) &
        (statistics_df["enemy_team_sorted"] == enemy_sorted)
    ]

    if match.empty:
        return None

    return match.iloc[0]

def prettify_assignments(assignments):
    """
    Returns a Streamlit-friendly prettified output of assignments.

    Each enemy team is a header, with the assigned player and their team below.
    """
    for assign in assignments:
        enemy_name = assign["enemy_team"]
        enemy_power = assign["enemy_power"]
        enemy_heroes = ", ".join(assign["enemy_heroes"])

        player_name = assign["assigned_player"]
        player_power = assign["player_power"]
        player_team = ", ".join(assign["player_team"])

        st.subheader(f"{enemy_name} ({enemy_power})")
        st.write(f"Enemy Heroes: {enemy_heroes}")
        st.write(f"{player_name} ({player_power}) : {player_team}")
        st.markdown("---")

st.set_page_config(page_title="Team Matcher", layout="wide")

st.title("Enemy Teams Input")

HEROES = sorted([
    "Ginger","Iris","Isaac","Julius","Fafnir","Nebula","Dante","Richter",
    "Octavia","Polaris","Martha","Oya","Hackebeil","Yasmine","Jhu",
    "Artemis","Corvus","Kayla","Tempus","Maya","Aidan","Arachne",
    "Tristan","Dunkler Stern","Orion","Folio","Morrigan","Champi und Gnon",
    "Kai","Cornelius","Satori","Luther","Jorgen","Astrid","Lillith",
    "Soleil","Gesichtsloser","Astaroth","Alvanor","Chabba","Karkh",
    "Elmir","Lian","Quing Mao","Rufus","Ziri","Keira","Dorian",
    "Galahad","Mojo","Phobos","Heidi","Thea","XeSha","Aurora",
    "Amira","Celeste","Sebastian","Kaskade","Peppy","Draufgänger",
    "Markus","Ishmael","Electra","Guus","Krista","Byrna",
    "Ninja Turtles","Helios","Lars","Fuchs","Andvari","Peech",
    "Somna","Lara Croft","Jet","Drayne"
])

ENEMY_NAMES = [
    "Festung 1",
    "Festung 2",
    "Festung 3",
    "Festung 4",
    "Festung 5",
    "Festung 6",
    "Festung 7",
    "Leuchtturm 1",
    "Leuchtturm 2",
    "Leuchtturm 3",
    "Akademie 1",
    "Akademie 2",
    "Akademie 3",
    "Kaserne 1",
    "Kaserne 2",
    "Kaserne 3",
    "Gießerei 1",
    "Gießerei 2",
    "Gießerei 3",
    "Gießerei 4"
]


num_teams = st.number_input(
    "Number of Enemy Teams",
    min_value=1,
    max_value=20,
    value=1
)

enemy_teams = []
selected_names = []

statistics_df = load_statistics()

# Create enemy team input sections
for i in range(num_teams):
    st.subheader(f"Enemy Team {i+1}")
    
    col1, col2 = st.columns([1, 3])
    
    # Only show names that are not already selected
    available_names = [
        name for name in ENEMY_NAMES
        if name not in selected_names
    ]

    with col1:
        team_name = st.selectbox(
            "Select Enemy Name",
            options=available_names,
            key=f"name_{i}"
        )
        selected_names.append(team_name)
    
    with col2:
        selected_heroes = st.multiselect(
            "Select 5 Heroes",
            HEROES,
            max_selections=5,
            key=f"heroes_{i}"
        )
    
    enemy_teams.append({
        "team_name": team_name,
        "heroes": selected_heroes
    })

# Move the calculate button below the enemy inputs
st.markdown("<br><br>", unsafe_allow_html=True)

if st.button("Calculate Matchups"):
    
    # Validation
    incomplete_teams = [
        t["team_name"] or f"Team {idx+1}"
        for idx, t in enumerate(enemy_teams)
        if len(t["heroes"]) != 5
    ]
    
    if incomplete_teams:
        st.error(
            "Each team must have exactly 5 heroes selected."
        )
    else:
        my_team_members = get_my_team_members(statistics_df)

        assignments = greedy_matchmaking(
            enemy_teams,
            my_team_members,
            can_defeat
        )

        if assignments:
            st.success("Assignments created")
            prettify_assignments(assignments)
        else:
            st.warning("No valid assignments found")

