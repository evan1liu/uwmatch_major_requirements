"""
Major Requirements Validation Module

This module contains functions to validate a student's course history against major requirements.
It provides detailed information on which requirements are fulfilled and which are not.
"""

import json
from typing import List, Dict, Any, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MajorRequirementsValidator:
    """Validator for major requirements based on the JSON schema"""
    
    def __init__(self, major_requirements_path: str):
        """
        Initialize the validator with a path to the major requirements JSON file
        
        Args:
            major_requirements_path: Path to the JSON file containing major requirements
        """
        self.requirements = self._load_requirements(major_requirements_path)
        self.major_name = self.requirements.get("major_name", "Unknown Major")
        self.total_credits_required = self.requirements.get("total_credits_required", 0)
    
    def _load_requirements(self, path: str) -> Dict[str, Any]:
        """
        Load the requirements from a JSON file
        
        Args:
            path: Path to the JSON file
        
        Returns:
            Dictionary containing the requirements data
        """
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading requirements file: {e}")
            return {}
    
    def validate_student_courses(self, student_courses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a student's courses against the major requirements
        
        Args:
            student_courses: List of course dictionaries, each containing at least:
                - course_code: The course code (e.g., "MATH 221")
                - credits: Number of credits for the course
                - grade: Grade received (optional)
                
        Returns:
            Dictionary with validation results containing:
            - overall_status: Whether all requirements are fulfilled
            - total_credits: Sum of all credits from courses that count toward the major
            - requirements_status: Detailed information about each requirement group
            - unfulfilled_requirements: List of requirements that are not yet fulfilled
        """
        if not self.requirements:
            return {"error": "No requirements loaded"}
        
        # Initialize result structure
        result = {
            "major_name": self.major_name,
            "total_credits_required": self.total_credits_required,
            "total_credits_earned": 0,
            "overall_status": False,
            "requirement_groups": [],
            "unfulfilled_requirements": []
        }
        
        # Process each requirement group
        for group in self.requirements.get("requirement_groups", []):
            group_result = self._validate_requirement_group(group, student_courses)
            result["requirement_groups"].append(group_result)
            
            # Add credits from this group to total
            result["total_credits_earned"] += group_result.get("credits_earned", 0)
            
            # Track unfulfilled requirements
            if not group_result.get("is_fulfilled", False) and not group.get("optional", False):
                result["unfulfilled_requirements"].append({
                    "group_name": group.get("name", "Unnamed Group"),
                    "description": group.get("description", ""),
                    "details": group_result.get("unfulfilled_conditions", [])
                })
        
        # Determine overall status - all non-optional requirements must be fulfilled
        result["overall_status"] = len(result["unfulfilled_requirements"]) == 0
        
        return result
    
    def _validate_requirement_group(self, group: Dict[str, Any], student_courses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a single requirement group
        
        Args:
            group: Dictionary containing the requirement group data
            student_courses: List of student course dictionaries
            
        Returns:
            Dictionary with validation results for this group
        """
        group_name = group.get("name", "Unnamed Group")
        credits_required = group.get("credits_required", 0)
        
        result = {
            "name": group_name,
            "description": group.get("description", ""),
            "credits_required": credits_required,
            "credits_earned": 0,
            "conditions": [],
            "unfulfilled_conditions": [],
            "is_fulfilled": False,
            "courses_applied": []
        }
        
        # Process conditions within the group
        all_conditions_fulfilled = True
        for condition in group.get("conditions", []):
            condition_result = self._validate_condition(condition, student_courses)
            result["conditions"].append(condition_result)
            
            # Add credits from this condition
            result["credits_earned"] += condition_result.get("credits_earned", 0)
            
            # Add courses applied to this condition
            result["courses_applied"].extend(condition_result.get("courses_applied", []))
            
            # Track if any required condition is not fulfilled
            if not condition_result.get("is_fulfilled", False):
                all_conditions_fulfilled = False
                result["unfulfilled_conditions"].append({
                    "description": condition.get("description", "Unnamed Condition"),
                    "details": condition_result.get("details", "")
                })
        
        # Check if the group has enough credits and all conditions are fulfilled
        if "credits_required" in group:
            credits_fulfilled = result["credits_earned"] >= credits_required
            result["is_fulfilled"] = all_conditions_fulfilled and credits_fulfilled
            
            if not credits_fulfilled:
                result["unfulfilled_conditions"].append({
                    "description": f"Credit Requirement",
                    "details": f"Need {credits_required} credits, earned {result['credits_earned']}"
                })
        else:
            # If no credit requirement, only check conditions
            result["is_fulfilled"] = all_conditions_fulfilled
        
        # Remove duplicate courses
        result["courses_applied"] = list({c["course_code"]: c for c in result["courses_applied"]}.values())
        
        return result
    
    def _validate_condition(self, condition: Dict[str, Any], student_courses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a single condition within a requirement group
        
        Args:
            condition: Dictionary containing the condition data
            student_courses: List of student course dictionaries
            
        Returns:
            Dictionary with validation results for this condition
        """
        result = {
            "description": condition.get("description", "Unnamed Condition"),
            "is_fulfilled": False,
            "details": "",
            "credits_earned": 0,
            "courses_applied": []
        }
        
        # Handle areas-based conditions (often used for distribution requirements)
        if "areas" in condition:
            areas_result = self._validate_areas(condition, student_courses)
            result.update(areas_result)
            return result
        
        # Handle regular conditions with filters
        matching_courses = []
        for course in student_courses:
            if self._course_matches_filters(course, condition.get("filters", [])):
                matching_courses.append(course)
        
        # Apply validation rules
        validation = condition.get("validation", {})
        
        # Check if minimum courses requirement is met
        min_courses = validation.get("min_courses", 0)
        if min_courses > 0:
            result["is_fulfilled"] = len(matching_courses) >= min_courses
            result["details"] = f"Found {len(matching_courses)}/{min_courses} required courses"
        
        # Check if minimum credits requirement is met
        min_credits = validation.get("min_credits", 0)
        if min_credits > 0:
            total_credits = sum(course.get("credits", 0) for course in matching_courses)
            result["is_fulfilled"] = total_credits >= min_credits
            result["details"] = f"Earned {total_credits}/{min_credits} required credits"
        
        # If no specific validation rule, fulfillment means at least one matching course
        if not validation:
            result["is_fulfilled"] = len(matching_courses) > 0
            result["details"] = f"Found {len(matching_courses)} matching courses"
        
        # Calculate total credits earned
        result["credits_earned"] = sum(course.get("credits", 0) for course in matching_courses)
        
        # Track applied courses
        result["courses_applied"] = [
            {
                "course_code": course.get("course_code", ""),
                "credits": course.get("credits", 0)
            } 
            for course in matching_courses
        ]
        
        # Check alternative fulfillment if main condition is not fulfilled
        if not result["is_fulfilled"] and "alternative_fulfillment" in condition:
            for alt in condition.get("alternative_fulfillment", []):
                alt_result = self._validate_condition(alt, student_courses)
                if alt_result.get("is_fulfilled", False):
                    result["is_fulfilled"] = True
                    result["details"] = f"Fulfilled via alternative: {alt.get('description', '')}"
                    result["credits_earned"] = alt_result.get("credits_earned", 0)
                    result["courses_applied"] = alt_result.get("courses_applied", [])
                    break
        
        return result
    
    def _validate_areas(self, condition: Dict[str, Any], student_courses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a condition that has multiple areas (distribution requirement)
        
        Args:
            condition: Dictionary containing the condition data with areas
            student_courses: List of student course dictionaries
            
        Returns:
            Dictionary with validation results for areas condition
        """
        result = {
            "is_fulfilled": False,
            "details": "",
            "areas": [],
            "fulfilled_areas_count": 0,
            "credits_earned": 0,
            "courses_applied": []
        }
        
        areas = condition.get("areas", [])
        validation = condition.get("validation", {})
        min_areas = validation.get("min_areas", 0)
        min_credits = validation.get("min_credits", 0)
        
        # Process each area
        for area in areas:
            area_result = {
                "name": area.get("name", "Unnamed Area"),
                "courses": [],
                "credits": 0,
                "is_fulfilled": False
            }
            
            # Find courses matching this area
            matching_courses = []
            for course in student_courses:
                if self._course_matches_filters(course, area.get("filters", [])):
                    matching_courses.append(course)
                    area_result["courses"].append({
                        "course_code": course.get("course_code", ""),
                        "credits": course.get("credits", 0)
                    })
            
            # Apply area-specific validation if present
            area_validation = area.get("validation", {})
            area_min_courses = area_validation.get("min_courses", 0)
            area_min_credits = area_validation.get("min_credits", 0)
            
            if area_min_courses > 0:
                area_result["is_fulfilled"] = len(matching_courses) >= area_min_courses
            elif area_min_credits > 0:
                area_credits = sum(course.get("credits", 0) for course in matching_courses)
                area_result["is_fulfilled"] = area_credits >= area_min_credits
            else:
                # If no specific validation, an area is fulfilled if it has at least one course
                area_result["is_fulfilled"] = len(matching_courses) > 0
            
            # Calculate total credits for this area
            area_result["credits"] = sum(course.get("credits", 0) for course in matching_courses)
            
            # Add to result
            result["areas"].append(area_result)
            
            if area_result["is_fulfilled"]:
                result["fulfilled_areas_count"] += 1
                result["credits_earned"] += area_result["credits"]
                result["courses_applied"].extend(area_result["courses"])
        
        # Check area distribution requirements
        if min_areas > 0:
            result["is_fulfilled"] = result["fulfilled_areas_count"] >= min_areas
            result["details"] = f"Fulfilled {result['fulfilled_areas_count']}/{min_areas} required areas"
        
        # Also check credit minimum if applicable
        if min_credits > 0 and result["credits_earned"] < min_credits:
            result["is_fulfilled"] = False
            result["details"] += f", Earned {result['credits_earned']}/{min_credits} required credits"
        
        # Check additional requirements
        additional_reqs = validation.get("additional_requirements", [])
        if additional_reqs:
            add_req_results = self._validate_additional_requirements(additional_reqs, student_courses)
            result["additional_requirements"] = add_req_results
            
            # All additional requirements must be met
            if not all(req.get("is_fulfilled", False) for req in add_req_results):
                result["is_fulfilled"] = False
                result["details"] += ", Not all additional requirements met"
        
        # Remove duplicate courses
        result["courses_applied"] = list({c["course_code"]: c for c in result["courses_applied"]}.values())
        
        return result
    
    def _validate_additional_requirements(self, requirements: List[Dict[str, Any]], 
                                         student_courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate additional requirements for distribution areas
        
        Args:
            requirements: List of additional requirement dictionaries
            student_courses: List of student course dictionaries
            
        Returns:
            List of dictionaries with validation results for each additional requirement
        """
        results = []
        
        for req in requirements:
            req_type = req.get("type", "")
            req_description = req.get("description", "Unnamed Requirement")
            req_count = req.get("count", 0)
            
            req_result = {
                "type": req_type,
                "description": req_description,
                "is_fulfilled": False,
                "details": "",
                "courses_applied": []
            }
            
            # Find courses matching the requirement filters
            matching_courses = []
            for course in student_courses:
                filters = req.get("courses", {}).get("filters", [])
                if self._course_matches_filters(course, filters):
                    matching_courses.append(course)
                    req_result["courses_applied"].append({
                        "course_code": course.get("course_code", ""),
                        "credits": course.get("credits", 0)
                    })
            
            if req_type == "min_courses":
                req_result["is_fulfilled"] = len(matching_courses) >= req_count
                req_result["details"] = f"Found {len(matching_courses)}/{req_count} required courses"
            
            elif req_type == "min_credits":
                total_credits = sum(course.get("credits", 0) for course in matching_courses)
                req_result["is_fulfilled"] = total_credits >= req_count
                req_result["details"] = f"Earned {total_credits}/{req_count} required credits"
            
            results.append(req_result)
        
        return results
    
    def _course_matches_filters(self, course: Dict[str, Any], filters: List[Dict[str, Any]]) -> bool:
        """
        Check if a course matches any of the provided filters
        
        Args:
            course: Dictionary containing course information
            filters: List of filter dictionaries
            
        Returns:
            True if the course matches any filter, False otherwise
        """
        if not filters:
            return False
        
        course_code = course.get("course_code", "")
        
        for filter_dict in filters:
            # Check for course list filter
            if "list" in filter_dict:
                course_list = filter_dict["list"]
                if course_code in course_list:
                    return True
                
                # Handle cross-listed courses (with slashes)
                for list_course in course_list:
                    if "/" in list_course and course_code in list_course.split("/"):
                        return True
            
            # Check for department filter
            if "department" in filter_dict:
                dept = filter_dict["department"]
                course_dept = course_code.split()[0] if " " in course_code else ""
                
                if dept == course_dept:
                    # If there's a course number filter
                    if "course_number" in filter_dict:
                        num_filter = filter_dict["course_number"]
                        course_num = int(course_code.split()[1]) if " " in course_code else 0
                        
                        # Handle MongoDB-style operators
                        if isinstance(num_filter, dict):
                            if "$gte" in num_filter and course_num < num_filter["$gte"]:
                                continue
                            if "$gt" in num_filter and course_num <= num_filter["$gt"]:
                                continue
                            if "$lte" in num_filter and course_num > num_filter["$lte"]:
                                continue
                            if "$lt" in num_filter and course_num >= num_filter["$lt"]:
                                continue
                        elif course_num != num_filter:
                            continue
                    
                    # Check for exclusions
                    if "exclude" in filter_dict:
                        excluded_courses = filter_dict["exclude"]
                        if course_code in excluded_courses:
                            continue
                    
                    return True
            
            # Add other filters as needed (attributes, breadth, etc.)
            # For attributes
            if "attribute" in filter_dict and "attributes" in course:
                req_attrs = filter_dict["attribute"]
                if isinstance(req_attrs, list):
                    if any(attr in course["attributes"] for attr in req_attrs):
                        return True
                elif req_attrs in course["attributes"]:
                    return True
            
            # For breadth
            if "breadth" in filter_dict and "breadth" in course:
                if filter_dict["breadth"] == course["breadth"]:
                    # Check for lab requirement if specified
                    if "has_lab" in filter_dict:
                        if filter_dict["has_lab"] == course.get("has_lab", False):
                            return True
                    else:
                        return True
        
        return False

# Example function for API endpoints
def validate_student_against_major(student_courses: List[Dict[str, Any]], major_code: str) -> Dict[str, Any]:
    """
    Validate a student's courses against a specific major's requirements
    
    Args:
        student_courses: List of student course dictionaries
        major_code: Code of the major to validate against (e.g., "EE" for Electrical Engineering)
        
    Returns:
        Validation results
    """
    # Map of major codes to requirement files
    major_file_mapping = {
        "EE": "ee_major_requirements.json",
        # Add other majors as needed
    }
    
    if major_code not in major_file_mapping:
        return {"error": f"Major code '{major_code}' not found"}
    
    validator = MajorRequirementsValidator(major_file_mapping[major_code])
    return validator.validate_student_courses(student_courses)
