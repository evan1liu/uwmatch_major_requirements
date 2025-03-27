from major_requirements.handle_filter import course_passes_filter

from major_requirements.handle_requirement import course_updates_requirement, requirement_passed

async def process_nested_requirement_with_course(course: dict, requirement: dict) -> dict:
    """
    Process a single course against a nested requirement structure.
    Aggregates course information and credits from sub-requirements to parent.
    
    Args:
        course (dict): A single course to evaluate
        requirement (dict): Requirement structure which may contain sub-requirements
        
    Returns:
        dict: Updated requirement with validation information
    """
    # Step 1: Process this requirement's direct filters using existing function
    # This already handles both "filter" and "filters" cases
    requirement = await course_updates_requirement(course, requirement)
    
    # Step 2: If this requirement has sub-requirements, process them recursively
    if "requirements" in requirement:
        # Init courses_passed for parent if not present
        if "courses_passed" not in requirement:
            requirement["courses_passed"] = []
            
        sub_req_courses = []  # Track courses passed by sub-requirements
        total_sub_req_credits = 0  # Track credits from sub-requirements
        
        for i, sub_req in enumerate(requirement["requirements"]):
            # Process the same course against each sub-requirement
            updated_sub_req = await process_nested_requirement_with_course(course, sub_req)
            requirement["requirements"][i] = updated_sub_req
            
            # Collect courses passed by sub-requirements
            if "courses_passed" in updated_sub_req:
                for passed_course in updated_sub_req["courses_passed"]:
                    if passed_course not in sub_req_courses:
                        sub_req_courses.append(passed_course)
                        
                    # Add to parent's courses_passed if not already there
                    if passed_course not in requirement["courses_passed"]:
                        requirement["courses_passed"].append(passed_course)
        
        # Update parent requirement's credit count if using min_credits
        if "validation" in requirement and "min_credits" in requirement["validation"]:
            # Reset current_credits to recalculate from courses
            total_credits = sum(course["credits"] for course in requirement["courses_passed"])
            requirement["validation"]["current_credits"] = total_credits
    
    # Step 3: Check if this requirement passes based on its validation criteria
    requirement = await requirement_passed(requirement)
    
    # Step 4: For requirements with sub-requirements, determine if it passes
    # based on both its own validation and its sub-requirements
    if "requirements" in requirement and "validation" in requirement and "passed" in requirement["validation"]:
        # Get validation status of all sub-requirements
        all_sub_reqs_pass = all(
            sub_req.get("validation", {}).get("passed", False) 
            for sub_req in requirement["requirements"]
        )
        
        # Requirement passes only if both its own validation AND all sub-requirements pass
        requirement["validation"]["passed"] = requirement["validation"]["passed"] and all_sub_reqs_pass
    
    return requirement

async def test_nested_requirement_single_course():
    """Test processing of a nested requirement structure with a single course"""
    
    # Example nested requirement with two sub-requirements
    nested_req = {
        "description": "Laboratory courses requirement",
        "validation": {"min_credits": 2},
        "requirements": [
            {
                "description": "Select at least one course from E C E 301 to E C E 317",
                "validation": {"min_courses": 1},
                "filter": {"department": "E C E", "course_number_range": {"$gte": 301, "$lte": 317}}
            },
            {
                "description": "An additional laboratory course",
                "validation": {"min_courses": 1},
                "filter": {"course_codes": ["E C E 453", "E C E 554"]}
            }
        ]
    }
    
    # First example course
    course1 = {
        '_id': '67577f1c7fd66ec727392090',
        'credits': 2,
        'course_number': '305',
        'departments': ['E C E'],
        'course_code': 'E C E 305'
    }
    
    # Process the first course
    result1 = await process_nested_requirement_with_course(course1, nested_req)
    
    print("\nAfter processing first course:")
    print(f"Main requirement passed: {result1.get('validation', {}).get('passed', False)}")
    print("\nSub-requirements:")
    for i, sub_req in enumerate(result1["requirements"]):
        print(f"  {i+1}. {sub_req.get('description', 'Unknown')}")
        print(f"     Passed: {sub_req.get('validation', {}).get('passed', False)}")
    
    # Second example course
    course2 = {
        '_id': '67577f1d7fd66ec7273920d1',
        'credits': 4,
        'course_number': '453',
        'departments': ['E C E'],
        'course_code': 'E C E 453'
    }
    
    # Process the second course with the updated requirement
    result2 = await process_nested_requirement_with_course(course2, result1)
    
    print("\nAfter processing second course:")
    print(f"Main requirement passed: {result2.get('validation', {}).get('passed', False)}")
    print("\nSub-requirements:")
    for i, sub_req in enumerate(result2["requirements"]):
        print(f"  {i+1}. {sub_req.get('description', 'Unknown')}")
        print(f"     Passed: {sub_req.get('validation', {}).get('passed', False)}")
    
    return result2

if __name__ == "__main__":
    import asyncio
    import time
    
    # Measure execution time
    start_time = time.perf_counter()
    asyncio.run(test_nested_requirement_single_course())
    end_time = time.perf_counter()
    
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.4f} seconds")