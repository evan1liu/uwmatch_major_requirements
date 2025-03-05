from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import sys
from pathlib import Path
# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Settings
import asyncio
from tests.example_conditions import conditions

# Step 1: Initialize the async MongoDB client
client = AsyncIOMotorClient(Settings.MONGODB_URI)
db = client.uwmatch  # Database name
course_colelction = db.courses


async def get_fields_by_id(collection, document_id, fields):
    """
    Retrieve specific fields from a MongoDB document by ID.

    :param collection: MongoDB collection object
    :param document_id: Document's ObjectId as a string
    :param fields: List of fields to retrieve
    :return: Dictionary with requested fields
    """
    try:
        # Convert list of fields to MongoDB projection
        projection = {field: 1 for field in fields}  # Include specified fields
        projection["_id"] = 0  # Exclude `_id` from results

        # Retrieve the document
        document = await collection.find_one({"_id": ObjectId(document_id)}, projection)

        return document if document else {"error": "Document not found"}
    
    except Exception as e:
        return {"error": str(e)}

async def main():
    result = await get_fields_by_id(course_colelction, "67577f997fd66ec727393c59", ["formatted_designations", "course_designation", "title"])
    print(result)
    
if __name__ == "__main__":
    asyncio.run(main())