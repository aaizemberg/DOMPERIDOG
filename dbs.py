import pymongo
import redis
from core.settings import settings

mongo_client = pymongo.MongoClient(settings.MONGODB_URL)
mongodb = mongo_client["domperidog"]
user_collection = mongodb["users"]
document_collection = mongodb["documents"]

user_collection.create_index([('username', pymongo.TEXT)], name='username_index', default_language='english')
document_collection.create_index([('title', pymongo.TEXT)], name='title_index', default_language='english')
document_collection.create_index([('author', pymongo.TEXT)], name='author_index', default_language='english')

try:
    mongo_client.list_database_names()
except pymongo.errors.ConnectionFailure:
    raise Exception("Mongo connection error")

rediscache = redis.Redis(host=settings.REDIS_CACHE_HOSTNAME, port=settings.REDIS_CACHE_PORT, db=0, password=settings.REDIS_CACHE_PASSWORD)

try:
    rediscache.ping()
except redis.exceptions.ConnectionError:
    raise Exception("Redis connection error")

