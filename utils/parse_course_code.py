# the function below will take a string "course code"
# and then parse it into a dictionary with a "departments" list, and a "course number"

example_course_code = "AGROECOL/​AGRONOMY/​C&E SOC/​ENTOM/​ENVIR ST 103"
# expected output: 
# {
# "departments": ["AGROECOL", "AGRONOMY", "C&E SOC", "ENTOM", "ENVIR ST"],
# "course_number": "103"
# }

def parse_course_code(course_code: str) -> dict:
    import re
    
    pattern = r'^(.*)\s+(\d+\w*)$'
    match = re.match(pattern, course_code)
    
    if match:
        dept_str = match.group(1)
        course_num = match.group(2)
        
        # Split by '/' and remove any zero-width spaces or other whitespace
        parsed_departments = []
        for dept in dept_str.split('/'):
            # Strip regular whitespace and also remove zero-width space character (\u200b)
            cleaned_dept = dept.strip().replace('\u200b', '')
            parsed_departments.append(cleaned_dept)
        
        return {
            "departments": parsed_departments,
            "course_number": course_num
        }
    else:
        return None

def main():
    parsed_dict = parse_course_code(example_course_code)
    print(parsed_dict)
    
if __name__ == "__main__":
    main()