from models.trainingDataEntry import TrainingDataEntry
from repositories.trainingDataRepository import TrainingDataRepository
from datetime import datetime, timezone
from collections import defaultdict
from models.aggregatedTeam import AggregatedTeam


class TrainingDataService:

    def __init__(self):
        self.repository = TrainingDataRepository()

    def save_training_data(
        self,
        player,
        ownTeam,
        ownStrength,
        wins,
        losses,
        enemyTeam,
        enemyStrength,
    ):
        entry = TrainingDataEntry(
            player=player,
            ownTeam=ownTeam,
            ownStrength=ownStrength,
            wins=wins,
            losses=losses,
            enemyTeam=enemyTeam,
            enemyStrength=enemyStrength,
            timestamp=datetime.now(timezone.utc),
        )

        entry_dict = entry.to_dict()
        entry_dict.pop("_id", None)
        inserted_entry = self.repository.insert_training_entry(entry_dict)
        return inserted_entry

    def fetch_training_data(self) -> list[TrainingDataEntry]:
        """Retrieve all entries from the database as dataclass objects."""
        docs = self.repository.get_all_training_entries()
        entries: list[TrainingDataEntry] = []
        for d in docs:
            entry_id = str(d.get("_id", ""))
            # drop Mongo-specific fields
            data = {k: v for k, v in d.items() if k != "_id"}
            # if the record has no timestamp (old data), give it one now (otherwise loading the data will fail)
            if "timestamp" not in data or data.get("timestamp") is None:
                data["timestamp"] = datetime.now(timezone.utc)
            # normalize numeric fields which may have been stored as strings
            for num_field in ("ownStrength", "enemyStrength", "wins", "losses"):
                if num_field in data and isinstance(data[num_field], str):
                    try:
                        data[num_field] = int(data[num_field])
                    except ValueError:
                        pass
            entries.append(TrainingDataEntry(**data, _id=entry_id))
        return entries

    def fetch_data_by_player(self, player: str) -> list[TrainingDataEntry]:
        """Retrieve all entries from the database as dataclass objects that include the specified player."""
        docs = self.repository.get_all_by_player(player)
        entries: list[TrainingDataEntry] = []
        for d in docs:
            entry_id = str(d.get("_id", ""))
            # drop Mongo-specific fields
            data = {k: v for k, v in d.items() if k != "_id"}
            # if the record has no timestamp (old data), give it one now (otherwise loading the data will fail)
            if "timestamp" not in data or data.get("timestamp") is None:
                data["timestamp"] = datetime.now(timezone.utc)
            # normalize numeric fields which may have been stored as strings
            for num_field in ("ownStrength", "enemyStrength", "wins", "losses"):
                if num_field in data and isinstance(data[num_field], str):
                    try:
                        data[num_field] = int(data[num_field])
                    except ValueError:
                        pass
            entries.append(TrainingDataEntry(**data, _id=entry_id))
        return entries

    def update_training_data(
        self,
        entry_id: str,
        wins: int,
        losses: int,
        enemy_strength: int,
        own_strength: int,
    ):
        """Update mutable fields of an existing training entry by its MongoDB _id."""
        updates = {
            "wins": wins,
            "losses": losses,
            "enemyStrength": enemy_strength,
            "ownStrength": own_strength,
        }
        self.repository.update_training_entry(entry_id, updates)

    def delete_training_data(self, entry_id: str):
        """Delete a training entry by its MongoDB _id."""
        self.repository.delete_training_entry(entry_id)

    def get_unique_player_teams_with_max_strength(self, player: str) -> list[AggregatedTeam]:
        """
        Returns a list of unique own teams for the given player,
        including the maximum observed ownStrength for each team.
        """
        entries = self.fetch_data_by_player(player)
        return self._aggregate_teams_max_strength(entries)

    def _aggregate_teams_max_strength(
        self, entries: list[TrainingDataEntry]
    ) -> list[AggregatedTeam]:
        """
        Internal aggregation logic.
        Groups teams order independent and keeps max ownStrength.
        """
        team_strength_map: dict[tuple[str, ...], int] = defaultdict(int)

        for entry in entries:
            # Normalize team order so hero order does not matter
            team_key = tuple(sorted(entry.ownTeam))

            # ensure we compare numeric values; some rows may have strings stored
            try:
                strength = int(entry.ownStrength)
            except (TypeError, ValueError):
                # fallback: if it's already numeric or None, let Python handle it
                strength = entry.ownStrength or 0

            if strength > team_strength_map[team_key]:
                team_strength_map[team_key] = strength

        result = [
            AggregatedTeam(list(team_key), max_strength)
            for team_key, max_strength in team_strength_map.items()
        ]

        return result
