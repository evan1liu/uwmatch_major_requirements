"""
EE Major Requirements MongoDB Validator

This module provides functions to validate EE major requirements against courses in MongoDB.
"""

import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import bson
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "uwmatch"
COURSE_COLLECTION = "courses"

# Initialize MongoDB client
client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]
course_collection = db[COURSE_COLLECTION]

# Test course IDs from the example
TEST_COURSE_IDS = [
    '67577f027fd66ec727391b39',  # First test course
    '67577f997fd66ec727393c59',  # Another test course
    '67577f147fd66ec727391eed',  # Additional test course
    '67577eec7fd66ec72739161f',
    '67577f067fd66ec727391bfc',
    '67577f7e7fd66ec727393650',
    '67577f1d7fd66ec7273920cb',
    '67577efb7fd66ec72739197d',
    '67577f557fd66ec727392d4c' Additional test course
]

# ===== Helper Functions =====

async def handle_list_criterion(course: dict, criterion: List[str]) -> bool:
    """Handle list criterion with in-memory course data"""
    course_code = course.get("course_code", "")
    
    for list_course in criterion:
        if course_code == list_course:
            return True
            
        # Handle cross-listed courses (with slashes)
        if "/" in list_course and course_code in list_course.split("/"):
            return True
        
        # Handle course codes with 'or'
        if " or " in list_course and course_code in list_course.split(" or "):
            return True
            
    return False

async def handle_department_criterion(course: dict, criterion: str) -> bool:
    """Handle department criterion with in-memory course data"""
    departments = course.get("departments", [])
    
    if not departments and "course_code" in course:
        # Extract department from course_code if department field is not available
        course_code = course.get("course_code", "")
        if " " in course_code:
            dept = course_code.split()[0]
            departments = [dept]
    
    return criterion in departments

async def handle_course_number_criterion(course: dict, criterion: Dict) -> bool:
    """Handle course number criterion with in-memory course data"""
    course_code = course.get("course_code", "")
    
    # Extract course number from course code
    if " " in course_code:
        try:
            course_number = int(''.join(c for c in course_code.split()[1] if c.isdigit()))
        except (ValueError, IndexError):
            return False
    else:
        return False
    
    # Check each comparison operator
    for operator, value in criterion.items():
        if operator == "$gt" and not (course_number > value):
            return False
        elif operator == "$gte" and not (course_number >= value):
            return False
        elif operator == "$lt" and not (course_number < value):
            return False
        elif operator == "$lte" and not (course_number <= value):
            return False
        elif operator == "$eq" and not (course_number == value):
            return False
        elif operator == "$ne" and not (course_number != value):
            return False
    
    return True

async def handle_category_criterion(course: dict, criterion: str) -> bool:
    """Handle category criterion with in-memory course data"""
    # For biology and zoology courses, match Biological Science
    if criterion == "Biological Science" and any(dept in ["BIOLOGY", "ZOOLOGY", "ENTOM"] 
                                               for dept in course.get("departments", [])):
        return True
        
    # For physics courses, match Physical Science
    if criterion == "Physical Science" and "PHYSICS" in course.get("departments", []):
        return True
        
    # For EE courses, match Engineering category
    if criterion == "Engineering" and "E C E" in course.get("departments", []):
        return True
    
    # Check if the category is directly in course attributes
    category = course.get("category", "")
    attributes = course.get("attributes", [])
    
    return criterion == category or criterion in attributes

async def handle_level_criterion(course: dict, criterion: List[str]) -> bool:
    """Handle level criterion with in-memory course data"""
    # For courses with number 300+, consider them "Advanced"
    # For courses 200-299, consider them "Intermediate"
    course_code = course.get("course_code", "")
    
    if " " in course_code:
        try:
            course_number = int(''.join(c for c in course_code.split()[1] if c.isdigit()))
            
            if "Advanced" in criterion and course_number >= 300:
                return True
                
            if "Intermediate" in criterion and course_number >= 200 and course_number < 300:
                return True
        except (ValueError, IndexError):
            pass
    
    # Also check if level is explicitly in attributes
    attributes = course.get("attributes", [])
    return any(level in attributes for level in criterion)

async def handle_attribute_criterion(course: dict, criterion) -> bool:
    """Handle attribute criterion with in-memory course data"""
    attributes = course.get("attributes", [])
    
    if isinstance(criterion, list):
        return any(attr in attributes for attr in criterion)
    return criterion in attributes

async def handle_breadth_criterion(course: dict, criterion: str) -> bool:
    """Handle breadth criterion with in-memory course data"""
    breadth = course.get("breadth", "")
    return breadth == criterion

async def handle_exclude_criterion(course: dict, criterion: List[str]) -> bool:
    """Handle exclude criterion - return True if course is NOT in excluded list"""
    course_code = course.get("course_code", "")
    
    # If it's a single department exclusion
    if isinstance(criterion, str):
        departments = course.get("departments", [])
        return criterion not in departments
    
    # If it's an exclusion list of course codes
    for excluded_course in criterion:
        if course_code == excluded_course:
            return False
        if "/" in excluded_course and course_code in excluded_course.split("/"):
            return False
    
    return True

async def handle_school_criterion(course: dict, criterion: str) -> bool:
    """Handle school criterion with in-memory course data"""
    school = course.get("school", "")
    # Some courses might store school in attributes or other fields
    attributes = course.get("attributes", [])
    departments = course.get("departments", [])
    
    # If school field exists, check direct match
    if school:
        return school == criterion
    
    # Check if the school is in attributes
    if criterion in attributes:
        return True
    
    # For UW-Madison, certain department prefixes might indicate school
    if criterion == "College of Engineering" or criterion == "Engineering":
        engineering_depts = ["E C E", "E M A", "M E", "CBE", "B M E", "INTEREGR"]
        for dept in departments:
            if dept in engineering_depts:
                return True
    elif criterion == "College of Letters & Science":
        ls_depts = ["COMP SCI", "MATH", "PHYSICS", "CHEM", "BIOLOGY", "ZOOLOGY"]
        for dept in departments:
            if dept in ls_depts:
                return True
    elif criterion == "Business":
        business_depts = ["ACCT", "FINANCE", "MARKETNG", "M H R", "OTM", "REAL EST"]
        for dept in departments:
            if dept in business_depts:
                return True
    
    return False

async def handle_exclude_departments_criterion(course: dict, criterion: List[str]) -> bool:
    """Handle exclude_departments criterion - return True if course departments are NOT in excluded list"""
    departments = course.get("departments", [])
    
    # If departments is empty, extract from course_code
    if not departments and "course_code" in course:
        course_code = course.get("course_code", "")
        if " " in course_code:
            dept = course_code.split()[0]
            departments = [dept]
    
    # Check if any of the course's departments are in the exclude list
    for dept in departments:
        if dept in criterion:
            return False
    
    return True

# Map criterion types to handlers
criterion_handlers = {
    'list': handle_list_criterion,
    'department': handle_department_criterion,
    'course_number': handle_course_number_criterion,
    'category': handle_category_criterion,
    'level': handle_level_criterion,
    'attribute': handle_attribute_criterion,
    'breadth': handle_breadth_criterion,
    'exclude': handle_exclude_criterion,
    'school': handle_school_criterion,
    'exclude_departments': handle_exclude_departments_criterion
}

async def course_meets_filter(course: dict, filter_item: dict) -> bool:
    """Check if a course meets all criteria in a filter item"""
    for criterion_type, criterion_value in filter_item.items():
        handler = criterion_handlers.get(criterion_type)
        if handler:
            if not await handler(course, criterion_value):
                return False
        else:
            print(f"Warning: No handler for criterion type '{criterion_type}'")
    return True

async def course_meets_condition(course: dict, condition: dict) -> bool:
    """Check if a course meets any filter in a condition's filters list"""
    for filter_item in condition.get('filters', []):
        if await course_meets_filter(course, filter_item):
            return True
    return False

async def validate_condition(condition: dict, courses: List[dict]) -> dict:
    """Validate a condition against a list of courses"""
    passing_courses = []
    course_codes = []
    course_details = []
    
    for course in courses:
        if await course_meets_condition(course, condition):
            passing_courses.append(course)
            course_code = course.get("course_code", "Unknown")
            course_codes.append(course_code)
            
            # Save details about which criteria were matched for debugging
            course_details.append({
                "course_code": course_code,
                "departments": course.get("departments", []),
                "credits": course.get("credits", 0)
            })
    
    # Calculate total credits
    total_credits = sum(course.get("credits", 0) for course in passing_courses)
    total_courses = len(passing_courses)
    
    # Prepare validation metrics
    validation = condition.get("validation", {})
    passed = True
    
    validation_status = {}
    
    if "min_courses" in validation:
        min_courses = validation["min_courses"]
        courses_passed = total_courses >= min_courses
        passed = passed and courses_passed
        validation_status["min_courses"] = {
            "required": min_courses,
            "actual": total_courses,
            "passed": courses_passed
        }
    
    if "min_credits" in validation:
        min_credits = validation["min_credits"]
        credits_passed = total_credits >= min_credits
        passed = passed and credits_passed
        validation_status["min_credits"] = {
            "required": min_credits,
            "actual": total_credits,
            "passed": credits_passed
        }
    
    # If no validation requirements, consider it passed if there's at least one passing course
    if not validation and total_courses > 0:
        passed = True
    
    return {
        "description": condition.get("description", "Unknown Condition"),
        "passed": passed,
        "validation_status": validation_status,
        "passing_courses": course_codes,
        "total_credits": total_credits,
        "total_courses": total_courses,
        "course_details": course_details
    }

async def fetch_courses_by_ids(course_ids: List[str]) -> List[dict]:
    """Fetch courses from MongoDB by their IDs"""
    try:
        # Convert string IDs to ObjectIds
        object_ids = [bson.ObjectId(id) for id in course_ids]
        
        # Fetch courses from MongoDB
        cursor = course_collection.find({"_id": {"$in": object_ids}})
        courses = await cursor.to_list(length=None)
        
        return courses
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return []

async def convert_ee_json_to_conditions(json_file: str) -> List[dict]:
    """Convert EE major requirements JSON to condition dictionaries"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    conditions = []
    
    # Process each requirement group
    for group in data.get("requirement_groups", []):
        group_name = group.get("name", "Unknown Group")
        
        # Process each condition in the group
        for condition in group.get("conditions", []):
            condition_dict = {
                "description": f"{group_name}: {condition.get('description', 'Unknown')}",
                "filters": condition.get("filters", []),
                "validation": condition.get("validation", {})
            }
            conditions.append(condition_dict)
            
            # Handle areas if present
            if "areas" in condition:
                for area in condition.get("areas", []):
                    area_dict = {
                        "description": f"{group_name}: {condition.get('description', 'Unknown')} - {area.get('name', 'Unknown Area')}",
                        "filters": area.get("filters", []),
                        "validation": area.get("validation", {})
                    }
                    conditions.append(area_dict)
    
    return conditions

async def get_test_course_info():
    """Print information about the test courses"""
    courses = await fetch_courses_by_ids(TEST_COURSE_IDS)
    print(f"Found {len(courses)} test courses:")
    
    for course in courses:
        course_id = str(course.get("_id"))
        course_code = course.get("course_code", "Unknown")
        course_title = course.get("clean_title", "Unknown")
        credits = course.get("credits", 0)
        
        # Show additional details if available
        departments = course.get("departments", [])
        breadth = course.get("breadth", "")
        attributes = course.get("attributes", [])
        
        print(f"  {course_code} ({credits} cr): {course_title} [ID: {course_id}]")
        
        if departments or breadth or attributes:
            details = []
            if departments:
                details.append(f"Departments: {', '.join(departments)}")
            if breadth:
                details.append(f"Breadth: {breadth}")
            if attributes:
                details.append(f"Attributes: {', '.join(attributes[:3])}")
                if len(attributes) > 3:
                    details[-1] += f" (+{len(attributes)-3} more)"
            
            print(f"    {'; '.join(details)}")
    
    return courses

async def validate_ee_requirements():
    """Validate EE major requirements against test courses"""
    print("\n=== VALIDATING EE MAJOR REQUIREMENTS ===\n")
    
    # Fetch test courses
    courses = await get_test_course_info()
    
    if not courses:
        print("Error: No test courses found in MongoDB.")
        return
    
    # Convert EE requirements to conditions
    conditions = await convert_ee_json_to_conditions("ee_major_requirements.json")
    print(f"\nConverted {len(conditions)} conditions from EE requirements JSON.")
    
    # Test with a few conditions first
    test_conditions = conditions[:5]
    print(f"\nTesting first {len(test_conditions)} conditions:")
    
    for i, condition in enumerate(test_conditions):
        print(f"{i+1}. {condition['description']}")
    
    print("\nValidating test courses against conditions...\n")
    
    # Find the Professional Electives condition
    professional_electives_condition = None
    for condition in conditions:
        if "Professional Electives" in condition.get('description', ''):
            professional_electives_condition = condition
            break
    
    if professional_electives_condition:
        print("\n--- Testing Professional Electives Criteria ---")
        print(f"Condition Description: {professional_electives_condition['description']}")
        print("Filters:")
        for i, filter_item in enumerate(professional_electives_condition.get('filters', [])):
            print(f"  Filter {i+1}: {filter_item}")
            
        # Test each course individually against the professional electives criteria
        print("\nTesting each course against Professional Electives criteria:")
        for course in courses:
            course_code = course.get("course_code", "Unknown")
            departments = course.get("departments", [])
            result = await course_meets_condition(course, professional_electives_condition)
            if result:
                print(f"  {course_code} ({', '.join(departments)}) matches Professional Electives criteria")
            else:
                print(f"  {course_code} ({', '.join(departments)}) does NOT match Professional Electives criteria")
        
        print("\n--- End of Professional Electives Test ---\n")
    
    # Validate each condition
    results = []
    for condition in conditions:
        result = await validate_condition(condition, courses)
        results.append(result)
        
        # Print result
        status = "" if result["passed"] else ""
        print(f"{status} {result['description']}")
        
        # Print validation details
        for key, status in result.get("validation_status", {}).items():
            if key == "min_courses":
                print(f"   Courses: {status['actual']}/{status['required']} {'' if status['passed'] else ''}")
            elif key == "min_credits":
                print(f"   Credits: {status['actual']}/{status['required']} {'' if status['passed'] else ''}")
        
        # Print passing courses (limit to 5 for readability)
        passing_courses = result.get("passing_courses", [])
        if passing_courses:
            print(f"   Passing courses ({len(passing_courses)}):")
            for course in passing_courses[:5]:
                print(f"     - {course}")
            if len(passing_courses) > 5:
                print(f"     - ... and {len(passing_courses) - 5} more")
        print()
    
    # Calculate overall progress
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    
    print(f"\nOverall Progress: {passed_count}/{total_count} requirements satisfied ({passed_count/total_count*100:.1f}%)")
    
    # Save results to file
    with open("ee_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nDetailed results saved to ee_validation_results.json")
    
    # Suggestion for next steps
    print("\nSuggested Next Steps:")
    print("1. Add more test courses to cover the requirements that are not currently being met")
    print("2. Adjust filter criteria if certain courses aren't matching correctly")
    print("3. Integrate this validation logic with your API for student-facing validation")

async def main():
    """Main function"""
    try:
        await validate_ee_requirements()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close MongoDB connection
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
