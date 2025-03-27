from major_requirements.handle_filters import course_passes_filters
from major_requirements.handle_filter import course_passes_filter

async def course_updates_requirement(course: dict, requirement: dict):
    """
    Updates a requirement based on a single course.
    Handles both single filter (requirement["filter"]) and multiple filters (requirement["filters"]).
    
    Args:
        course (dict): The course to evaluate
        requirement (dict): The requirement to potentially update
        
    Returns:
        dict: The updated requirement
    """
    # Check if we have a single filter or multiple filters
    if "filter" in requirement:
        # Single filter case
        course_meets_requirement = await course_passes_filter(course, requirement["filter"])
    elif "filters" in requirement:
        # Multiple filters case
        course_meets_requirement = await course_passes_filters(course, requirement["filters"])
    else:
        # No filter defined, can't evaluate
        return requirement
    
    if course_meets_requirement:
        if "courses_passed" not in requirement:
            requirement["courses_passed"] = []
        requirement["courses_passed"].append(course)
        
        validation_type = list(requirement["validation"].keys())[0]
        
        if validation_type == "min_credits":
            course_credit = course["credits"]
            current_credits = requirement["validation"].get("current_credits", 0)  # Get the current value or 0
            requirement["validation"]["current_credits"] = current_credits + course_credit  # Add and assign
            
        if validation_type == "min_courses":
            current_courses_count = requirement["validation"].get("current_courses_count", 0)
            requirement["validation"]["current_courses_count"] = current_courses_count + 1
    
    return requirement


# NOTE: For the final processing, we'll pass in each course one by one
#       to the validation function with the entire nested dictionary.
#       Therefore, we probably won't be using this function in the
#       final requirements processing. 
async def courses_update_requirement(courses: list[dict], requirement: dict) -> dict:
    """
    Updates a requirement by processing a list of courses sequentially.
    Each course updates the requirement, and the updated requirement is used for the next course.
    
    Args:
        courses (list[dict]): List of course dictionaries to process
        requirement (dict): The initial requirement dictionary
        
    Returns:
        dict: The final updated requirement after processing all courses
    """
    current_requirement = requirement
    for course in courses:
        current_requirement = await course_updates_requirement(course, current_requirement)
    return current_requirement


async def credit_constraints_update_requirement(requirement: dict) -> dict:
    """
    Applies credit constraints to the requirement's current_credits.
    Uses filters to identify courses and applies maximum credit limits.
    Does not modify the requirement if:
    - credits_constraints is not defined
    - no courses have been passed
    - validation or current_credits not being tracked
    
    Args:
        requirement (dict): The requirement dictionary to check constraints on
        
    Returns:
        dict: The requirement with credit constraints applied
    """
    # Skip if no constraints defined or no courses passed yet
    if not requirement.get("credits_constraints") or "courses_passed" not in requirement:
        return requirement
        
    for constraint in requirement["credits_constraints"]:
        # Calculate total credits for courses matching this constraint's filter
        matching_credits = 0
        for course in requirement["courses_passed"]:
            if await course_passes_filter(course, constraint["filter"]):
                matching_credits += course["credits"]
        
        # If we're over the limit, subtract the excess from current_credits
        if matching_credits > constraint["max_credits"]:
            excess_credits = matching_credits - constraint["max_credits"]
            requirement["validation"]["current_credits"] -= excess_credits
    
    requirement["credits_constraints_applied"] = True
            
    return requirement


async def requirement_passed(requirement):
    """
    Check if a requirement passes based on its validation criteria.
    Ensures counters are initialized even if no courses matched.
    """
    if "validation" not in requirement:
        return requirement
        
    validation_type = list(requirement["validation"].keys())[0]
    
    if validation_type == "min_credits":
        # Initialize current_credits if it doesn't exist
        if "current_credits" not in requirement["validation"]:
            requirement["validation"]["current_credits"] = 0
            
        if requirement["validation"]["current_credits"] >= requirement["validation"]["min_credits"]:
            requirement["validation"]["passed"] = True
        else:
            requirement["validation"]["passed"] = False
    
    elif validation_type == "min_courses":
        # Initialize current_courses_count if it doesn't exist 
        if "current_courses_count" not in requirement["validation"]:
            requirement["validation"]["current_courses_count"] = 0
            
        if requirement["validation"]["current_courses_count"] >= requirement["validation"]["min_courses"]:
            requirement["validation"]["passed"] = True
        else:
            requirement["validation"]["passed"] = False
            
    return requirement
