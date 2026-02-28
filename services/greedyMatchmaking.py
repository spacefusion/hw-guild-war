# greedyMatchmaking.py
from models.trainingDataEntry import TrainingDataEntry


def _get_my_team_players(entries: list[TrainingDataEntry]) -> list[str]:
    """Return a unique list of player names present in *entries*.
    The matchmaking algorithm only needs the list of names to track which
    players are available and how many attacks each has.
    """
    seen = set()
    names: list[str] = []
    for entry in entries:
        if entry.player in seen:
            continue
        seen.add(entry.player)
        names.append(entry.player)
    return names


def _can_defeat(
    player: str, enemy, entries: list[TrainingDataEntry], power_offset: int
):
    """
    Return a :class:`TrainingDataEntry` if *player* can defeat *enemy*.
    The helper scans the entire history for the given player/enemy pair.  If
    the enemy specifies a preferred power, the entry must meet the constraint
    ``enemyStrength >= specified_power - power_offset``.  The first qualifying
    record is returned.
    """
    enemy_sorted = tuple(sorted(enemy["heroes"]))
    specified_power = enemy.get("specified_power", 0)

    # filter entries for this player and enemy team
    matches = [
        e
        for e in entries
        if e.player == player and tuple(sorted(e.enemyTeam)) == enemy_sorted
    ]

    if not matches:
        return None

    for match in matches:
        # decide on power constraint
        if specified_power == 0:
            return match

        required_min_power = specified_power - power_offset
        if match.enemyStrength >= required_min_power:
            return match

    return None


def greedy_matchmaking(
    enemy_teams, training_entries: list[TrainingDataEntry], power_offset=0
):
    """Greedy assignment of players to enemy teams.
    *enemy_teams* is a list of dicts with keys ``team_name``, ``heroes`` and
    optionally ``specified_power``.
    *training_entries* is the full list of :class:`TrainingDataEntry` objects
    retrieved from MongoDB; the function is responsible for deriving the
    usable player list and looking up historic matches itself.
    The function returns ``(assignments, unassigned_enemies)`` where each
    assignment is a dict containing:

    * ``buildingPosition`` – the name/position passed in as ``team_name``
    * ``searchedEnemyStrength`` – the value of ``specified_power`` supplied by
      the caller when the enemy team was created
    * ``entry`` – the matching :class:`TrainingDataEntry` object from the
      database.
    """

    my_team_players = _get_my_team_players(training_entries)
    remaining_attacks = {name: 2 for name in my_team_players}
    enemy_options = []

    for enemy in enemy_teams:
        possible_players = []

        for player in my_team_players:
            entry = _can_defeat(player, enemy, training_entries, power_offset)

            if entry is not None:
                possible_players.append(
                    {"player_name": player, "entry": entry}
                )

        enemy_options.append({"enemy": enemy, "possible_players": possible_players})

    enemy_options.sort(key=lambda x: len(x["possible_players"]))

    assignments = []
    unassigned_enemies = []

    for entry in enemy_options:
        enemy = entry["enemy"]
        possible = entry["possible_players"]

        valid_players = [p for p in possible if remaining_attacks[p["player_name"]] > 0]

        if not valid_players:
            unassigned_enemies.append(enemy)
            continue

        chosen = sorted(
            valid_players, key=lambda m: remaining_attacks[m["player_name"]]
        )[0]

        entry = chosen["entry"]

        assignments.append(
            {
                "buildingPosition": enemy["team_name"],
                "searchedEnemyStrength": enemy.get("specified_power", 0),
                # original training entry that produced the match
                "entry": entry,
            }
        )

        remaining_attacks[chosen["player_name"]] -= 1

    return assignments, unassigned_enemies
