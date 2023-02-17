from pymongo import MongoClient
import os
connection_url = os.getenv("connection_url")


def get_db_handle():
    client = MongoClient(connection_url)
    db_handle = client["olt_settings"]
    collection = db_handle["olt"]
    return collection
