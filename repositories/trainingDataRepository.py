from pymongo import MongoClient
from config.settings import MONGO_URI


class TrainingDataRepository:
    DATABASE_NAME = "BlackPearl"
    COLLECTION_NAME = "TrainingData"

    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[self.DATABASE_NAME]
        self.collection = self.db[self.COLLECTION_NAME]

    def insert_training_entry(self, entry: dict) -> str:
        """
        Inserts a training entry into MongoDB and returns the inserted document ID.
        """
        result = self.collection.insert_one(entry)
        return str(result)
