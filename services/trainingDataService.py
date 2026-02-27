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


def insert_training_entry(self, entry: dict) -> dict:
    result = self.collection.insert_one(entry)
    entry["_id"] = result.inserted_id  # add the MongoDB ID to the dict
    return entry