example_nested_requirement = {
    "name": "Electrical Engineering Advanced Electives",
    "requirement_id": "ee_advanced_electives", # NOTE: MAKE SURE TO ALWAYS USE UNDERSCORE!!!
                                               # TODO: CHANGE ALL FIELD NAMES TO UNDERSCORES IN MONGODB COLLECTIONS
    "description": " ".join("""Classes to be taken in an area of professional interest.
                    The following courses are acceptable as professional electives
                    if the courses are not used to meet any other degree requirements.""".split()),
    "validation": {"min_credits": 9},

    "requirements":
        [
            {
                "description": "At least 9 credits must be in E C E courses numbered 400 and above.",
                "validation": {"min_credits": 9},
                "filter": {"department": "E C E", "course_number_range": {"$gte": 400}}
             },
            {
                "description": "At least one course must be a capstone design course from the following list: E C E 453 Embedded Microprocessor System Design, E C E 454 Mobile Computing Laboratory, E C E 455 Capstone Design in Electrical and Computer Engineering, E C E 554 Digital Engineering Laboratory. These courses are also indicated in the areas below with a *.",
                "validation": {"min_courses": 1},
                "filter": {"course_codes": ["E C E 453", "E C E 454", "E C E 455", "E C E 554"]}
            },
            # TODO: FIND A WAY TO FIT THE AUXILARY MATH REQUIREMENT TO THE NESTED REQUIREMENTS
            {
                "description": "Students must take at least 2 credits in two laboratory courses.",
                "validation": {"min_credits: 2"},
                "requirements": [
                    {"description": "Select at least one course from E C E 301 to E C E 317",
                     "validation": {"min_courses": 1},
                     "filter": {"department": "E C E", "course_number_range": {"$gte": 301, "$lte": 317}}},
                    {"description": "An additional laboratory course must be taken from the following list:",
                     "validation": {"min_courses": 1},
                     "filter": {"course_codes": ["E C E 303", "E C E 304", "E C E 305", "E C E 306", "E C E 308", "E C E 313", "E C E 315", "E C E 317", "E C E 432", "E C E 453", "E C E/B M E  462", "E C E 504", "E C E 512", "E C E 545", "E C E 549", "E C E 554", "E C E/M E  577"]}}
                ]
            },
            {
                "description": "Students must take 22 credits in at least three of six areas",
                "validation": {???},
                "requirements": [
                    {"description": "Fields & Waves",
                     "validation": {"min_courses": 1},
                     "course_codes": ["E C E 320", "E C E 420", "E C E 434", "E C E/N E/PHYSICS  525", "E C E/N E/PHYSICS  527", "E C E/N E  528", "E C E 536", "E C E 546", "E C E 547"]},
                    {"description": "Systems & Control",
                     "validation": {"min_courses": 1},
                     "course_codes": ["E C E 332", "E C E 334", "E C E/M E  439", "E C E/M E  577"]},
                    {"description": "Power & Machines",
                     "validation": {"min_courses": 1},
                     "course_codes": ["E C E 355", "E C E 356", "E C E 411", "E C E 412", "E C E 427", "E C E 504", "E C E 511", "E C E 512"]},
                    {"description": "Communications & Signal Processing",
                     "validation": {"min_courses": 1},
                     "course_codes": ["E C E 331", "E C E 401", "E C E 431", "E C E 432", "E C E/COMP SCI/MATH  435", "E C E 436", "E C E 437", "E C E 447", "E C E/COMP SCI/M E  532", "E C E/COMP SCI  533", "E C E 537", "E C E/COMP SCI/M E  539", "E C E/I SY E  570", "E C E/MATH  641"]},
                    {"description": "Circuits & Devices",
                     "validation": {"min_courses": 1},
                     "course_codes": ["E C E 335", "E C E 342", "E C E 445", "E C E/B M E  462", "E C E 466", "E C E 541", "E C E 542", "E C E 545", "E C E 548", "E C E 549", "E C E 555"]},
                    {"description": "Computers & Computing",
                     "validation": {"min_courses": 1},
                     "course_codes": ["E C E 353", "E C E/COMP SCI  354", "E C E 453", "E C E 454", "E C E/B M E  463", "E C E/COMP SCI  506", "E C E 551", "E C E/COMP SCI  552", "E C E 553", "E C E 554", "E C E 556"]}
                ]
            }
        ],
    "filters": [
        {"description": "Students can take E C E 379 Special Topics in Electrical and Computer Engineering and E C E 601 Special Topics in Electrical and Computer Engineering as advanced electives.",
         "course_codes": ["E C E 379", "E C E 601"]},
        {"description": "E C E courses numbered 300 that are not specified in an area can count toward the total number of advanced elective credits required.",
         "department": "E C E", "course_number_range": {"$gte": 300, "$lte": 399}},
        
        
    ]
}