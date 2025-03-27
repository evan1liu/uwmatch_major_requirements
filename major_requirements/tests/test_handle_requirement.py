import asyncio
import time
import pytest

from major_requirements.handle_requirement import (
    course_updates_requirement, 
    courses_update_requirement,
    credit_constraints_update_requirement,
    requirement_passed
)

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

async def test_course_updates_requirement_single_filter():
    example_requirement_1 = {
        "name": "E C E Advanced Elective",
        "requirement_id": "ece_advanced_elective",
        "description": "At least 9 credits must be in E C E courses numbered 400 and above.",
        "validation": {"min_credits": 9},
        "filter": {"department": "E C E", "course_number_range": {"$gte": 400}}
    }
    
    example_course_1 = {'_id': '67577f1d7fd66ec7273920d1',
                        'credits': 4,
                        'course_number': '453',
                        'departments': ['E C E'],
                        'course_code': 'E C E 453'}
    
    updated_requirement1 = await course_updates_requirement(example_course_1, example_requirement_1)
    print(updated_requirement1)
    
    example_course_2 = {'_id': '67577f1e7fd66ec72739212f',
                        'credits': 3,
                        'course_number': '551',
                        'departments': ['E C E'],
                        'course_code': 'E C E 551'}
                        
    output_requirement2 = await course_updates_requirement(example_course_2, updated_requirement1)
    print(output_requirement2)

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

async def test_credit_constraints_update_requirement():
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
        "credits_constraints": [
            {"description": " ".join("""Students may only earn degree credit for MATH 320
                                    Linear Algebra and Differential Equations or MATH 340
                                    Elementary Matrix and Linear Algebra, not both.""".split()),
                "max_credits": 3,  # Only count 3 credits total from this group
                "filter": {
                    "course_codes": ["MATH 320", "MATH 340"]
                }
            }
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
          'school-or-college': ['education', 'human-ecology']},
        {'_id': '67577f587fd66ec727392de3',
         'credits': 3,
         'course_number': '320',
         'departments': ['MATH'],
         'course_code': 'MATH 320',
         'formatted_designations':
             ['Level - Advanced', 'Breadth - Natural Science',
              'L&S Credit - Counts as Liberal Arts and Science credit in L&S'],
         'school-or-college': ['letters-science']},
        {'_id': '67577f597fd66ec727392e1a',
         'credits': 3,
         'course_number': '340',
         'departments': ['MATH'],
         'course_code': 'MATH 340',
         'formatted_designations':
             ['Level - Advanced', 'Breadth - Natural Science',
              'L&S Credit - Counts as Liberal Arts and Science credit in L&S'],
         'school-or-college': ['letters-science']}   
    ]
    final_requirement = await courses_update_requirement(example_courses, example_requirement)
    requirement_after_apply_credit_constraints = await credit_constraints_update_requirement(final_requirement)
    print(requirement_after_apply_credit_constraints)

async def test_requirement_passed():
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
        "credits_constraints": [
            {"description": " ".join("""Students may only earn degree credit for MATH 320
                                    Linear Algebra and Differential Equations or MATH 340
                                    Elementary Matrix and Linear Algebra, not both.""".split()),
                "max_credits": 3,  # Only count 3 credits total from this group
                "filter": {
                    "course_codes": ["MATH 320", "MATH 340"]
                }
            }
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
          'school-or-college': ['education', 'human-ecology']},
        {'_id': '67577f587fd66ec727392de3',
         'credits': 3,
         'course_number': '320',
         'departments': ['MATH'],
         'course_code': 'MATH 320',
         'formatted_designations':
             ['Level - Advanced', 'Breadth - Natural Science',
              'L&S Credit - Counts as Liberal Arts and Science credit in L&S'],
         'school-or-college': ['letters-science']},
        {'_id': '67577f597fd66ec727392e1a',
         'credits': 3,
         'course_number': '340',
         'departments': ['MATH'],
         'course_code': 'MATH 340',
         'formatted_designations':
             ['Level - Advanced', 'Breadth - Natural Science',
              'L&S Credit - Counts as Liberal Arts and Science credit in L&S'],
         'school-or-college': ['letters-science']}   
    ]
    checked_requirement = await courses_update_requirement(example_courses, example_requirement)
    requirement_after_apply_credit_constraints = await credit_constraints_update_requirement(checked_requirement)
    final_requirement = await requirement_passed(requirement_after_apply_credit_constraints)
    print(final_requirement)


async def test_single_filter_requirement():
    example_requirement = {
                "description": "At least 9 credits must be in E C E courses numbered 400 and above.",
                "validation": {"min_credits": 9},
                "filter": {"department": "E C E", "course_number_range": {"$gte": 400}}
             }
    example_course = {'_id': '67577f1d7fd66ec7273920d1',
                        'credits': 4,
                        'course_number': '453',
                        'departments': ['E C E'],
                        'course_code': 'E C E 453'}
    result = await course_updates_requirement(example_course, example_requirement)
    print(result)
    
if __name__ == "__main__":
    import asyncio
    import time
    
    # Uncomment the test you want to run
    # asyncio.run(test_course_updates_requirement())
    # asyncio.run(test_courses_update_requirement())
    # asyncio.run(test_course_updates_requirement_single_filter())
    # asyncio.run(test_credit_constraints_update_requirement())
    
    # Measure execution time
    # start_time = time.perf_counter()
    # asyncio.run(test_requirement_passed())
    # end_time = time.perf_counter()
    
    # execution_time = end_time - start_time
    # print(f"Execution time: {execution_time:.4f} seconds") 
    
    asyncio.run(test_single_filter_requirement())