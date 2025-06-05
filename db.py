from pymongo import MongoClient
import os

MONGO_URI = os.environ.get("MONGO_URI", "your_mongodb_connection_string_here")
client = MongoClient('mongodb://localhost:27017/')
db = client['bookstore_db']