import json
from typing import Any, Dict, List, Union
from utils.parse_course_code import parse_course_code

class RecursiveMajorValidator:
    def __init__(self, major_requirements: Dict[str, Any], completed_courses: List[Dict[str, Any]]):
        """
        major_requirements: JSON-like dict describing the major.
        completed_courses: list of dicts, each describing a course the student completed.
                          Example: { "_id": "abc123", "course_code": "MATH 222", "credits": 4, "departments": ["MATH"], ...}
        """
        self.major_requirements = major_requirements
        self.courses = completed_courses
        # Convert list of courses -> dict keyed by course_code for fast lookups
        self.course_dict = {c["course_code"]: c for c in completed_courses}

    def validate_major(self) -> Dict[str, Any]:
        """Validate the entire major from the top-level requirement object."""
        overall = self._validate_requirement(self.major_requirements)
        return overall

    def _validate_requirement(self, requirement: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively evaluate single requirement or sub-requirement.
        Return dict with 'satisfied' (bool), 'details' (dict), plus any other data we want to show.
        """
        result = {
            "id": requirement.get("id", ""),
            "name": requirement.get("name", ""),
            "description": requirement.get("description", ""),
            "satisfied": False,
            "details": {}
        }

        # If we have multiple subrequirements under this requirement
        if "requirements" in requirement and requirement.get("validation_type") == "all":
            # "all" means all subrequirements must be satisfied
            subresults = []
            all_satisfied = True
            for sub_req in requirement["requirements"]:
                sr = self._validate_requirement(sub_req)
                subresults.append(sr)
                if not sr["satisfied"]:
                    all_satisfied = False
            result["satisfied"] = all_satisfied
            result["details"]["sub_requirements"] = subresults

        elif "alternatives" in requirement and requirement.get("validation_type") == "alternative":
            # "alternative" means at least one sub-path is satisfied
            altresults = []
            any_satisfied = False
            for altreq in requirement["alternatives"]:
                sr = self._validate_requirement(altreq)
                altresults.append(sr)
                if sr["satisfied"]:
                    any_satisfied = True
            result["satisfied"] = any_satisfied
            result["details"]["alternatives"] = altresults

        else:
            # "standard" requirement: check if it has subrequirements plus local filters
            subresults = []
            if "requirements" in requirement:
                for sub_req in requirement["requirements"]:
                    sr = self._validate_requirement(sub_req)
                    subresults.append(sr)
            result["details"]["sub_requirements"] = subresults

            # Evaluate local filters & validation metrics
            validation_metrics = self._apply_filters_and_validation(
                requirement.get("filters", []),
                requirement.get("validation", {})
            )
            # If subrequirements exist, final satisfaction usually checks local + subrequirements
            # But you can tailor this logic to your exact preference
            sub_all_satisfied = all(sr["satisfied"] for sr in subresults)
            current_satisfied = validation_metrics["passed"]

            # Combine them or pick your own logic:
            result["satisfied"] = current_satisfied and sub_all_satisfied
            result["details"]["validation_metrics"] = validation_metrics

        return result

    def _apply_filters_and_validation(self, filters: List[Dict[str, Any]], validation: Dict[str, Any]) -> Dict[str, Any]:
        """Select courses passing any filter group, then check min_credits, min_courses, etc."""
        # If no filters, no courses match by default. Or interpret it as "all courses" if you prefer.
        matching_courses = []
        for group in filters:
            group_matches = self._match_filter_group(group)
            matching_courses.extend(group_matches)

        # Remove duplicates
        matching_courses = list({mc["course_code"]: mc for mc in matching_courses}.values())

        # Calculate metrics
        total_credits = sum(c.get("credits", 0) for c in matching_courses)
        total_courses = len(matching_courses)

        # Check validation
        min_credit_req = validation.get("min_credits", 0)
        min_course_req = validation.get("min_courses", 0)

        passed_credits = (total_credits >= min_credit_req)
        passed_courses = (total_courses >= min_course_req)

        return {
            "matching_courses": [c["course_code"] for c in matching_courses],
            "total_credits": total_credits,
            "total_courses": total_courses,
            "passed": passed_credits and passed_courses
        }

    def _match_filter_group(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return courses that match all 'criteria' in one filter group (logical AND)."""
        filtered = list(self.courses)
        
        if "list" in criteria:
            course_list = criteria["list"]
            matching_courses = []
            
            for course in filtered:
                # Student course data already has structured fields
                course_departments = course.get("departments", [])
                course_number = str(course.get("course_number", ""))
                
                # For each course code in the filter list
                for list_code in course_list:
                    # Parse the requirement's course code
                    parsed = parse_course_code(list_code)
                    if not parsed:
                        continue
                    
                    list_departments = parsed["departments"]
                    list_number = parsed["course_number"]
                    
                    # Check if course number matches
                    if course_number != list_number:
                        continue
                    
                    # Check if all required departments are present (regardless of order)
                    if all(dept in course_departments for dept in list_departments):
                        matching_courses.append(course)
                        break
            
            filtered = matching_courses
        
        # Modified category matching to look for substring
        if "category" in criteria:
            cat = criteria["category"]
            filtered = [c for c in filtered if any(cat in designation for designation in c.get("formatted_designations", []))]

        if "has_lab" in criteria:
            if criteria["has_lab"]:
                filtered = [c for c in filtered if c.get("has_lab", False)]

        if "department" in criteria:
            dept = criteria["department"]
            filtered = [c for c in filtered if dept in c.get("departments", [])]

        if "course_number" in criteria:
            ops = criteria["course_number"]
            for op, val in ops.items():
                course_num_val = val
                
                if op == "$gte":
                    filtered = [c for c in filtered if int(c.get("course_number", 0)) >= course_num_val]
                elif op == "$gt":
                    filtered = [c for c in filtered if int(c.get("course_number", 0)) > course_num_val]
                elif op == "$lte":
                    filtered = [c for c in filtered if int(c.get("course_number", 0)) <= course_num_val]
                elif op == "$lt":
                    filtered = [c for c in filtered if int(c.get("course_number", 0)) < course_num_val]
                elif op == "$eq":
                    filtered = [c for c in filtered if int(c.get("course_number", 0)) == course_num_val]
                elif op == "$ne":
                    filtered = [c for c in filtered if int(c.get("course_number", 0)) != course_num_val]
        
        return filtered


from motor.motor_asyncio import AsyncIOMotorClient
import sys
from pathlib import Path
import asyncio
import bson
from typing import Dict, Any, Callable, List, Set, Optional, Tuple
from collections import defaultdict
import copy

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Settings
from utils.mongodb import get_fields_by_id
from utils.parse_course_code import parse_course_code

# Initialize the async MongoDB client
client = AsyncIOMotorClient(Settings.MONGODB_URI)
db = client.uwmatch  # Database name
course_collection = db.courses

async def get_course_information(list_of_string_courseids: list[str]) -> list[dict[str]]:
        # we first convert the list of string ids into a list of mongodb's bson ObjectId
    course_object_ids = [bson.ObjectId(course_id) for course_id in list_of_string_courseids]
    
    # Build an initial pipeline to get the basic course data
    base_pipeline = [
        {"$match": {"_id": {"$in": course_object_ids}}},
        {"$project": {"_id": 1, "course_code": 1, "credits": 1, "departments": 1, 
                      "course_number": 1, "formatted_designations": 1}}
    ]
    
    # course_data is a list of dictionaries, wht key/value pairs being the field names and values we extracted
    course_data = await course_collection.aggregate(base_pipeline).to_list(length=None)
    for course in course_data:
        print(course)
    return course_data
    
# Create a main async function to wrap everything
async def main():
    # Load major requirements from JSON
    with open("app/validation/EERequirements.json") as f:
        ee_major = json.load(f)

    # Basic student courses 
    student_courses = [
        {"course_code": "MATH/STAT 221", "credits": 5, "departments": ["MATH", "STAT"], "course_number": 221},
        {"course_code": "MATH 222", "credits": 4, "departments": ["MATH"], "course_number": 222},
        {"course_code": "GENED 110", "credits": 3, "formatted_designations": ["Humanities"]},
        {"course_code": "BIOLOGY 101", "credits": 4, "formatted_designations": ["Natural Science"], "has_lab": True}
    ]
    
    from example_list_of_courses import test_courses
    
    # Get additional courses from database - now with await
    db_courses = await get_course_information(test_courses)
    student_courses.extend(db_courses)

    validator = RecursiveMajorValidator(ee_major, student_courses)
    results = validator.validate_major()
    print(json.dumps(results, indent=2))

# Use asyncio to run the main function
if __name__ == "__main__":
    asyncio.run(main())