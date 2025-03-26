from handle_filters import course_passes_filters

async def update_requirement(course: dict, requirement: dict):
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


async def test_update_requirement():
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
    updated_requirement1 = await update_requirement(example_course_1, example_requirement_1)
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
    output_requirement2 = await update_requirement(example_course_2, updated_requirement1)
    print(output_requirement2)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_update_requirement())