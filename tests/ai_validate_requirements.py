from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from uwmatch import Settings
import asyncio
from pprint import pprint

async def validate_requirements(course_ids, conditions, course_collection):
    """
    Validate a list of course IDs against a set of conditions.
    
    Args:
        course_ids (list): List of course ID strings
        conditions (list): List of condition dictionaries
        course_collection: MongoDB collection for courses
        
    Returns:
        dict: Results of validation with fulfilled and unfulfilled requirements
    """
    # Convert string IDs to ObjectId if needed
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in course_ids]
    
    # Retrieve all courses in one query
    courses = []
    async for course in course_collection.find({'_id': {'$in': object_ids}}):
        courses.append(course)
    
    print(f"Retrieved {len(courses)} courses from database")
    
    # Initialize results
    results = {
        'fulfilled_requirements': [],
        'unfulfilled_requirements': [],
        'courses_used': {},  # Tracks which courses fulfill which requirements
        'summary': {}
    }
    
    # Check each condition against the courses
    for condition in conditions:
        condition_result = {
            'description': condition.get('description', 'Unnamed Requirement'),
            'courses_that_match': [],
            'is_fulfilled': False,
            'needed': condition.get('val_value', 0),
            'current': 0,
            'val_type': condition.get('val_type', 'min_credits'),
            'suggested_courses': []
        }
        
        # Check each course against this condition
        for course in courses:
            if course_meets_condition(course, condition):
                course_info = {
                    'id': str(course['_id']),
                    'code': course.get('course_code', 'Unknown'),
                    'title': course.get('title', 'Unnamed Course'),
                    'credits': course.get('credits', 0)
                }
                condition_result['courses_that_match'].append(course_info)
                
                # Track course usage
                if str(course['_id']) not in results['courses_used']:
                    results['courses_used'][str(course['_id'])] = []
                results['courses_used'][str(course['_id'])].append(condition['description'])
                
                # Update current progress based on val_type
                if condition['val_type'] == 'min_credits':
                    condition_result['current'] += course.get('credits', 0)
                elif condition['val_type'] == 'min_courses':
                    condition_result['current'] += 1 
        
        # Determine if requirement is fulfilled
        if condition['val_type'] == 'min_credits':
            condition_result['is_fulfilled'] = condition_result['current'] >= condition['val_value']
        elif condition['val_type'] == 'min_courses':
            condition_result['is_fulfilled'] = condition_result['current'] >= condition['val_value']
        
        # If not fulfilled, find suggested courses
        if not condition_result['is_fulfilled']:
            suggested_courses = await find_suggested_courses(condition, course_collection, limit=3)
            condition_result['suggested_courses'] = suggested_courses
        
        # Add to appropriate results list
        if condition_result['is_fulfilled']:
            results['fulfilled_requirements'].append(condition_result)
        else:
            results['unfulfilled_requirements'].append(condition_result)
    
    # Generate summary
    results['summary'] = {
        'total_requirements': len(conditions),
        'fulfilled': len(results['fulfilled_requirements']),
        'unfulfilled': len(results['unfulfilled_requirements']),
        'completion_percentage': round(len(results['fulfilled_requirements']) / len(conditions) * 100 if conditions else 0, 2)
    }
    
    return results


def course_meets_condition(course, condition):
    """
    Check if a course meets a condition based on the filters.
    
    Args:
        course (dict): The course document
        condition (dict): The condition to check against
        
    Returns:
        bool: True if the course meets the condition, False otherwise
    """
    # Get the formatted designations for easier checking
    formatted_designations = course.get('formatted_designations', [])
    
    # Default to False - course must match at least one filter to be True
    for filter_item in condition.get('filter', []):
        # Check if course is in the specified list
        if 'list' in filter_item:
            course_code = course.get('course_code', '')
            if course_code in filter_item['list']:
                return True
        
        # Check department and course number
        elif 'department' in filter_item and 'course_number' in filter_item:
            # Check department match
            department = filter_item['department']
            if department in course.get('departments', []) or department == course.get('department', ''):
                # Get course number
                course_num = int(course.get('course_number', '0').replace(' ', ''))
                
                # Check course number based on filter type
                if isinstance(filter_item['course_number'], dict):
                    # Handle MongoDB operators
                    if '$gte' in filter_item['course_number'] and course_num >= filter_item['course_number']['$gte']:
                        return True
                    if '$lte' in filter_item['course_number'] and course_num <= filter_item['course_number']['$lte']:
                        return True
                    if '$eq' in filter_item['course_number'] and course_num == filter_item['course_number']['$eq']:
                        return True
                elif course_num == int(filter_item['course_number']):
                    return True
        
        # Check category and level from formatted_designations
        elif 'category' in filter_item and 'level' in filter_item:
            # Get required category and levels
            category = filter_item['category']
            levels = filter_item['level'] if isinstance(filter_item['level'], list) else [filter_item['level']]
            
            # Check if any formatted designation matches the category
            category_matched = False
            for designation in formatted_designations:
                if category in designation:
                    category_matched = True
                    break
            
            if category_matched:
                # Check if any formatted designation matches any of the required levels
                for level in levels:
                    for designation in formatted_designations:
                        if f"Level - {level}" == designation:
                            return True
        
        # Check just category
        elif 'category' in filter_item:
            category = filter_item['category']
            for designation in formatted_designations:
                if category in designation:
                    return True
        
        # Check just level
        elif 'level' in filter_item:
            levels = filter_item['level'] if isinstance(filter_item['level'], list) else [filter_item['level']]
            for level in levels:
                if f"Level - {level}" in formatted_designations:
                    return True
    
    # If we get here, none of the filters matched
    return False


async def find_suggested_courses(condition, course_collection, limit=3):
    """
    Find courses that would fulfill an unfulfilled requirement.
    
    Args:
        condition (dict): The condition to find suggestions for
        course_collection: MongoDB collection for courses
        limit (int): Maximum number of suggestions to return
        
    Returns:
        list: List of suggested courses
    """
    suggested_courses = []
    
    # Build a MongoDB query based on the condition filters
    for filter_item in condition.get('filter', []):
        query = {}
        
        # Handle list filter
        if 'list' in filter_item:
            query = {'course_code': {'$in': filter_item['list']}}
        
        # Handle department and course number filter
        elif 'department' in filter_item and 'course_number' in filter_item:
            query = {
                '$or': [
                    {'departments': filter_item['department']},
                    {'department': filter_item['department']}
                ]
            }
            
            if isinstance(filter_item['course_number'], dict):
                # Handle MongoDB operators
                course_num_query = {}
                for op, val in filter_item['course_number'].items():
                    course_num_query[op] = val
                query['course_number'] = course_num_query
            else:
                query['course_number'] = filter_item['course_number']
        
        # Handle category and level filter
        elif 'category' in filter_item and 'level' in filter_item:
            category = filter_item['category']
            levels = filter_item['level'] if isinstance(filter_item['level'], list) else [filter_item['level']]
            
            level_queries = []
            for level in levels:
                level_queries.append(f"Level - {level}")
                
            query = {
                'formatted_designations': {
                    '$all': [
                        {'$regex': category},
                        {'$in': level_queries}
                    ]
                }
            }
        
        # Handle just category
        elif 'category' in filter_item:
            query = {
                'formatted_designations': {
                    '$regex': filter_item['category']
                }
            }
        
        # Handle just level
        elif 'level' in filter_item:
            levels = filter_item['level'] if isinstance(filter_item['level'], list) else [filter_item['level']]
            level_queries = [f"Level - {level}" for level in levels]
            
            query = {
                'formatted_designations': {
                    '$in': level_queries
                }
            }
        
        # Execute query and get suggestions
        if query:
            async for course in course_collection.find(query).limit(limit):
                suggestion = {
                    'id': str(course['_id']),
                    'code': course.get('course_code', 'Unknown'),
                    'title': course.get('title', 'Unnamed Course'),
                    'credits': course.get('credits', 0)
                }
                if suggestion not in suggested_courses:
                    suggested_courses.append(suggestion)
                    if len(suggested_courses) >= limit:
                        break
        
        # If we have enough suggestions, no need to continue with other filters
        if len(suggested_courses) >= limit:
            break
    
    return suggested_courses

from example_list_of_courses import list_of_courses
from example_conditions import conditions


async def main():
    """
    Example usage of the validation function.
    """
    # Connect to the database
    client = AsyncIOMotorClient(Settings.MONGODB_URI)
    db = client.uwmatch
    course_collection = db.courses
    
    # Validate requirements
    results = await validate_requirements(list_of_courses, conditions, course_collection)
    
    # Print results
    print("\n========== REQUIREMENTS VALIDATION RESULTS ==========\n")
    
    # Print fulfilled requirements
    print(f"✅ FULFILLED REQUIREMENTS ({len(results['fulfilled_requirements'])}/{len(conditions)}):")
    for req in results['fulfilled_requirements']:
        print(f"  • {req['description']}: {req['current']}/{req['needed']} {req['val_type'].replace('min_', '')}")
        print(f"    Courses used:")
        for course in req['courses_that_match']:
            print(f"    - {course['code']}: {course['title']} ({course['credits']} credits)")
        print()
    
    # Print unfulfilled requirements
    if results['unfulfilled_requirements']:
        print(f"❌ UNFULFILLED REQUIREMENTS ({len(results['unfulfilled_requirements'])}/{len(conditions)}):")
        for req in results['unfulfilled_requirements']:
            print(f"  • {req['description']}: {req['current']}/{req['needed']} {req['val_type'].replace('min_', '')}")
            
            if req['courses_that_match']:
                print(f"    Partial credit from:")
                for course in req['courses_that_match']:
                    print(f"    - {course['code']}: {course['title']} ({course['credits']} credits)")
            
            print(f"    Suggested courses to fulfill this requirement:")
            if req['suggested_courses']:
                for course in req['suggested_courses']:
                    print(f"    - {course['code']}: {course['title']} ({course['credits']} credits)")
            else:
                print(f"    - No specific suggestions available")
            print()
    
    # Print summary
    print("📊 SUMMARY:")
    print(f"  • Total requirements: {results['summary']['total_requirements']}")
    print(f"  • Fulfilled: {results['summary']['fulfilled']}")
    print(f"  • Unfulfilled: {results['summary']['unfulfilled']}")
    print(f"  • Completion: {results['summary']['completion_percentage']}%")
    
    # Close the connection
    client.close()

if __name__ == "__main__":
    asyncio.run(main()) 