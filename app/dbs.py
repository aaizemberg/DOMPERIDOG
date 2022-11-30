import pymongo
from app.core.settings import settings

mongo_client = pymongo.MongoClient(settings.MONGODB_URL)
mongodb = mongo_client["domperidog"]
user_collection = mongodb["users"]
document_collection = mongodb["documents"]

user_collection.create_index([('username', pymongo.TEXT)], name='username_index', default_language='english')

try:
    mongo_client.list_database_names()
except pymongo.errors.ConnectionFailure:
    raise Exception("Mongo connection error")
