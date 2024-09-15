from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["msee"]

songs = db["songs"]
settings = db["settings"]
hcm_features = db["hcm_features"]
jobs = db["jobs"]


def get_collection(collection_name: str):
    return db[collection_name]


def close_mongo_connection():
    client.close()
