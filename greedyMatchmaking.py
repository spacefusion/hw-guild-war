# greedyMatchmaking.py
def greedy_matchmaking(enemy_teams, my_team_members, can_defeat_func):

    remaining_attacks = {m["name"]: 2 for m in my_team_members}
    enemy_options = []

    for enemy in enemy_teams:
        possible_members = []

        for member in my_team_members:
            result = can_defeat_func(member, enemy)

            if result is not None:
                possible_members.append({
                    "member_name": member["name"],
                    "match_row": result
                })

        enemy_options.append({
            "enemy": enemy,
            "possible_members": possible_members
        })

    enemy_options.sort(key=lambda x: len(x["possible_members"]))

    assignments = []
    unassigned_enemies = []

    for entry in enemy_options:
        enemy = entry["enemy"]
        possible = entry["possible_members"]

        valid_members = [
            p for p in possible
            if remaining_attacks[p["member_name"]] > 0
        ]

        if not valid_members:
            unassigned_enemies.append(enemy)
            continue

        chosen = sorted(
            valid_members,
            key=lambda m: remaining_attacks[m["member_name"]]
        )[0]

        match_row = chosen["match_row"]

        assignments.append({
            "enemy_team": enemy["team_name"],
            "enemy_heroes": enemy["heroes"],
            "enemy_power": match_row["Power Enemy"],
            "assigned_player": chosen["member_name"],
            "player_team": (
                match_row["Own1"],
                match_row["Own2"],
                match_row["Own3"],
                match_row["Own4"],
                match_row["Own5"]
            ),
            "player_power": match_row["Power Own"]
        })

        remaining_attacks[chosen["member_name"]] -= 1

    return assignments,unassigned_enemies