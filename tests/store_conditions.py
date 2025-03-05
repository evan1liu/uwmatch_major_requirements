from motor.motor_asyncio import AsyncIOMotorClient
import sys
from pathlib import Path
# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Settings
import asyncio
from tests.example_conditions import condition

# Step 1: Initialize the async MongoDB client
client = AsyncIOMotorClient(Settings.MONGODB_URI)
db = client.uwmatch  # Database name
major_requirements_collection = db.major_requirements

async def store_data(course_data):
    # Insert the dictionary asynchronously
    result = await major_requirements_collection.insert_one(course_data)
    print(f"Inserted document with ID: {result.inserted_id}")

# Run the async function
asyncio.run(store_data(condition))