# A FILTER CONTAINS MULTIPLE DIFFERENT TYPES OF CRITERIA
# THESE CRITERIA HAVE AN "AND" RELATIONSHIP
# THAT MEANS YOU MUST PASS ALL TYPES OF CRITERIA TO PASS THE FILTER


from major_requirements.handle_criterion import (
    course_passes_course_code_criterion,
    course_passes_category_criterion,
    course_passes_level_criterion,
    course_passes_department_criterion,
    course_passes_course_number_range_criterion,
    course_passes_school_or_college_criterion # a dictionary matching the criterion type to the handle_creiterion function
)

# we map the keys of different criteria to a function name
# we'll be deciding which function to use based on the key of the filter dictionary
criterion_handlers = {
    'course_codes': course_passes_course_code_criterion,
    'categories': course_passes_category_criterion,
    'levels': course_passes_level_criterion,
    'departments': course_passes_department_criterion,
    'course_number_range': course_passes_course_number_range_criterion,
    'schools_or_colleges': course_passes_school_or_college_criterion
}

async def course_passes_filter(course: dict, filter: dict) -> bool:
    """_summary_

    Args:
        course (dict): A course object containing many different fields
        filter (dict): A filter is a dictionary of criteria, the course must passes all criteria.
                     For each key/value pair, the key that is the type of criterium,
                     and the value is the actual criterium for filtering.
                     If the key starts with 'not_', the result will be inverted.

    Returns:
        bool: returns True if the course passes filter, and False if not
    """
    course_passes_filter = True
    for criterium_type, criterium in filter.items():
        # Check if this is a NOT criterion
        is_not = criterium_type.startswith('not_')
        # Remove 'not_' prefix if present to get the actual criterion type
        actual_type = criterium_type[4:] if is_not else criterium_type
        
        course_passes_criterium = await criterion_handlers[actual_type](course, criterium)
        # Invert the result if this is a NOT criterion
        if is_not:
            course_passes_criterium = not course_passes_criterium
            
        if not course_passes_criterium:
            course_passes_filter = False
            break
    return course_passes_filter

import pytest

@pytest.mark.asyncio
async def test_course_passes_filter():
    example_course_1 = {'_id': '67577f1d7fd66ec7273920d1',
                        'credits': 4,
                        'course_number': '453',
                        'departments': ['E C E'],
                        'course_code': 'E C E 453'}
    # Original Text: E C E courses numbered 399 and higher
    example_filter_1 = {'departments': ["E C E"], 'course_number_range': {'$gte': 399}}
    result1 = await course_passes_filter(example_course_1, example_filter_1)
    assert result1 == True
    
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
    # Original Text: Any biological science course that is designated as intermediate or advanced
    example_filter_2 = {'categories': ['Biological Science'], 'levels': ['Intermediate', 'Advanced']}
    result2 = await course_passes_filter(example_course_2, example_filter_2)
    assert result2 == True
    
    example_course_3 = {'_id': '67577f477fd66ec727392a2d',
                        'credits': 2,
                        'course_number': '119',
                        'departments': ['KINES'],
                        'course_code': 'KINES 119',
                        'school-or-college': ['education']}
    example_filter_3 = {'course_codes': ['KINES 250',
                        'KINES 260',
                        'KINES 312',
                        'KINES 325',
                        'KINES 360',
                        'KINES 387',
                        'KINES 390',
                        'KINES 427',
                        'KINES 501',
                        'KINES 508',
                        'KINES/NURSING  523',
                        'KINES/NUTR SCI  525',
                        'KINES 527',
                        'KINES 531',
                        'KINES 555',
                        'KINES 614',
                        'KINES 615',
                        'KINES 618']}
    result3 = await course_passes_filter(example_course_3, example_filter_3)
    assert result3 == False
    
    example_course_4 = {'_id': '67577f1c7fd66ec727392091',
                        'credits': 3,
                        'course_number': '439',
                        'departments': ['E C E', 'M E'],
                        'course_code': 'E C E/M E 439',
                        'school-or-college': ['engineering']}
    # Original Text: "Engineering courses numbered 300 and higher that are not E C E or cross-listed with E C E"
    example_filter_4 = {'schools-or-colleges': ['engineering'],
                        'course_number_range': {'$gte': 300},
                        'not_departments': ["E C E"]}
    result4 = await course_passes_filter(example_course_4, example_filter_4)
    assert result4 == False
    
    example_course_5 = {'_id': '67577f797fd66ec72739352a',
                        'credits': 3,
                        'course_number': '241',
                        'departments': ['PHYSICS'],
                        'course_code': 'PHYSICS 241',
                        'formatted_designations':
                            ['L&S Credit - Counts as Liberal Arts and Science credit in L&S',
                             'Breadth - Physical Science',
                             'Level - Intermediate'],
                        'school-or-college': ['letters-science']}
    # Original Text: Any physical science course that is designated as intermediate or advanced (except PHYSICS 241)
    example_filter_5 = {'categories': ['Physical Science'], 'levels': ['Intermediate', 'Advanced'], 'not_course_codes': ['PHYSICS 241']}
    result5 = await course_passes_filter(example_course_5, example_filter_5)
    assert result5 == False