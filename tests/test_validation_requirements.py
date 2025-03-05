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

from utils.mongodb import get_fields_by_id
from utils.parse_course_code import parse_course_code


async def course_meets_condition(course_id: str, condition: dict):
    
    # for a given filter, there may be multiple criteria (plural)
    # we first assume all criteria met is true until proven otherwise
    # this way, if one criterion isn't satisfied, all_crtierion_satisfied is false
    # and therefore it doesn't match the filter
    for filter in condition['filters']:
        all_criterion_match = True
        
        for criterion_type, criterion in filter.items():
            criterion_satisfied = False
            
            if criterion_type == 'list':
                fields_to_retrieve = ["departments", "course_number"]
                course_data = await get_fields_by_id(course_colelction, course_id, fields_to_retrieve)
                
                # Check if any course in the list matches the current course
                for list_course in criterion:
                    parsed = parse_course_code(list_course)
                    
                    # If course numbers match and there's at least one department in common
                    if (parsed["course_number"] == course_data["course_number"] and 
                        any(dept in course_data["departments"] for dept in parsed["departments"])):
                        criterion_satisfied = True
                        break
            elif criterion_type == 'category':
                fields_to_retrieve = ["formatted_designations"]
                course_data = await get_fields_by_id(course_colelction, course_id, fields_to_retrieve)
                
                for designation in course_data["formatted_designations"]:
                    if criterion in designation:
                        criterion_satisfied = True
                        break
            elif criterion_type == 'level':
                fields_to_retrieve = ["formatted_designations"]
                course_data = await get_fields_by_id(course_colelction, course_id, fields_to_retrieve)
                
                for designation in course_data["formatted_designations"]:
                    for level in criterion:
                        if level in designation:
                            criterion_satisfied = True
                            break
                
            if not criterion_satisfied:
                all_criterion_match = False
                
        if all_criterion_match == True:
            print("GOOD MATCH!!!")


example_condition1 = {
    'description': 'Professional Electives',
    'filters': [
        {'list': ['MATH/COMP SCI 240', 'E C E 204', 'E C E 320', 'E C E 331', 'E C E 332', 'E C E 431']}],
    'validation': {'min_courses': 3}
}

example_condition2 = {
    'description': 'Professional Electives',
     'filters': [
         {'category': 'Biological Science', 'level': ['Intermediate', 'Advanced'] }]
}

test_courses_1 = ['67577f027fd66ec727391b39', '67577f027fd66ec727391b39', '67577f997fd66ec727393c59']
async def main():
    for condition in [example_condition1, example_condition1]:
        for course_id in test_courses_1:
            await course_meets_condition(course_id, condition)
            

if __name__ == "__main__":
    asyncio.run(main())