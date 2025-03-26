from bson import ObjectId
from typing import Optional, List, Dict
from utils.get_mongodb_collection import get_mongodb_collection
import asyncio
import time

COURSE_COLLECTION = get_mongodb_collection("courses")

async def get_single_course_by_id(course_id: str, fields: Optional[List[str]] = None) -> Optional[Dict]:
    """The function retrieves a single course document by its ID.

    Args:
        course_id (str): The MongoDB ObjectId of the course as a string.
        fields (Optional[List[str]]): Fields to include in the result; if None, all fields are returned.

    Returns:
        Optional[Dict]: The course document, or None if not found.

    Note:
        In the MongoDB pipeline, we use $match first to filter out the document that matches the course_id
        Then, we use $project to specify the fields we're retrieving
    """
    query = {"_id": ObjectId(course_id)}
    projection = {field: 1 for field in fields} if fields is not None else None
    course = await COURSE_COLLECTION.find_one(query, projection)
    course["_id"] = str(course["_id"])
    
    return course

async def get_courses_by_ids_bulk(course_ids: List[str], fields: Optional[List[str]] = None) -> Dict:
    """The function retrieves multiple course documents by a list of course IDs

    Args:
        course_ids (List[str]): A list of STRING IDs, NOT ObjectID
        fields (Optional[List[str]]): Fields to include in the result; if None, all fields are returned.

    Returns:
        Dict: A dictionary containing:
            - 'found_courses': List of found course documents
            - 'missing_course_ids': List of course IDs that weren't found
    """
    
    course_object_ids = [ObjectId(course_id) for course_id in course_ids]
    pipeline = [{"$match": {"_id": {"$in": course_object_ids}}}]
    
    if fields is not None:
        pipeline.append({"$project": {field: 1 for field in fields}})
    
    found_courses = await COURSE_COLLECTION.aggregate(pipeline).to_list(length=None)
    found_courses = [{**course, "_id": str(course["_id"])} for course in found_courses]
    
    # before returning the course documents, first we check if all courses successfully retrieved
    found_ids = {course["_id"] for course in found_courses}
    # if some of the course_ids do not exist in the course documents we retrieved, we add them to the list of missing ids
    missing_course_ids = [course_id for course_id in course_ids if course_id not in found_ids]
    
    # return it as a dictionary, use found_courses for retrieving information, use missing_course_ids for debugging
    return {
        "found_courses": found_courses,
        "missing_course_ids": missing_course_ids
    }

COURSE_FIELDS = [
    "_id",
    "course_code",
    "credits",
    "departments",
    "course_number",
    "formatted_designations",
    "school-or-college"
]

async def main():
    # Example test cases
    test_course_id = "67577efb7fd66ec727391979"
    test_course_ids = [
        "67577f107fd66ec727391df5",
        "67577eec7fd66ec72739161f",
        '67577f027fd66ec727391b39',  # First test course
        '67577f997fd66ec727393c59',  # Another test course
        '67577f147fd66ec727391eed',  # Additional test course
        '67577eec7fd66ec72739161f',
        '67577f067fd66ec727391bfc',
        '67577f7e7fd66ec727393650',
        '67577f1d7fd66ec7273920cb',
        '67577efb7fd66ec72739197d' # Additional test course
    ]
    
    # Test 1: Single course, all fields
    start_time = time.time()
    single_course_all = await get_single_course_by_id(test_course_id)
    elapsed_time = time.time() - start_time
    print(f"Single course (all fields) - Time: {elapsed_time:.4f} seconds")
    print("Single course (all fields):\n", single_course_all)

    # Test 2: Single course, specific fields
    start_time = time.time()
    single_course_specific = await get_single_course_by_id(test_course_id, COURSE_FIELDS)
    elapsed_time = time.time() - start_time
    print(f"\nSingle course (specific fields) - Time: {elapsed_time:.4f} seconds")
    print("Single course (specific fields):\n", single_course_specific)

    # Test 3: Bulk courses, all fields
    start_time = time.time()
    bulk_courses_all = await get_courses_by_ids_bulk(test_course_ids)
    elapsed_time = time.time() - start_time
    print(f"\nBulk courses (all fields) - Time: {elapsed_time:.4f} seconds")
    print("Found courses:\n", bulk_courses_all["found_courses"])
    print("Missing course IDs:\n", bulk_courses_all["missing_course_ids"])

    # Test 4: Bulk courses, specific fields
    start_time = time.time()
    bulk_result = await get_courses_by_ids_bulk(test_course_ids, COURSE_FIELDS)
    elapsed_time = time.time() - start_time
    print(f"\nBulk courses (specific fields) - Time: {elapsed_time:.4f} seconds")
    print("Found courses:\n", bulk_result["found_courses"])
    print("Missing course IDs:\n", bulk_result["missing_course_ids"])

if __name__ == "__main__":
    asyncio.run(main())