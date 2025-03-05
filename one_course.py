from motor.motor_asyncio import AsyncIOMotorClient
from config import Settings
import asyncio

client = AsyncIOMotorClient(Settings.MONGODB_URI)
db = client.uwmatch  # Database name

from motor.motor_asyncio import AsyncIOMotorClient
from config import Settings
import asyncio

# Connect to MongoDB
client = AsyncIOMotorClient(Settings.MONGODB_URI)
db = client.uwmatch  # Database name

# Define an async function to handle the query
async def fetch_course():
    cursor = db.courses.find(
        {'title': "COM ARTS 100 — INTRODUCTION TO SPEECH COMPOSITION"},
        {
            'title': 1,
            'course_designation': 1,
            'credits': 1,
            'description': 1,
            'last_taught': 1,
            'learning_outcomes': 1,
            'repeatable': 1,
            'requisites': 1
        }
    )
    async for doc in cursor:
        print(doc)

# Run the async function
asyncio.run(fetch_course())