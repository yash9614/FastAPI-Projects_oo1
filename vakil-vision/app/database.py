from pymongo import MongoClient

from app.config import MONGODB_URI

client = MongoClient(MONGODB_URI)
db = client.get_default_database()
if db is None:
    db = client["vakil_vision"]

contracts_collection = db["contracts"]
analysis_collection = db["analysis"]


def init_db():
    contracts_collection.create_index("filename", unique=True)
    analysis_collection.create_index("contract_id")
