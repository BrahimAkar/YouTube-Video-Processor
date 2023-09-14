import os
from pymongo import MongoClient

# Mongo client
client = MongoClient(os.getenv("MONGODB_URL"))


# Database
db = client['app_v2']

# Collections
results_collection = db['videos_processing_results']
youtube_videos_collection = db['youtube_videos']