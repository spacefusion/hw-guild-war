from pymongo import MongoClient
from config.settings import MONGO_URI


class TrainingDataRepository:
    DATABASE_NAME = "BlackPearl"
    COLLECTION_NAME = "TrainingData"

    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[self.DATABASE_NAME]
        self.collection = self.db[self.COLLECTION_NAME]

    def insert_training_entry(self, entry: dict) -> dict:
        """
        Inserts a training entry into MongoDB and returns the inserted document.
        """
        self.collection.insert_one(entry)
        # return the inserted id string so callers can echo or store it
        return entry

    def get_all_training_entries(self) -> list[dict]:
        return list(self.collection.find({}))
