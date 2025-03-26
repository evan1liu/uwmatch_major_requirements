from handle_filters import course_passes_filters
from handle_filter import course_passes_filter

async def course_updates_requirement(course: dict, requirement: dict):
    course_meets_requirement = await course_passes_filters(course, requirement["filters"])
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


async def test_course_updates_requirement():
    example_requirement_1 = {
        "name": "Professional Electives",
        "requirement-id": "professional-electives",
        "description": " ".join("""Classes to be taken in an area of professional interest.
                        The following courses are acceptable as professional electives
                        if the courses are not used to meet any other degree requirements.""".split()),
        "validation": {"min_credits": 9},
        "filters": [
            {'course_codes': ['MATH/COMP SCI  240', 'E C E 204', 'E C E 320', 'E C E 331', 'E C E 332', 'E C E 334', 'E C E 335', 'E C E 342', 'E C E 353', 'E C E/COMP SCI  354', 'E C E 355', 'E C E 356', 'E C E 356']},
            {'departments': 'E C E', 'course_number_range': {'$gte': 399}},
            {'departments': ['COMP SCI', 'MATH', 'STAT'], 'course_number_range': {'$gte': 400}},
            {'course_codes': ['MATH 319', 'MATH 320', 'MATH 321', 'MATH 322', 'MATH 340']},
            {'categories': 'Biological Science', 'levels': ['Intermediate', 'Advanced']},
            {'categories': 'Physical Science', 'levels': ['Intermediate', 'Advanced'], 'not_course_codes': 'PHYSICS 241'},
            {'categories': 'Natural Science', 'levels': 'Advanced', 'not_departments': ['MATH', 'STAT', 'COMP SCI']},
            {'schools_or_colleges': 'engineering', 'course_number_range': {'$gte': 300}, 'not_departments': 'E C E'},
            {'course_codes': ['DS 501', 'DANCE 560']}
        ]
    }
    example_course_1 = {'_id': '67577f7e7fd66ec727393650',
                        'credits': 3,
                        'course_number': '449',
                        'departments': ['PHYSICS'],
                        'course_code': 'PHYSICS 449',
                        'formatted_designations':
                            ['Level - Advanced', 'Breadth - Physical Science',
                             'L&S Credit - Counts as Liberal Arts and Science credit in L&S'],
                        'school-or-college': ['letters-science']}
    updated_requirement1 = await course_updates_requirement(example_course_1, example_requirement_1)
    print(updated_requirement1)
    
    example_course_2 = {'_id': '67577f9d7fd66ec727393d36',
                        'credits': 3,
                        'course_number': '570',
                        'departments': ['ZOOLOGY'],
                        'course_code': 'ZOOLOGY 570',
                        'formatted_designations':
                            ['Breadth - Biological Science',
                             'L&S Credit - Counts as Liberal Arts and Science credit in L&S',
                             'Level - Intermediate'],
                        'school-or-college': ['letters-science']}
    output_requirement2 = await course_updates_requirement(example_course_2, updated_requirement1)
    print(output_requirement2)

    
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

# Example usage in test:
async def test_courses_update_requirement():
    example_requirement = {
        "name": "Professional Electives",
        "requirement-id": "professional-electives",
        "description": " ".join("""Classes to be taken in an area of professional interest.
                        The following courses are acceptable as professional electives
                        if the courses are not used to meet any other degree requirements.""".split()),
        "validation": {"min_credits": 9},
        "filters": [
            {'course_codes': ['MATH/COMP SCI  240', 'E C E 204', 'E C E 320', 'E C E 331', 'E C E 332', 'E C E 334', 'E C E 335', 'E C E 342', 'E C E 353', 'E C E/COMP SCI  354', 'E C E 355', 'E C E 356', 'E C E 356']},
            {'departments': 'E C E', 'course_number_range': {'$gte': 399}},
            {'departments': ['COMP SCI', 'MATH', 'STAT'], 'course_number_range': {'$gte': 400}},
            {'course_codes': ['MATH 319', 'MATH 320', 'MATH 321', 'MATH 322', 'MATH 340']},
            {'categories': 'Biological Science', 'levels': ['Intermediate', 'Advanced']},
            {'categories': 'Physical Science', 'levels': ['Intermediate', 'Advanced'], 'not_course_codes': 'PHYSICS 241'},
            {'categories': 'Natural Science', 'levels': 'Advanced', 'not_departments': ['MATH', 'STAT', 'COMP SCI']},
            {'schools_or_colleges': 'engineering', 'course_number_range': {'$gte': 300}, 'not_departments': 'E C E'},
            {'course_codes': ['DS 501', 'DANCE 560']}
        ]
    }
    
    example_courses = [
        {'_id': '67577f7e7fd66ec727393650',
         'credits': 3,
         'course_number': '449',
         'departments': ['PHYSICS'],
         'course_code': 'PHYSICS 449',
         'formatted_designations':
             ['Level - Advanced', 'Breadth - Physical Science',
              'L&S Credit - Counts as Liberal Arts and Science credit in L&S'],
         'school-or-college': ['letters-science']},
        {'_id': '67577f9d7fd66ec727393d36',
         'credits': 3,
         'course_number': '570',
         'departments': ['ZOOLOGY'],
         'course_code': 'ZOOLOGY 570',
         'formatted_designations':
             ['Breadth - Biological Science',
              'L&S Credit - Counts as Liberal Arts and Science credit in L&S',
              'Level - Intermediate'],
         'school-or-college': ['letters-science']},
         {'_id': '67577efb7fd66ec727391979',
          'credits': 3,
          'course_number': '427',
          'departments': ['CSCS', 'CURRIC'],
          'course_code': 'CSCS/CURRIC 427',
          'school-or-college': ['education', 'human-ecology']}
    ]
    
    final_requirement = await courses_update_requirement(example_courses, example_requirement)
    print("Final updated requirement after processing all courses:")
    print(final_requirement)

example_requirement = {
    "name": "Professional Electives",
    "requirement-id": "professional-electives",
    "description": " ".join("""Classes to be taken in an area of professional interest.
                    The following courses are acceptable as professional electives
                    if the courses are not used to meet any other degree requirements.""".split()),
    "validation": {"min_credits": 9},
    "filters": [
        {'course_codes': ['MATH/COMP SCI  240', 'E C E 204', 'E C E 320', 'E C E 331', 'E C E 332', 'E C E 334', 'E C E 335', 'E C E 342', 'E C E 353', 'E C E/COMP SCI  354', 'E C E 355', 'E C E 356', 'E C E 356']},
        {'departments': 'E C E', 'course_number_range': {'$gte': 399}},
        {'departments': ['COMP SCI', 'MATH', 'STAT'], 'course_number_range': {'$gte': 400}},
        {'course_codes': ['MATH 319', 'MATH 320', 'MATH 321', 'MATH 322', 'MATH 340']},
        {'categories': 'Biological Science', 'levels': ['Intermediate', 'Advanced']},
        {'categories': 'Physical Science', 'levels': ['Intermediate', 'Advanced'], 'not_course_codes': 'PHYSICS 241'},
        {'categories': 'Natural Science', 'levels': 'Advanced', 'not_departments': ['MATH', 'STAT', 'COMP SCI']},
        {'schools_or_colleges': 'engineering', 'course_number_range': {'$gte': 300}, 'not_departments': 'E C E'},
        {'course_codes': ['DS 501', 'DANCE 560']}
    ],
    "credits_constraint": [
        {"description": " ".join("""1
                                    Students may only earn degree credit for MATH 320 Linear Algebra and Differential Equations
                                    or MATH 340 Elementary Matrix and Linear Algebra, not both.""".split()),
            "max_credits": 3,  # Only count 3 credits total from this group
            "filter": {
                "course_codes": ["MATH 320", "MATH 340"]
            }
        }
    ]
}

async def credit_constraints_update_requirement(requirement: dict) -> dict:
    """
    Applies credit constraints to the requirement's current_credits.
    Uses filters to identify courses and applies maximum credit limits.
    Does not modify the requirement if:
    - credits_constraint is not defined
    - no courses have been passed
    - validation or current_credits not being tracked
    
    Args:
        requirement (dict): The requirement dictionary to check constraints on
        
    Returns:
        dict: The requirement with credit constraints applied
    """
    # Skip if no constraints defined or no courses passed yet
    if not requirement.get("credits_constraint") or "courses_passed" not in requirement:
        return requirement
        
    for constraint_name, constraint in requirement["credits_constraint"].items():
        # Calculate total credits for courses matching this constraint's filter
        matching_credits = sum(
            course["credits"] for course in requirement["courses_passed"]
            if await course_passes_filter(course, constraint["filter"])
        )
        
        # If we're over the limit, subtract the excess from current_credits
        if matching_credits > constraint["max_credits"]:
            excess_credits = matching_credits - constraint["max_credits"]
            requirement["validation"]["current_credits"] -= excess_credits
            
    return requirement

if __name__ == "__main__":
    import asyncio
    # asyncio.run(test_course_updates_requirement())
    asyncio.run(test_courses_update_requirement())