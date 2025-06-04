from pymongo import MongoClient
import os

MONGO_URI = os.environ.get("MONGO_URI", "your_mongodb_connection_string_here")
client = MongoClient(MONGO_URI)
db = client.bookstore