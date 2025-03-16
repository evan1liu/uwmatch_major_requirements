# Each condition consists of a description, validation type, validation value, and filters.
# Filters:
#   - "filters" can be a list of filters or a single filter item.
#   - If there are multiple filter items, a course only needs to fit into one of them.
#   - Each filter item is a dictionary that can contain multiple key/value pairs for filter criteria.
#   - If a filter item has multiple key-value pairs, the course must satisfy all those requirements.
#   - To validate, we iterate through the filters list, starting with the first dictionary and the first key.
# Validation Function:
#   - We use a function that takes a "course id" (a string) and a "condition" (a dictionary like the ones below).
#   - It returns whether or not the course passes the given condition.
#   - We iterate through the conditions, and for each condition we iterate through all the course IDs in the roadmap
# What makes a "Condition"?:
#   - Major requirements are complex, but at the most bottom it's a "condition"
#   - A condition exists when there's a minimum number of credits or courses required
#   - It doesn't even have to be required,
#   - it could be additional conditions like MATH 375/376 that replaces MATH 234, auxilary math, and provide for professional credits
#   - it could be EMA 201/202 that replaces the requirements for PHYSICS 201
# More with "Conditions":
#   - Courses that satisfy a condition are based on the filter criteria.
#   - A course could multiple conditions, it's essential to record the course and the specific condition(s) it satisfies.
#   - After passing the course id and condition into the function, if the course satisfies the condition, we attach the given condition to the course object.
#   - After iterating through all the conditions, we then start dealing with those special limitations
# After iterating through conditions
#   - After iterating through all the conditions, there could be conditions that are not fulfilled
#   - When conditions for MATH 234 and auxiliary math are not fulfilled, but MATH 375/376 are fulfilled. It's still considered good.
#   - Therefore, we need a field for each condition dictionary specifically for describing the relationships between conditions
# New kind of validation type:
#   - There's this validation type that is minimum number of areas, you need to take 22 credits in at least three of the six areas
#   - Therefore, validation type can actually be...
#   - Wait, maybe validation_method should be a dictionary, {min_credits: 9}, or {min_credits: 22, min_areas: 3}
#   - in that way, we can accomodate a more special type of validation that has two kinds of minimums: min_credits & min_areas
# Other considerations:
#   - For some courses, there are limitations for maximum number of credits you can get
#   - How to deal with conditions that satisfy multiple requirements?
#   - EX: A course fulfills a given requirement therefore cannot be used to fulfill any other requirements

example_condition_1 = {
        'description': 'Professional Electives',
        'filters': [
            {'list': ['MATH/COMP SCI 240', 'E C E 204', 'E C E 320', 'E C E 331', 'E C E 332', 'E C E 334']},
            {'department': 'E C E', 'course_number': {'$gte': 400}},
            {'category': 'Biological Science', 'level': ['Intermediate', 'Advanced']}
        ],
        'validation': {'min_credits': 9}
}
example_condition_2 = {
        'description': 'Communication Requirement',
        'filters': [
            {'category': 'Communication Part A'}
        ],
        'validation': {'min_courses': 1}
}


