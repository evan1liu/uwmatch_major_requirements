from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import sys
from pathlib import Path
# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Settings

# Step 1: Initialize the async MongoDB client
client = AsyncIOMotorClient(Settings.MONGODB_URI)
db = client.uwmatch  # Database name
# course_colelction = db.courses

# no need to make this function async, since it's just a reference to a collection
# no operations is being done through solely using this function
def get_mongodb_collection(collection_name):
    return db[collection_name] # inside a function, we must use a bracket notation