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

# ============================
# Strategy Pattern Handlers for In-Memory Data
# ============================

async def mem_handle_list_criterion(course: dict, criterion: List[str]) -> bool:
    """Handle list criterion with in-memory course data"""
    # first, we get the "departments" list from the course dictionary
    departments = course.get("departments", [])
    # then, we get the course_number string from the course dictionary
    course_number = course.get("course_number", "")
    
    # since the list criterion type is a list of course_code, we're iterating through it
    for list_course in criterion:
        # we use the function parse_course_code from utils to convert the course_code string
        # into a dictionary with keys "departments" and "course_number"
        parsed = parse_course_code(list_course)
        # first check if the number is the same
        # if the number doesn't match (first comparitve doesn't pass), then the code doesn't check anymore
        if (parsed["course_number"] == course_number and 
            # then, we check if they have any overlapping department
            # when finds the same department, it stops checking and return True
            any(dept in departments for dept in parsed["departments"])):
            return True
    # after iterating through all the courses, and it hasn't return True yet,
    # that means the course is not in the list, so return False
    return False

async def mem_handle_category_criterion(course: dict, criterion: str) -> bool:
    """Handle category criterion with in-memory course data"""
    
    formatted_designations = course.get("formatted_designations", [])
    # check if the criterion (ex: Biological Science) exists in the string designation (ex: Breath - Biological Science)
    return any(criterion in designation for designation in formatted_designations)

async def mem_handle_level_criterion(course: dict, criterion: List[str]) -> bool:
    """Handle level criterion with in-memory course data"""
    # the "level" also exists in the list of formatted_designations
    formatted_designations = course.get("formatted_designations", [])
    # formatted_designations is just a list of strings
    for designation in formatted_designations:
        # the criterion in level could be a list: ['Intermediate', 'Advanced']
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
    course_number = int(course_number_str)
    
    # for 'course_number' criterion, usually there's an operator and a value to compare the course_number to
    # it could be a list, who knows...
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

# we map the keys of different criteria to a function name
# we'll be deciding which function to use based on the key of the filter dictionary
mem_criterion_handlers = {
    'list': mem_handle_list_criterion,
    'category': mem_handle_category_criterion,
    'level': mem_handle_level_criterion,
    'department': mem_handle_department_criterion,
    'course_number': mem_handle_course_number_range_criterion,
}

async def course_meets_condition_mem(course: dict, condition: dict) -> bool:
    """Check if a course meets a condition using the strategy pattern with in-memory data"""
    # there could be multiple filters exist for a given condition
    # therefore, we have to iterate through all filters
    for filter_criteria in condition['filters']:
        # we first assume all criteria matches
        all_criteria_match = True
        
        # we iterate through the filter items, and seperate the criterion type, and the criterion
        # we use our criterion_type to decide which function to use by using .get on the dictionary 'mem_criterion_handlers' we defined earlier
        for criterion_type, criterion in filter_criteria.items():
            handler = mem_criterion_handlers.get(criterion_type)

            # we feed in the course dict object and the criterion as arguments to the handler
            # each criterion handler returns a boolean value of whether the course fits the criterion
            if handler and not await handler(course, criterion):
                # as soon as a criterion doesn't match, the course doesn't pass the filter
                # since we defined a filter as having many criteria, you must pass all criteria to pass the filter
                all_criteria_match = False
                break
        # if goin
        if all_criteria_match:
            return True
    # if the course doesn't match any filter, then it's defaulted to False
    return False

# ============================
# Hybrid Bulk+Strategy Implementation
# ============================

async def bulk_strategy_check_courses_condition(condition: dict, courses: List[str]) -> dict:
    """
    Check a single condition for multiple courses using bulk MongoDB operations
    but apply the strategy pattern for evaluating criteria
    """
    # we first convert the list of string ids into a list of mongodb's bson ObjectId
    course_object_ids = [bson.ObjectId(course_id) for course_id in courses]
    
    # Build an initial pipeline to get the basic course data
    base_pipeline = [
        {"$match": {"_id": {"$in": course_object_ids}}},
        {"$project": {"_id": 1, "course_code": 1, "credits": 1, "departments": 1, 
                      "course_number": 1, "formatted_designations": 1}}
    ]
    
    # course_data is a list of dictionaries, wht key/value pairs being the field names and values we extracted
    course_data = await course_collection.aggregate(base_pipeline).to_list(length=None)
    
    # convert the list of dictionaries into a dictionary of dictionaries, with each sub-dictionary's key being the course_id
    course_dict = {str(course["_id"]): course for course in course_data}
    
    # first, initiate the passing courses as an empty list
    passing_courses = []
    
    # we iterate through the courses for the given condition
    for course in course_data:
        course_id = str(course["_id"])
        course_code = course.get("course_code", "Unknown").replace('\u200b', '')
        
        # we defined the function 'course_meets_condition_mem' as a function that returns a boolean variable
        condition_passed = await course_meets_condition_mem(course, condition)
        
        if condition_passed:
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

class CourseValidationEngine:
    """
    A recursive engine for validating major requirements against completed courses.
    """
    
    def __init__(self, major_requirements: Dict, course_data: List[Dict]):
        """
        Initialize the validation engine with major requirements and completed courses.
        
        Args:
            major_requirements: The JSON structure defining the major requirements
            course_data: List of completed courses with their metadata
        """
        self.requirements = major_requirements
        self.courses = course_data
        
        # Create dictionaries for faster lookups
        self.course_dict = {str(course["_id"]): course for course in course_data}
        self.course_id_by_code = {course.get("course_code", ""): str(course["_id"]) 
                                 for course in course_data}
        
        # Track which courses have been used to satisfy which requirements
        self.course_usage = defaultdict(set)
        
        # Store validation results for future reference
        self.validation_results = {}
        
    def validate_major(self) -> Dict:
        """
        Validate the entire major requirements against completed courses.
        
        Returns:
            Dict containing validation results for the entire major
        """
        return self._validate_requirement(self.requirements)
    
    def _validate_requirement(self, requirement: Dict, parent_path: str = "") -> Dict:
        """
        Recursively validate a requirement and its sub-requirements.
        
        Args:
            requirement: The requirement to validate
            parent_path: Path string to identify the requirement hierarchy
            
        Returns:
            Dict containing validation results for this requirement
        """
        req_id = requirement.get("id", "unnamed")
        path = f"{parent_path}/{req_id}" if parent_path else req_id
        
        # Check if we've already validated this requirement
        if path in self.validation_results:
            return self.validation_results[path]
        
        # Initialize validation result
        result = {
            "id": req_id,
            "name": requirement.get("name", "Unnamed Requirement"),
            "description": requirement.get("description", ""),
            "satisfied": False,
            "details": {},
            "sub_requirements": []
        }
        
        # If this is a reference to another requirement, follow the reference
        if "reference" in requirement:
            ref_id = requirement["reference"]
            # We need to find the referenced requirement in the full structure
            referenced_req = self._find_requirement_by_id(ref_id)
            if referenced_req:
                ref_result = self._validate_requirement(referenced_req)
                result["satisfied"] = ref_result["satisfied"]
                result["reference_to"] = ref_id
                result["details"] = ref_result["details"]
                self.validation_results[path] = result
                return result
            else:
                result["error"] = f"Referenced requirement '{ref_id}' not found"
                self.validation_results[path] = result
                return result
        
        # Handle different validation types
        validation_type = requirement.get("validation_type", "standard")
        
        if validation_type == "alternative":
            # One of multiple alternative ways must be satisfied
            alternatives_results = []
            satisfied = False
            
            for i, alternative in enumerate(requirement.get("alternatives", [])):
                alt_result = self._validate_alternative(alternative, f"{path}/alt_{i}")
                alternatives_results.append(alt_result)
                if alt_result["satisfied"]:
                    satisfied = True
                    
            result["satisfied"] = satisfied
            result["details"]["alternatives"] = alternatives_results
        
        elif validation_type == "all":
            # All sub-requirements must be satisfied
            sub_results = []
            all_satisfied = True
            
            for i, sub_req in enumerate(requirement.get("requirements", [])):
                sub_result = self._validate_requirement(sub_req, path)
                sub_results.append(sub_result)
                if not sub_result["satisfied"]:
                    all_satisfied = False
            
            result["satisfied"] = all_satisfied
            result["sub_requirements"] = sub_results
        
        else:  # Standard validation
            # Validate against filters and constraints
            validation_metrics = self._validate_filters_and_constraints(requirement, path)
            result["details"] = validation_metrics
            
            # Check if sub-requirements exist and validate them
            if "requirements" in requirement:
                sub_results = []
                for i, sub_req in enumerate(requirement["requirements"]):
                    sub_result = self._validate_requirement(sub_req, path)
                    sub_results.append(sub_result)
                result["sub_requirements"] = sub_results
            
            # Determine if this requirement is satisfied
            result["satisfied"] = self._is_requirement_satisfied(requirement, validation_metrics, 
                                                               result.get("sub_requirements", []))
        
        # Store result for future reference
        self.validation_results[path] = result
        return result
    
    def _validate_alternative(self, alternative: Dict, path: str) -> Dict:
        """
        Validate an alternative requirement.
        
        Args:
            alternative: The alternative requirement configuration
            path: Path string to identify the requirement hierarchy
            
        Returns:
            Dict containing validation results for this alternative
        """
        # An alternative is essentially a standalone requirement
        temp_req = copy.deepcopy(alternative)
        if "id" not in temp_req:
            temp_req["id"] = path.split("/")[-1]
        if "name" not in temp_req:
            temp_req["name"] = "Alternative Option"
            
        return self._validate_requirement(temp_req, path)
    
    def _validate_filters_and_constraints(self, requirement: Dict, path: str) -> Dict:
        """
        Apply filters and constraints to find matching courses.
        
        Args:
            requirement: The requirement configuration
            path: Path string to identify the requirement hierarchy
            
        Returns:
            Dict containing validation metrics (courses that match, credits, etc.)
        """
        # Initialize validation metrics
        metrics = {
            "passing_courses": [],
            "total_credits": 0,
            "total_courses": 0,
            "areas_satisfied": set(),
            "validation_status": {}
        }
        
        # Apply filters to find matching courses
        matching_courses = self._apply_filters(requirement.get("filters", []))
        
        # Apply constraints to filter out invalid courses
        valid_courses = self._apply_constraints(matching_courses, requirement.get("constraints", []), path)
        
        # Calculate metrics
        for course_id, course in valid_courses.items():
            # Check if this course is already used by another requirement
            if self._can_use_course(course_id, path, requirement):
                course_code = course.get("course_code", "Unknown")
                credits = course.get("credits", 0)
                
                metrics["passing_courses"].append((course_code, course_id))
                metrics["total_credits"] += credits
                metrics["total_courses"] += 1
                
                # Track area satisfaction if applicable
                if "area_id" in requirement:
                    metrics["areas_satisfied"].add(requirement["area_id"])
                
                # Mark this course as used by this requirement
                self.course_usage[course_id].add(path)
        
        # Check validation requirements
        validation = requirement.get("validation", {})
        
        if "min_credits" in validation:
            min_credits = validation["min_credits"]
            metrics["validation_status"]["min_credits"] = {
                "required": min_credits,
                "satisfied": metrics["total_credits"],
                "passed": metrics["total_credits"] >= min_credits
            }
        
        if "min_courses" in validation:
            min_courses = validation["min_courses"]
            metrics["validation_status"]["min_courses"] = {
                "required": min_courses,
                "satisfied": metrics["total_courses"],
                "passed": metrics["total_courses"] >= min_courses
            }
            
        if "min_areas" in validation:
            min_areas = validation["min_areas"]
            metrics["validation_status"]["min_areas"] = {
                "required": min_areas,
                "satisfied": len(metrics["areas_satisfied"]),
                "passed": len(metrics["areas_satisfied"]) >= min_areas
            }
        
        if "min_gpa" in validation:
            # This would require student GPA data to be included
            pass
        
        # Convert set to list for JSON serialization
        metrics["areas_satisfied"] = list(metrics["areas_satisfied"])
        
        return metrics
    
    def _apply_filters(self, filters: List[Dict]) -> Dict[str, Dict]:
        """
        Apply filters to find matching courses.
        
        Args:
            filters: List of filter criteria
            
        Returns:
            Dict of course_id -> course for courses that match the filters
        """
        if not filters:
            return {}
        
        matching_courses = {}
        
        # Each filter group is applied separately (OR logic between filter groups)
        for filter_group in filters:
            # Find courses that match this filter group
            group_matches = self._match_filter_group(filter_group)
            
            # Add matches to the overall matching set
            for course_id, course in group_matches.items():
                matching_courses[course_id] = course
                
        return matching_courses
    
    def _match_filter_group(self, filter_group: Dict) -> Dict[str, Dict]:
        """
        Match courses against a single filter group.
        
        Args:
            filter_group: Filter criteria
            
        Returns:
            Dict of course_id -> course for courses that match this filter group
        """
        matching_courses = {}
        
        # Start with all courses and apply each filter criterion
        candidate_courses = dict(self.course_dict)
        
        # Special case: empty filter means any course
        if not filter_group:
            return candidate_courses
            
        # Process "list" filter - direct list of course codes
        if "list" in filter_group:
            course_codes = filter_group["list"]
            list_matches = {}
            
            for code in course_codes:
                if code in self.course_id_by_code:
                    course_id = self.course_id_by_code[code]
                    list_matches[course_id] = self.course_dict[course_id]
            
            # If we have a list filter, we start with only these courses
            candidate_courses = list_matches
            
        # Process "not_list" filter - exclusion list
        if "not_list" in filter_group:
            excluded_codes = filter_group["not_list"]
            excluded_ids = {self.course_id_by_code.get(code) for code in excluded_codes 
                           if code in self.course_id_by_code}
            
            # Remove excluded courses
            for course_id in excluded_ids:
                if course_id in candidate_courses:
                    del candidate_courses[course_id]
        
        # Process department filter
        if "department" in filter_group:
            dept = filter_group["department"]
            dept_matches = {}
            
            for course_id, course in candidate_courses.items():
                if dept in course.get("departments", []):
                    dept_matches[course_id] = course
            
            candidate_courses = dept_matches
            
        # Process not_departments filter
        if "not_departments" in filter_group:
            excluded_depts = filter_group["not_departments"]
            filtered_courses = {}
            
            for course_id, course in candidate_courses.items():
                course_depts = course.get("departments", [])
                if not any(dept in excluded_depts for dept in course_depts):
                    filtered_courses[course_id] = course
            
            candidate_courses = filtered_courses
            
        # Process school filter
        if "school" in filter_group:
            school = filter_group["school"]
            school_matches = {}
            
            for course_id, course in candidate_courses.items():
                if course.get("school") == school:
                    school_matches[course_id] = course
            
            candidate_courses = school_matches
        
        # Process category filter
        if "category" in filter_group:
            category = filter_group["category"]
            category_matches = {}
            
            for course_id, course in candidate_courses.items():
                designations = course.get("formatted_designations", [])
                if any(category in designation for designation in designations):
                    category_matches[course_id] = course
            
            candidate_courses = category_matches
        
        # Process level filter
        if "level" in filter_group:
            levels = filter_group["level"]
            level_matches = {}
            
            for course_id, course in candidate_courses.items():
                designations = course.get("formatted_designations", [])
                if any(any(level in designation for level in levels) for designation in designations):
                    level_matches[course_id] = course
            
            candidate_courses = level_matches
        
        # Process designations filter (H, S, L, Z)
        if "designations" in filter_group:
            valid_designations = filter_group["designations"]
            designation_matches = {}
            
            for course_id, course in candidate_courses.items():
                course_designations = course.get("designations", [])
                if any(designation in valid_designations for designation in course_designations):
                    designation_matches[course_id] = course
            
            candidate_courses = designation_matches
        
        # Process has_lab filter
        if "has_lab" in filter_group and filter_group["has_lab"]:
            lab_matches = {}
            
            for course_id, course in candidate_courses.items():
                if course.get("has_lab", False):
                    lab_matches[course_id] = course
            
            candidate_courses = lab_matches
        
        # Process course_number filter with MongoDB-style operators
        if "course_number" in filter_group:
            number_criteria = filter_group["course_number"]
            number_matches = {}
            
            for course_id, course in candidate_courses.items():
                course_number = course.get("course_number", 0)
                if isinstance(course_number, str):
                    try:
                        course_number = int(course_number)
                    except ValueError:
                        continue
                
                matches = True
                for operator, value in number_criteria.items():
                    if operator == "$gt" and not (course_number > value):
                        matches = False
                        break
                    elif operator == "$gte" and not (course_number >= value):
                        matches = False
                        break
                    elif operator == "$lt" and not (course_number < value):
                        matches = False
                        break
                    elif operator == "$lte" and not (course_number <= value):
                        matches = False
                        break
                    elif operator == "$eq" and not (course_number == value):
                        matches = False
                        break
                    elif operator == "$ne" and not (course_number != value):
                        matches = False
                        break
                
                if matches:
                    number_matches[course_id] = course
            
            candidate_courses = number_matches
        
        return candidate_courses
    
    def _apply_constraints(self, courses: Dict[str, Dict], constraints: List[Dict], path: str) -> Dict[str, Dict]:
        """
        Apply constraints to filter out invalid courses.
        
        Args:
            courses: Dict of course_id -> course
            constraints: List of constraint specifications
            path: Path string to identify the requirement hierarchy
            
        Returns:
            Dict of course_id -> course for courses that pass all constraints
        """
        if not constraints:
            return courses
        
        valid_courses = dict(courses)
        
        for constraint in constraints:
            constraint_type = constraint.get("type", "")
            
            if constraint_type == "courses_from_list":
                # Constraint that courses must be from a specific list
                allowed_courses = constraint.get("courses_from_list", [])
                allowed_ids = {self.course_id_by_code.get(code) for code in allowed_courses 
                             if code in self.course_id_by_code}
                
                filtered_courses = {}
                for course_id, course in valid_courses.items():
                    if course_id in allowed_ids:
                        filtered_courses[course_id] = course
                
                valid_courses = filtered_courses
            
            elif constraint_type == "exclusion":
                # Constraint that certain course combinations are not allowed
                exclusive_groups = constraint.get("exclusive_groups", [])
                
                for group in exclusive_groups:
                    group_ids = {self.course_id_by_code.get(code) for code in group 
                               if code in self.course_id_by_code}
                    
                    # Count how many courses from this group are in our valid courses
                    matched_courses = [cid for cid in valid_courses if cid in group_ids]
                    
                    # If more than one course matches, keep only the first one
                    if len(matched_courses) > 1:
                        for cid in matched_courses[1:]:
                            del valid_courses[cid]
            
            elif constraint_type == "max_credits":
                # Constraint on maximum credits from a specific source
                filters = constraint.get("filters", [])
                max_credits = constraint.get("max_credits", 0)
                
                # Find courses that match these filters
                constrained_courses = self._apply_filters(filters)
                
                # Calculate total credits for these courses
                constrained_ids = set(constrained_courses.keys())
                current_credits = sum(course.get("credits", 0) for course_id, course in valid_courses.items() 
                                    if course_id in constrained_ids)
                
                # If over the limit, remove courses to get under the limit
                if current_credits > max_credits:
                    excess_credits = current_credits - max_credits
                    courses_to_remove = []
                    
                    # Sort constrained courses by credits (lowest first)
                    sorted_courses = sorted(
                        [(cid, valid_courses[cid]) for cid in valid_courses if cid in constrained_ids],
                        key=lambda x: x[1].get("credits", 0)
                    )
                    
                    # Remove courses until we're under the limit
                    for course_id, course in sorted_courses:
                        credits = course.get("credits", 0)
                        courses_to_remove.append(course_id)
                        excess_credits -= credits
                        if excess_credits <= 0:
                            break
                    
                    # Remove the identified courses
                    for course_id in courses_to_remove:
                        if course_id in valid_courses:
                            del valid_courses[course_id]
            
            elif constraint_type == "min_areas":
                # This is handled at a higher level in the validation process
                pass
            
            elif constraint_type == "course_credits":
                # Constraint requiring minimum credits matching specific filters
                # This is usually handled at a higher level, but we can check it here
                pass
            
            elif constraint_type == "fulfillment_source":
                # This is an informational constraint, no validation needed
                pass
        
        return valid_courses
    
    def _can_use_course(self, course_id: str, req_path: str, requirement: Dict) -> bool:
        """
        Check if a course can be used to satisfy a requirement.
        
        Args:
            course_id: The course identifier
            req_path: Path string identifying the requirement
            requirement: The requirement configuration
            
        Returns:
            Boolean indicating if the course can be used for this requirement
        """
        # If the course hasn't been used yet, it can be used
        if course_id not in self.course_usage:
            return True
        
        # If this exact requirement has already used this course, don't double-count it
        if req_path in self.course_usage[course_id]:
            return False
        
        # Check if course usage exclusivity is defined
        constraints = requirement.get("constraints", [])
        exclusive_usage = True  # Default to exclusive usage
        
        for constraint in constraints:
            if constraint.get("type") == "shared_usage" and constraint.get("allowed", False):
                exclusive_usage = False
                break
        
        # If exclusive usage and the course is already used, don't allow it
        if exclusive_usage and self.course_usage[course_id]:
            # Check for special "satisfies_additional" property
            if "satisfies_additional" in requirement:
                return True
        
        return False

if __name__ == "__main__":
    asyncio.run(main()) 