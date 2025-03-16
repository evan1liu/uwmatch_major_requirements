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
    cursor = db.roadmap.find(
        
    )
    async for doc in cursor:
        print(doc)

# Run the async function
asyncio.run(fetch_course())