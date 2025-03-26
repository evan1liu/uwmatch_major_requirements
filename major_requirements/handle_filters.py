from major_requirements.handle_filter import course_passes_filter
import asyncio

async def course_passes_filters(course: dict, filters: list[dict]) -> dict | None:
    """_summary_

    Args:
        course (dict): A course object containing many different fields
        filters (list[dict]): A list of filters, each filter is a dictionary of different types ofcriteria

    Returns:
        dict | None: Returns the first filter that the course passes, or None if no filter passes
    """
    for filter in filters:
        passes = await course_passes_filter(course, filter)
        if passes:
            return filter  # Return the first passing filter
            
    return None  # Return None if no filter passes


async def test_course_passes_filters():
    example_filters = [
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
    example_course_1 = {'_id': '67577f7e7fd66ec727393650',
                        'credits': 3,
                        'course_number': '449',
                        'departments': ['PHYSICS'],
                        'course_code': 'PHYSICS 449',
                        'formatted_designations':
                            ['Level - Advanced', 'Breadth - Physical Science',
                             'L&S Credit - Counts as Liberal Arts and Science credit in L&S'],
                        'school-or-college': ['letters-science']}
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
    result1 = await course_passes_filters(example_course_1, example_filters)
    print(result1)
    result2 = await course_passes_filters(example_course_2, example_filters)
    print(result2)
    
if __name__ == "__main__":
    asyncio.run(test_course_passes_filters())