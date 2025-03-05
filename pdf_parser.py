import re

# Load the text from the PDF
with open("report-gradedistribution-2024-2025fall.txt", "r") as f:
    text = f.read()

# Define the course title
course_title = "Intro to Ag & Applied Econ"

# Find the line that contains the course title
course_line = re.search(f".*{course_title}.*", text).group(0)

course_total_match = re.search(f".*{course_line}.*\n.*Course Total.*", text)
if course_total_match:
    course_total_line = course_total_match.group(0)
    # Extract the course total using a regular expression
    course_total = re.search(r"Course Total\s+(\d+)", course_total_line).group(1)
    # Print the course total
    print(f"Course total for {course_title}: {course_total}")
else:
    print(f"Could not find course total for {course_title}")