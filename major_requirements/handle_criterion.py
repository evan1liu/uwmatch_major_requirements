from utils.parse_course_code import parse_course_code



async def course_passes_list_criterion(course: dict, criterion: list[str]) -> bool:
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

async def course_passes_category_criterion(course: dict, criterion: list[str]) -> bool:
    """Handle category criterion with in-memory course data"""
    formatted_designations = course.get("formatted_designations", [])
    # A "designation" in "formatted_designations" may be "Breadth - Biological Science"
    # It doesn't exactly match the category in criterion "Biologcal Science"
    # Therefore, we're checking it the criterion belongs to any of the substrings in formatted designations
    return any(cat in designation for designation in formatted_designations for cat in criterion)

# A LEVEL criterion could have multiple levels (e.g. Intermediate AND Advanced)
# Therefore, the criterion value/parameter is a list of strings
async def course_passes_level_criterion(course: dict, criterion: list[str]) -> bool:
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

async def course_passes_department_criterion(course: dict, criterion: list[str]) -> bool:
    """
    Handle department criterion with in-memory course data
    Checks if a course belongs to any of the specified departments
    """
    departments = course.get("departments", [])
    # Check if any department from criterion exists in the course's departments
    return any(dept in departments for dept in criterion)

# The "course_number" type criterion has a value of a dictionary
# Each key/value pair within the dictionary: Key is the comparative, value is a number
# e.g. {'$gte': 300, '$lte': 699}
# This means that the course numnber should be greater or equal to 300, less than or equal to 699
async def course_passes_course_number_range_criterion(course: dict, criterion: dict) -> bool:
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

# TODO: We'll need to create a new field in the database that assigns each course to its college/school
# @file:departments.json
async def course_passes_school_or_college_criterion(course: dict, criterion: list[str]):
    course_school_or_college = course["school-or-college"]
    return any(school in course_school_or_college for school in criterion)
    

# we map the keys of different criteria to a function name
# we'll be deciding which function to use based on the key of the filter dictionary
criterion_handlers = {
    'list': course_passes_list_criterion,
    'category': course_passes_category_criterion,
    'level': course_passes_level_criterion,
    'department': course_passes_department_criterion,
    'course_number': course_passes_course_number_range_criterion,
}