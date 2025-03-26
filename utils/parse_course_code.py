def parse_course_code(course_code: str) -> dict:
    """The function takes a course code as a string, and returns a dictionary 
    with a list of department names and a course number

    Args:
        course_code (str): DEPT1/DEPT2 100 (e.g. "COMP SCI/E C E 252")

    Returns:
        dict: {'departments': ['DEPT1', 'DEPT2'], 'course_number': 100}
        (e.g. {'departments': ['COMP SCI', 'ECE'], 'course_number': 252})
    """
    import re
    
    pattern = r'^(.*)\s+(\d+\w*)$'
    match = re.match(pattern, course_code)
    
    if match:
        dept_str = match.group(1)
        course_num = match.group(2)
        
        # Split by '/' and remove whitespace
        parsed_departments = []
        for dept in dept_str.split('/'):
            cleaned_dept = dept.strip()
            parsed_departments.append(cleaned_dept)
        
        return {
            "departments": parsed_departments,
            "course_number": course_num
        }
    else:
        return None

def main():
    example_course_code = "AGROECOL/AGRONOMY/C&E SOC/ENTOM/ENVIR ST 103"
    
    """ Expected output: 
        {"departments": ["AGROECOL", "AGRONOMY", "C&E SOC", "ENTOM", "ENVIR ST"],
        "course_number": "103"}
    """
    
    parsed_dict = parse_course_code(example_course_code)
    print(parsed_dict)
    
if __name__ == "__main__":
    main()