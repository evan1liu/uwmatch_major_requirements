from utils.get_mongodb_collection import get_mongodb_collection
from tqdm.asyncio import tqdm
from collections import Counter
from pymongo import UpdateOne

async def update_courses_with_schools():
    # Get the courses collection
    courses = get_mongodb_collection("courses")
    
    # Create a department to school mapping
    dept_to_school = {}
    with open('data/departments.json') as f:
        import json
        data = json.load(f)
        for school, departments in data['departments'].items():
            for dept in departments:
                dept_to_school[dept] = school

    # Get total count for progress bar
    total_courses = await courses.count_documents({})
    
    # Track missing departments
    missing_depts = Counter()
    
    # Prepare bulk operations
    bulk_operations = []
    batch_size = 1000  # Process in batches of 1000
    
    # Update all course documents with progress bar
    async for course in tqdm(courses.find(), total=total_courses, desc="Processing courses"):
        if 'departments' in course:
            # Track missing departments
            for dept in course['departments']:
                if dept not in dept_to_school:
                    missing_depts[dept] += 1
            
            # Get unique schools for all departments in the course
            schools = list(set(
                dept_to_school.get(dept) 
                for dept in course['departments'] 
                if dept_to_school.get(dept)
            ))
            
            # Add to bulk operations
            bulk_operations.append(
                UpdateOne(
                    {'_id': course['_id']},
                    {'$set': {'school-or-college': schools}}
                )
            )
            
            # Execute batch if we've reached batch_size
            if len(bulk_operations) >= batch_size:
                await courses.bulk_write(bulk_operations)
                bulk_operations = []
    
    # Execute any remaining operations
    if bulk_operations:
        await courses.bulk_write(bulk_operations)
    
    # Print missing departments summary
    if missing_depts:
        print("\nMissing departments and their occurrence count:")
        for dept, count in missing_depts.most_common():
            print(f"- {dept}: {count} times")

if __name__ == "__main__":
    import asyncio
    asyncio.run(update_courses_with_schools())