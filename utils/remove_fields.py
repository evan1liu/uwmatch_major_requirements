from utils.get_mongodb_collection import get_mongodb_collection
import asyncio

# !!! SPECIFY THE FIELDS YOU WANT TO REMOVE HERE !!!
fields_to_remove = [
    "school-or-college"
]
# !!! SPECIFY THE COLLECTION YOU'RE WORKING WITH !!!
operating_collection = "courses"

async def check_fields_existence(collection, fields_to_remove):
    """
    Checks how many documents contain each field we plan to remove.
    This helps verify the operation before proceeding.
    
    Args:
        collection: MongoDB collection object
        fields_to_remove: List of field names to check
    """
    print("\nChecking field existence in documents:")
    for field in fields_to_remove:
        # Count documents where this field exists
        count = await collection.count_documents({field: {"$exists": True}})
        total = await collection.count_documents({})
        print(f"Field '{field}' exists in {count} out of {total} documents ({(count/total)*100:.1f}%)")

async def remove_fields(collection, fields_to_remove):
    """
    Removes specified fields from all documents in the collection.
    
    Args:
        collection: MongoDB collection object
        fields_to_remove: List of field names to remove
    """
    # Create the $unset operation dictionary
    unset_operation = {f"${field}": "" for field in fields_to_remove}
    
    # First, let's count how many documents we'll update
    documents_to_update = await collection.count_documents({})
    
    print(f"\nPreparing to remove fields from {documents_to_update} documents...")
    
    # Get confirmation from user
    confirmation = input("\nAre you sure you want to proceed? This cannot be undone! (yes/no): ")
    if confirmation.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    try:
        # Perform the update
        result = await collection.update_many(
            {},  # Match all documents
            {"$unset": {field: "" for field in fields_to_remove}}
        )
        
        print(f"\nOperation completed successfully:")
        print(f"Modified {result.modified_count} documents")
        
        # Verify the fields are gone
        print("\nVerifying fields were removed...")
        await check_fields_existence(collection, fields_to_remove)
        
    except Exception as e:
        print(f"An error occurred during the update: {e}")

async def main():    
    try:
        # Get collection using your utility function
        collection = get_mongodb_collection(operating_collection)
        
        # First, check which fields exist
        print("\nBefore removal:")
        await check_fields_existence(collection, fields_to_remove)
        
        # Remove the fields
        await remove_fields(collection, fields_to_remove)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())