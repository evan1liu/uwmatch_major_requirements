"""
Test script for the major validation functionality.

This script tests the MajorRequirementsValidator against student data from MongoDB
to ensure it correctly validates requirements.
"""

import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from major_validation import MajorRequirementsValidator
import pprint
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example list of course IDs a student might have taken
SAMPLE_COURSE_IDS = [
    # Mathematics
    "MATH 221", "MATH 222", "MATH 234", "STAT 311", "MATH 340",
    
    # Science
    "COMP SCI 300", "PHYSICS 207", "PHYSICS 208", "CHEM 109",
    
    # EE Core
    "E C E 203", "E C E 210", "E C E 222", "E C E 230", "E C E 235", 
    "E C E 252", "E C E 270", "E C E 271", "E C E 330",
    "E C E 340", "E C E 352", "E C E 370",
    
    # Advanced Electives
    "E C E 304", "E C E 453", "E C E 320", "E C E 420",
    "E C E 334", "E C E 439", "E C E 342",
    
    # Professional Electives
    "MATH 240", "E C E 204", "COMP SCI 400",
    
    # Communication Skills
    "ENGL 100", "INTEREGR 397",
    
    # Liberal Studies
    "HISTORY 101", "PSYCH 202", "PHILOS 101", "GERMAN 101", "GERMAN 102",
    
    # University General Education
    "COM ARTS 100", "BIOLOGY 101", "BIOLOGY 102", "ECON 101", 
    "HISTORY 160", "MATH 112", "ECON 301", "ENGLISH 201"
]

async def fetch_courses_from_mongodb(course_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch course data from MongoDB based on course IDs
    
    Args:
        course_ids: List of course IDs to fetch
        
    Returns:
        List of course dictionaries with all necessary information
    """
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.get_database("uwmatch")  # Use your actual database name
        courses_collection = db.get_collection("courses")  # Use your actual collection name
        
        # Fetch courses
        cursor = courses_collection.find({"course_code": {"$in": course_ids}})
        courses = await cursor.to_list(length=None)
        
        logger.info(f"Found {len(courses)} courses in MongoDB")
        
        # Transform to the format needed by the validator
        formatted_courses = []
        for course in courses:
            formatted_course = {
                "course_code": course.get("course_code", ""),
                "credits": course.get("credits", 0),
            }
            
            # Add optional fields if they exist
            if "attributes" in course:
                formatted_course["attributes"] = course["attributes"]
            if "breadth" in course:
                formatted_course["breadth"] = course["breadth"]
            if "has_lab" in course:
                formatted_course["has_lab"] = course["has_lab"]
            if "category" in course:
                formatted_course["category"] = course["category"]
            
            formatted_courses.append(formatted_course)
        
        return formatted_courses
    
    except Exception as e:
        logger.error(f"Error fetching courses from MongoDB: {e}")
        return []

def print_requirement_status(result, indent=""):
    """Print a simplified version of requirement fulfillment status"""
    groups = result.get("requirement_groups", [])
    
    print(f"{indent}Major: {result.get('major_name')}")
    print(f"{indent}Total Credits: {result.get('total_credits_earned')}/{result.get('total_credits_required')}")
    print(f"{indent}Overall Status: {'Fulfilled' if result.get('overall_status') else 'Not Fulfilled'}")
    print()
    
    # Print each requirement group status
    for group in groups:
        is_fulfilled = group.get("is_fulfilled", False)
        status = "✅" if is_fulfilled else "❌"
        
        print(f"{indent}{status} {group.get('name')}: {group.get('credits_earned')}/{group.get('credits_required')} credits")
        
        # Print conditions
        for condition in group.get("conditions", []):
            condition_status = "✅" if condition.get("is_fulfilled", False) else "❌"
            print(f"{indent}  {condition_status} {condition.get('description')}: {condition.get('details')}")
            
            # Print areas if present
            if "areas" in condition:
                for area in condition.get("areas", []):
                    area_status = "✅" if area.get("is_fulfilled", False) else "❌"
                    area_credits = area.get("credits", 0)
                    print(f"{indent}    {area_status} {area.get('name')}: {area_credits} credits")
                    
                    # Print courses in this area
                    for course in area.get("courses", []):
                        print(f"{indent}      - {course.get('course_code')} ({course.get('credits')} cr)")
                
                # Print additional requirements if present
                for add_req in condition.get("additional_requirements", []):
                    add_req_status = "✅" if add_req.get("is_fulfilled", False) else "❌"
                    print(f"{indent}    {add_req_status} {add_req.get('description')}: {add_req.get('details')}")
        
        print()
    
    # Print unfulfilled requirements
    if not result.get("overall_status"):
        print(f"{indent}Unfulfilled Requirements:")
        for req in result.get("unfulfilled_requirements", []):
            print(f"{indent}  ❌ {req.get('group_name')}: {req.get('description')}")
            for detail in req.get("details", []):
                print(f"{indent}    - {detail.get('description')}: {detail.get('details')}")
        print()

def test_with_mock_data():
    """Test with mock data if MongoDB is not available"""
    logger.info("Testing with mock data...")
    
    # Sample student course data (this is a fallback if MongoDB is not available)
    sample_student_courses = [
        # Mathematics courses (just a few examples)
        {"course_code": "MATH 221", "credits": 5},
        {"course_code": "MATH 222", "credits": 4},
        {"course_code": "MATH 234", "credits": 4},
        {"course_code": "STAT 311", "credits": 3},
        
        # Science courses (just a few examples)
        {"course_code": "COMP SCI 300", "credits": 3},
        {"course_code": "PHYSICS 207", "credits": 5},
        {"course_code": "PHYSICS 208", "credits": 5}
    ]
    
    # Initialize validator with EE requirements
    validator = MajorRequirementsValidator("ee_major_requirements.json")
    
    # Validate sample student courses
    result = validator.validate_student_courses(sample_student_courses)
    
    # Print results
    print("\n=== VALIDATION RESULTS (MOCK DATA) ===\n")
    print_requirement_status(result)
    
    # Save detailed results to file for examination
    with open("validation_results_mock.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("Detailed mock results saved to validation_results_mock.json")

async def main():
    """Main test function"""
    # Initialize validator with EE requirements
    validator = MajorRequirementsValidator("ee_major_requirements.json")
    
    try:
        # Try to fetch courses from MongoDB
        student_courses = await fetch_courses_from_mongodb(SAMPLE_COURSE_IDS)
        
        if not student_courses:
            # If no courses are found, fall back to mock data
            logger.warning("No courses found in MongoDB, falling back to mock data")
            test_with_mock_data()
            return
        
        # Validate student courses
        result = validator.validate_student_courses(student_courses)
        
        # Print results
        print("\n=== VALIDATION RESULTS ===\n")
        print_requirement_status(result)
        
        # Save detailed results to file for examination
        with open("validation_results.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print("Detailed results saved to validation_results.json")
    
    except Exception as e:
        logger.error(f"Error in main: {e}")
        # Fall back to mock data testing
        test_with_mock_data()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
