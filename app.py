import streamlit as st
import pandas as pd
from greedyMatchmaking import greedy_matchmaking

@st.cache_data
def load_statistics():
    df = pd.read_csv("statistics.csv")

    # parse to numeric value
    df["Power Own"] = pd.to_numeric(df["Power Own"], errors="coerce")
    df["Power Enemy"] = pd.to_numeric(df["Power Enemy"], errors="coerce")

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

def can_defeat(member, enemy, statistics_df, power_offset):
    enemy_sorted = tuple(sorted(enemy["heroes"]))
    specified_power = enemy.get("specified_power", 0)

    matches = statistics_df[
        (statistics_df["Player"] == member["name"]) &
        (statistics_df["enemy_team_sorted"] == enemy_sorted)
    ]

    if matches.empty:
        return None

    for _, row in matches.iterrows():

        if specified_power == 0:
            return row

        required_min_power = specified_power - power_offset

        if row["Power Enemy"] >= required_min_power:
            return row

    return None

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

        # Format powers with k and handle NaN
        enemy_power_str = f"{int(enemy_power)}k" if pd.notna(enemy_power) else "?"
        player_power_str = f"{int(player_power)}k" if pd.notna(player_power) else "?"

        st.subheader(f"{enemy_name} ({enemy_power_str})")
        st.write(f"Enemy Heroes: {enemy_heroes}")
         # Player info with green team
        st.markdown(
            f"<span style='color:green'>{player_name} ({player_power_str}) : </span>"
            f"<span style='color:green'>{player_team}</span>",
            unsafe_allow_html=True
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

st.set_page_config(page_title="Team Matcher", layout="wide")

templates_df = load_templates()

guilds = sorted(
    templates_df["Guild"]
    .dropna()
    .unique()
)

selected_guild = st.selectbox(
    "Choose Guild Template",
    guilds
)
guild_templates = templates_df[
    templates_df["Guild"] == selected_guild
]
prefill_teams = []

for _, row in guild_templates.iterrows():
    prefill_teams.append({
        "team_name": row["Building"],
        "heroes": row["enemy_team"],
        "power": row["Power"]
    })

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

power_offset = st.number_input(
    "Allowed Enemy Power Offset (k)",
    min_value=0,
    value=10,
    step=1,
    help="Value is in thousands. Example: 10 means 10k."
)

if selected_guild:
    for i, team in enumerate(prefill_teams):
        st.session_state[f"name_{i}"] = team["team_name"]
        st.session_state[f"power_{i}"] = int(team["power"])

        # multiselect expects list
        st.session_state[f"heroes_{i}"] = team["heroes"]
        
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

        enemy_power = st.number_input(
            "Enemy Power (k, optional)",
            min_value=0,
            value=0,
            step=1,
            key=f"power_{i}",
            help="Value is in thousands. Example: 60 means 60k."
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
        "heroes": selected_heroes,
        "specified_power": enemy_power
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

        assignments, unassigned_enemies = greedy_matchmaking(
            enemy_teams,
            my_team_members,
            lambda member, enemy: can_defeat(
                member,
                enemy,
                statistics_df,
                power_offset
            )
)

        if assignments:
            st.success("Assignments created")
            prettify_assignments(assignments)

            if unassigned_enemies:
                st.warning("No valid assignment found for the following enemy teams:")

                for enemy in unassigned_enemies:
                    name = enemy["team_name"]
                    heroes = ", ".join(enemy["heroes"])
                    specified_power = enemy.get("specified_power", 0)

                    if specified_power:
                        st.write(f"- {name} ({specified_power}k)")
                    else:
                        st.write(f"- {name}")

                    st.write(f"  Heroes: {heroes}")
        else:
            st.warning("No valid assignments found")
