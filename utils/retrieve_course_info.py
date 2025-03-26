from bson import ObjectId
from typing import Optional, List, Dict
from utils.get_mongodb_collection import get_mongodb_collection
import asyncio

COURSE_COLLECTION = get_mongodb_collection("courses")

async def get_single_course(course_id: str, fields: Optional[List[str]] = None) -> Optional[Dict]:
    # a mongodb pipeline is a list of operations that mongodb will undertake
    # $match filters out the courses that match your criteria
    # when $project doesn't exist, mongodb automatically retrieves all fields
    pipeline = [{"$match": {"_id": ObjectId(course_id)}}]
    if fields is not None:
        pipeline.append({"$project": {field: 1 for field in fields}})
    result = await COURSE_COLLECTION.aggregate(pipeline).to_list(length=1)
    return result[0] if result else None

async def get_courses_bulk(course_ids: List[str], fields: Optional[List[str]] = None) -> List[Dict]:
    course_object_ids = [ObjectId(course_id) for course_id in course_ids]
    pipeline = [{"$match": {"_id": {"$in": course_object_ids}}}]
    if fields is not None:
        pipeline.append({"$project": {field: 1 for field in fields}})
    return await COURSE_COLLECTION.aggregate(pipeline).to_list(length=None)

COURSE_FIELDS = [
    "_id",
    "course_code",
    "credits",
    "departments",
    "course_number",
    "formatted_designations"
]

async def main():
    # Example test cases
    test_course_id = "67577f1d7fd66ec7273920cb"
    test_course_ids = ["67577f1d7fd66ec7273920cb", "67577eec7fd66ec72739161f"]

    # Test 1: Single course, all fields
    single_course_all = await get_single_course(test_course_id)
    print("Single course (all fields):", single_course_all)
    # Expected: Full course document or None if not found

    # Test 2: Single course, specific fields
    single_course_specific = await get_single_course(test_course_id, COURSE_FIELDS)
    print("Single course (specific fields):", single_course_specific)
    # Expected: Dict with only _id, course_code, and credits (or None)

    # Test 3: Bulk courses, all fields
    bulk_courses_all = await get_courses_bulk(test_course_ids)
    print("Bulk courses (all fields):", bulk_courses_all)
    # Expected: List of full course documents

    # Test 4: Bulk courses, specific fields
    bulk_courses_specific = await get_courses_bulk(test_course_ids, COURSE_FIELDS)
    print("Bulk courses (specific fields):", bulk_courses_specific)
    # Expected: List of dicts with only _id, course_code, and credits

    # Optional: Simple assertions (commented out since real data varies)
    # assert single_course_all is not None, "Single course (all) should exist"
    # assert "course_code" in single_course_specific, "Specific fields should include course_code"
    # assert len(bulk_courses_all) <= len(test_course_ids), "Bulk all should return <= input IDs"

if __name__ == "__main__":
    asyncio.run(main())