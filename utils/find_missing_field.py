from motor.motor_asyncio import AsyncIOMotorClient
import sys
from pathlib import Path
import asyncio

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Settings
from utils.get_mongodb_collection import get_fields_by_id

# Initialize the async MongoDB client
client = AsyncIOMotorClient(Settings.MONGODB_URI)
db = client.uwmatch  # Database name
course_collection = db.courses

# Test courses - use the same ones from your test
test_courses = ['67577f027fd66ec727391b39', '67577f027fd66ec727391b39', '67577f997fd66ec727393c59', '67577f147fd66ec727391eed', '67577eec7fd66ec72739161f']

async def check_courses_for_missing_fields():
    """Check which courses are missing the formatted_designations field"""
    results = []
    
    for course_id in test_courses:
        # First get the course code for better identification
        course_data = await get_fields_by_id(course_collection, course_id, ["course_code"])
        course_code = course_data.get("course_code", "Unknown").replace('\u200b', '')
        
        # Now check for the formatted_designations field
        fields_data = await get_fields_by_id(course_collection, course_id, ["formatted_designations"])
        has_field = "formatted_designations" in fields_data
        
        # Get the document for inspection
        full_document = await course_collection.find_one({"_id": course_id})
        available_fields = list(full_document.keys()) if full_document else []
        
        results.append({
            "course_id": course_id,
            "course_code": course_code,
            "has_formatted_designations": has_field,
            "available_fields": available_fields
        })
    
    return results

async def main():
    print("Checking courses for missing 'formatted_designations' field...")
    results = await check_courses_for_missing_fields()
    
    print("\nResults:")
    for result in results:
        print(f"Course ID: {result['course_id']}")
        print(f"Course Code: {result['course_code']}")
        print(f"Has 'formatted_designations' field: {result['has_formatted_designations']}")
        print(f"Available fields: {', '.join(result['available_fields'])}")
        print("-" * 50)
    
    print("\nCourses missing 'formatted_designations' field:")
    missing_field = [r for r in results if not r['has_formatted_designations']]
    if missing_field:
        for course in missing_field:
            print(f"- {course['course_code']} (ID: {course['course_id']})")
    else:
        print("All courses have the 'formatted_designations' field.")

if __name__ == "__main__":
    asyncio.run(main()) 