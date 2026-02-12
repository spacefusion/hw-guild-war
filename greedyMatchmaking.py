# greedyMatchmaking.py

def greedy_matchmaking(enemy_teams, my_team_members, can_defeat_func):
    """
    Greedy Level 1 Matchmaking

    enemy_teams: list of dicts
    my_team_members: list of dicts
    can_defeat_func(member, enemy) -> bool
    """

    remaining_attacks = {m["name"]: 2 for m in my_team_members}

    enemy_options = []

    for enemy in enemy_teams:
        possible_members = []

        for member in my_team_members:
            if can_defeat_func(member, enemy):
                possible_members.append(member["name"])

        enemy_options.append({
            "enemy": enemy,
            "possible_members": possible_members
        })

    # Fewest options first
    enemy_options.sort(key=lambda x: len(x["possible_members"]))

    assignments = []

    for entry in enemy_options:
        enemy = entry["enemy"]
        possible = entry["possible_members"]

        valid_members = [
            m for m in possible
            if remaining_attacks[m] > 0
        ]

        if not valid_members:
            continue

        # Choose member with lowest remaining attacks
        chosen = sorted(
            valid_members,
            key=lambda m: remaining_attacks[m]
        )[0]

        assignments.append({
            "enemy_team": enemy["team_name"],
            "assigned_member": chosen
        })

        remaining_attacks[chosen] -= 1

    return assignments