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
        {'clean_title': "ELEMENTARY MATRIX AND LINEAR ALGEBRA"},
        {"_id": 1, "course_code": 1, "credits": 1, "departments": 1, "course_number": 1, "formatted_designations": 1, "school-or-college": 1}
    )
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        print(doc)

# Run the async function
asyncio.run(fetch_course())