from models.trainingDataEntry import TrainingDataEntry
from repositories.trainingDataRepository import TrainingDataRepository


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
        )

        inserted_entry = self.repository.insert_training_entry(entry.to_dict())
        return inserted_entry

    def fetch_training_data(self) -> list[TrainingDataEntry]:
        """Retrieve all entries from the database as dataclass objects."""
        docs = self.repository.get_all_training_entries()
        entries: list[TrainingDataEntry] = []
        for d in docs:
            # drop Mongo-specific fields
            data = {k: v for k, v in d.items() if k != "_id"}
            entries.append(TrainingDataEntry(**data))
        return entries
