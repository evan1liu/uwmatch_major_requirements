from motor.motor_asyncio import AsyncIOMotorClient
import sys
from pathlib import Path
import asyncio
import bson
from typing import Dict, Any, Callable, List

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Settings
from utils.mongodb import get_fields_by_id
from utils.parse_course_code import parse_course_code

# Initialize the async MongoDB client
client = AsyncIOMotorClient(Settings.MONGODB_URI)
db = client.uwmatch  # Database name
course_collection = db.courses

# ============================
# Strategy Pattern Handlers for In-Memory Data
# ============================

async def mem_handle_list_criterion(course: dict, criterion: List[str]) -> bool:
    """Handle list criterion with in-memory course data"""
    departments = course.get("departments", [])
    course_number = course.get("course_number", "")
    
    for list_course in criterion:
        parsed = parse_course_code(list_course)
        if (parsed["course_number"] == course_number and 
            any(dept in departments for dept in parsed["departments"])):
            return True
    return False

async def mem_handle_category_criterion(course: dict, criterion: str) -> bool:
    """Handle category criterion with in-memory course data"""
    formatted_designations = course.get("formatted_designations", [])
    return any(criterion in designation for designation in formatted_designations)

async def mem_handle_level_criterion(course: dict, criterion: List[str]) -> bool:
    """Handle level criterion with in-memory course data"""
    formatted_designations = course.get("formatted_designations", [])
    for designation in formatted_designations:
        for level in criterion:
            if level in designation:
                return True
    return False

async def mem_handle_department_criterion(course: dict, criterion: str) -> bool:
    """
    Handle department criterion with in-memory course data
    Checks if a course belongs to a specific department
    """
    departments = course.get("departments", [])
    return criterion in departments

async def mem_handle_course_number_range_criterion(course: dict, criterion: Dict) -> bool:
    """
    Handle course number range criterion with in-memory course data
    Supports MongoDB-style comparison operators for course numbers:
    - $gt (greater than)
    - $gte (greater than or equal)
    - $lt (less than)
    - $lte (less than or equal)
    - $eq (equal)
    - $ne (not equal)
    """
    course_number_str = course.get("course_number", "")
    
    # Extract the numeric part from course number (e.g., "301A" -> 301)
    try:
        # Try to extract just the numeric part from the course number
        course_number = int(''.join(c for c in course_number_str if c.isdigit()))
    except (ValueError, TypeError):
        # If we can't convert to a number, this criterion doesn't match
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
    
    # If we passed all the operator checks, return True
    return True

# Map criterion types to in-memory handlers
mem_criterion_handlers = {
    'list': mem_handle_list_criterion,
    'category': mem_handle_category_criterion,
    'level': mem_handle_level_criterion,
    'department': mem_handle_department_criterion,
    'course_number': mem_handle_course_number_range_criterion,
}

async def course_meets_condition_mem(course: dict, condition: dict) -> bool:
    """Check if a course meets a condition using the strategy pattern with in-memory data"""
    for filter_criteria in condition['filters']:
        all_criterion_match = True
        
        for criterion_type, criterion in filter_criteria.items():
            handler = mem_criterion_handlers.get(criterion_type)
            if handler and not await handler(course, criterion):
                all_criterion_match = False
                break
                
        if all_criterion_match:
            return True
    return False

# ============================
# Hybrid Bulk+Strategy Implementation
# ============================

async def bulk_strategy_check_courses_condition(condition: dict, courses: List[str]) -> dict:
    """
    Check a single condition for multiple courses using bulk MongoDB operations
    but apply the strategy pattern for evaluating criteria
    """
    # Convert string IDs to ObjectIds for MongoDB queries
    course_object_ids = [bson.ObjectId(course_id) for course_id in courses]
    
    # Build an initial pipeline to get the basic course data
    base_pipeline = [
        {"$match": {"_id": {"$in": course_object_ids}}},
        {"$project": {"_id": 1, "course_code": 1, "credits": 1, "departments": 1, 
                      "course_number": 1, "formatted_designations": 1}}
    ]
    
    # Get all relevant course data in a single query
    course_data = await course_collection.aggregate(base_pipeline).to_list(length=None)
    
    # Create a dictionary for faster lookups
    course_dict = {str(course["_id"]): course for course in course_data}
    
    # Process each course against the condition using the strategy pattern
    passing_courses = []
    
    for course in course_data:
        course_id = str(course["_id"])
        course_code = course.get("course_code", "Unknown").replace('\u200b', '')
        
        # Use the strategy pattern with in-memory data
        passes = await course_meets_condition_mem(course, condition)
        
        if passes:
            passing_courses.append((course_code, course_id))
    
    # Calculate total credits from passing courses
    total_credits = sum(course_dict[course_id].get("credits", 0) for _, course_id in passing_courses)
    
    # Prepare validation metrics
    validation_requirements = condition.get("validation", {})
    validation_metrics = {
        "total_passing_courses": len(passing_courses),
        "total_credits": total_credits,
        "validation_status": {}
    }
    
    # Check each validation requirement and record status
    if "min_courses" in validation_requirements:
        min_courses = validation_requirements["min_courses"]
        validation_metrics["validation_status"]["min_courses"] = {
            "required": min_courses,
            "satisfied": len(passing_courses),
            "passed": len(passing_courses) >= min_courses
        }
    
    if "min_credits" in validation_requirements:
        min_credits = validation_requirements["min_credits"]
        validation_metrics["validation_status"]["min_credits"] = {
            "required": min_credits,
            "satisfied": total_credits,
            "passed": total_credits >= min_credits
        }
    
    # Overall validation pass/fail
    validation_metrics["overall_passed"] = all(
        status["passed"] for status in validation_metrics["validation_status"].values()
    ) if validation_metrics["validation_status"] else True
    
    return {
        "description": condition["description"],
        "validation_requirements": validation_requirements,
        "passing_courses": [course for course, _ in passing_courses],
        "metrics": validation_metrics
    }

# ============================
# Interface Functions (using the hybrid approach internally)
# ============================

async def check_condition_for_courses(condition: dict, courses: List[str]) -> dict:
    """
    Check a single condition for multiple courses and return detailed validation results
    """
    return await bulk_strategy_check_courses_condition(condition, courses)

async def check_single_course_condition(course_id: str, condition: dict) -> tuple:
    """
    Check if a single course meets a condition and return tuple with course code, id, and result
    """
    # We'll use the hybrid approach but for a single course
    result = await bulk_strategy_check_courses_condition(condition, [course_id])
    
    # Get course data for the response
    course_data = await get_fields_by_id(course_collection, course_id, ["course_code"])
    course_code = course_data.get("course_code", "Unknown").replace('\u200b', '')
    
    # Return in the expected format
    return (course_code, course_id, course_id in [c.split(" - ")[1] for c in result["passing_courses"]])

async def concurrent_main(courses: List[str], conditions: List[dict]) -> List[dict]:
    """
    Process multiple conditions concurrently, each condition checking all courses
    """
    tasks = []
    for condition in conditions:
        tasks.append(bulk_strategy_check_courses_condition(condition, courses))
    
    results = await asyncio.gather(*tasks)
    return results

# ============================
# Test Data
# ============================

from example_conditions import *
from example_list_of_courses import *

# ============================
# Main Function
# ============================

async def main():
    """
    Run the hybrid implementation with the test data
    """
    print("\nValidation Results by Condition:")
    all_conditions = [example_condition_1, example_condition_2] 
    conditions_results = await concurrent_main(test_courses, all_conditions)
    
    for result in conditions_results:
        print(f"\n=== {result['description']} ===")
        print(f"Validation requirements: {result['validation_requirements']}")
        
        metrics = result['metrics']
        print(f"Overall validation passed: {metrics['overall_passed']}")
        print(f"Total passing courses: {metrics['total_passing_courses']}")
        print(f"Total credits: {metrics['total_credits']}")
        
        # Print detailed validation status
        for req_type, status in metrics['validation_status'].items():
            print(f"{req_type}: {status['satisfied']}/{status['required']} "
                  f"({status['passed'] and 'PASS' or 'FAIL'})")
        
        print("Passing courses:")
        for course in result['passing_courses']:
            print(f"  - {course}")

if __name__ == "__main__":
    asyncio.run(main()) 