from pymongo import MongoClient
from bson import ObjectId
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
    
    def get_all_by_player(self, player:str) -> list[dict]:
        # filter by the player field; previous implementation accidentally
        # passed a set which raised a TypeError from pymongo.
        return list(self.collection.find({"player": player}))

    def update_training_entry(self, entry_id: str, updates: dict):
        """Update fields of an existing training entry by its MongoDB _id."""
        self.collection.update_one({"_id": ObjectId(entry_id)}, {"$set": updates})
