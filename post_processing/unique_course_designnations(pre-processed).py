# for each course BEFORE processing,
# course designations are in a pure string seperated by lines


from motor.motor_asyncio import AsyncIOMotorClient
from config import Settings
import asyncio

# Step 1: Initialize the async MongoDB client
client = AsyncIOMotorClient(Settings.MONGODB_URI)
db = client.uwmatch  # Database name
course_collection = db.courses

# Step 2: Define the async function to process the collection
async def get_unique_categories():
    unique_categories = set()

    # Step 3: Use an async cursor to iterate through all documents
    async for doc in course_collection.find():
        # Get the 'course_designation' field (default to empty string if missing)
        course_designation = doc.get("course_designation", "")
        
        # Step 4: Split the field into lines and add to the set
        if course_designation:  # Check if the field is non-empty
            lines = course_designation.split("\n")  # Split by newline
            unique_categories.update(line.strip() for line in lines if line.strip())  # Add non-empty lines to set

    # Step 5: Return the unique items
    return unique_categories

# Step 6: Define the main async function to run the script
async def main():
    # Get the unique categories
    unique_categories = await get_unique_categories()

    # Output the unique items
    print("Unique Course Designation Items:")
    for item in sorted(unique_categories):  # Sort for readability (optional)
        print(item)

    print(f"\nTotal number of unique items: {len(unique_categories)}")

    # Close the connection (optional, as AsyncIOMotorClient closes automatically in modern versions)
    client.close()

# Step 7: Run the async event loop
if __name__ == "__main__":
    asyncio.run(main())