import pytest

# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]
pytestmark = pytest.mark.asyncio

from major_requirements.handle_criterion import (
    course_passes_list_criterion,
    course_passes_category_criterion,
    course_passes_level_criterion,
    course_passes_department_criterion,
    course_passes_course_number_range_criterion,
    course_passes_school_or_college_criterion,
    criterion_handlers # a dictionary matching the criterion type to the handle_creiterion function
)

async def test_course_passes_list_criterion():
    example_course_1 = {'_id': '67577f107fd66ec727391df5',
                        'credits': 2,
                        'course_number': '210',
                        'departments': ['E C E'],
                        'course_code': 'E C E 210'}
    example_list_criterion_1 = ["E C E 203", "E C E 210", "E C E 222"]
    result1 = await course_passes_list_criterion(example_course_1, example_list_criterion_1)
    assert result1 == True
    
    example_course_2 = {'_id': '67577f0f7fd66ec727391ddd',
                        'credits': 3,
                        'course_number': '203',
                        'departments': ['E C E'],
                        'course_code': 'E C E 203'}
    example_list_criterion_2 = ["E C E 320", "E C E 420", "E C E 434"]
    result2 = await course_passes_list_criterion(example_course_2, example_list_criterion_2)
    assert result2 == False
    
    
async def test_course_passes_category_criterion():
    example_course_1 = {'_id': '67577eec7fd66ec72739161f',
                        'credits': 3,
                        'course_number': '101',
                        'departments': ['BIOLOGY', 'ZOOLOGY'],
                        'course_code': 'BIOLOGY/ZOOLOGY 101',
                        'formatted_designations':
                        ['Breadth - Biological Science',
                         'Level - Elementary',
                        'L&S Credit - Counts as Liberal Arts and Science credit in L&S']}
    example_category_criterion_1  = ["Biological Science", "Physical Science"]
    result1 = await course_passes_category_criterion(example_course_1, example_category_criterion_1)
    assert result1 == True
    
    example_course_2 =  {'_id': '67577efb7fd66ec72739197d',
                         'credits': 3,
                         'course_number': '100',
                         'departments': ['COM ARTS'],
                         'course_code': 'COM ARTS 100',
                         'formatted_designations':
                             ['Gen Ed - Communication Part A',
                              'Level - Elementary',
                              'L&S Credit - Counts as Liberal Arts and Science credit in L&S']}
    example_category_criterion_2  = ["Communication Part B"]
    result2 = await course_passes_category_criterion(example_course_2, example_category_criterion_2)
    assert result2 == False
    
async def test_course_passes_level_criterion():
    example_course_1 =  {'_id': '67577f7e7fd66ec727393650',
                         'credits': 3,
                         'course_number': '449',
                         'departments': ['PHYSICS'],
                         'course_code': 'PHYSICS 449',
                         'formatted_designations':
                             ['Level - Advanced',
                              'Breadth - Physical Science',
                              'L&S Credit - Counts as Liberal Arts and Science credit in L&S']}
    example_level_criterion_1 = ["Intermediate", "Advanced"]
    result1 = await course_passes_level_criterion(example_course_1, example_level_criterion_1)
    assert result1 == True

    example_course_2 = {'_id': '67577eec7fd66ec72739161f',
                        'credits': 3,
                        'course_number': '101',
                        'departments': ['BIOLOGY', 'ZOOLOGY'],
                        'course_code': 'BIOLOGY/ZOOLOGY 101',
                        'formatted_designations':
                            ['Breadth - Biological Science',
                             'Level - Elementary',
                             'L&S Credit - Counts as Liberal Arts and Science credit in L&S']}    
    example_level_criterion_2 = ["Intermediate", "Advanced"]
    result2 = await course_passes_level_criterion(example_course_2, example_level_criterion_2)
    assert result2 == False
    
async def test_course_passes_department_criterion():
    example_course_1 = {'_id': '67577f1d7fd66ec7273920d1',
                        'credits': 4,
                        'course_number': '453',
                        'departments': ['E C E'],
                        'course_code': 'E C E 453'}
    example_department_criterion_1 = ["E C E"]
    # keep the spaces between "E C E" because it's consistent across all school's webpages
    # we're not post-processing the "E C E" to remove white spaces
    result1 = await course_passes_department_criterion(example_course_1, example_department_criterion_1)
    assert result1 == True
    
    example_course_2 = {'_id': '67577efb7fd66ec727391979',
                        'credits': 3,
                        'course_number': '427',
                        'departments': ['CSCS', 'CURRIC'],
                        'course_code': 'CSCS/CURRIC 427'}
    example_department_criterion_2 = ["CSCS", "DS", "HDFS", "INTER-HE"]
    
    result2 = await course_passes_department_criterion(example_course_2, example_department_criterion_2)
    assert result2 == True

    example_course_3 = {'_id': '67577eef7fd66ec7273916fb',
                        'credits': 3,
                        'course_number': '301',
                        'departments': ['B M E'],
                        'course_code': 'B M E 301',
                        'formatted_designations': ['Gen Ed - Communication Part B']}
    example_department_criterion_3 = ["CSCS", "DS", "HDFS", "INTER-HE"]
    
    result3 = await course_passes_department_criterion(example_course_3, example_department_criterion_3)
    assert result3 == False
    
async def test_course_passes_course_number_range_criterion():
    example_course_1 = {'_id': '67577f1d7fd66ec7273920d1',
                        'credits': 4,
                        'course_number': '453',
                        'departments': ['E C E'],
                        'course_code': 'E C E 453'}
    example_course_number_range_criterion_1 = {"$gte": 399}
    result1 = await course_passes_course_number_range_criterion(example_course_1, example_course_number_range_criterion_1)
    assert result1 == True
    
    example_course_2 = {'_id': '67577eef7fd66ec7273916fb',
                        'credits': 3,
                        'course_number': '301',
                        'departments': ['B M E'],
                        'course_code': 'B M E 301',
                        'formatted_designations': ['Gen Ed - Communication Part B']}
    example_course_number_range_criterion_2 = {"$gte": 400}
    result2 = await course_passes_course_number_range_criterion(example_course_2, example_course_number_range_criterion_2)
    assert result2 == False
    
async def test_course_passes_school_or_college_criterion():
    example_course_1 = {'_id': '67577eef7fd66ec7273916fb',
                        'credits': 3,
                        'course_number': '301',
                        'departments': ['B M E'],
                        'course_code': 'B M E 301',
                        'formatted_designations': ['Gen Ed - Communication Part B'],
                        'school-or-college': ['engineering']}
    example_school_or_college_criterion_1 = ["engineering"]
    result1 = await course_passes_school_or_college_criterion(example_course_1, example_school_or_college_criterion_1)
    assert result1 == True
    
    example_course_2 = {'_id': '67577f0c7fd66ec727391d4c',
                        'credits': 3,
                        'course_number': '350',
                        'departments': ['ECON'],
                        'course_code': 'ECON 350',
                        'formatted_designations':
                            ['Breadth - Social Science', 'L&S Credit - Counts as Liberal Arts and Science credit in L&S',
                             'Level - Intermediate'],
                        'school-or-college': ['letters-science']}
    example_school_or_college_criterion_2 = ["business"]
    result2 = await course_passes_school_or_college_criterion(example_course_2, example_school_or_college_criterion_2)
    assert result2 == False