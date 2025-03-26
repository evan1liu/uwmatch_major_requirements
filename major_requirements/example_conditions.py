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

{
  "name": "Electrical Engineering",
  "total_credits_required": 120,
  "requirements": [
    {
      "id": "general_education",
      "name": "University General Education Requirements",
      "description": "Core requirements that all undergraduate students must fulfill",
      "requirements": [
        {
          "id": "breadth_humanities",
          "name": "Breadth—Humanities/Literature/Arts",
          "validation": {"min_credits": 6},
          "filters": [{"category": "Humanities"}]
        },
        {
          "id": "breadth_natural_science",
          "name": "Breadth—Natural Science",
          "description": "4-5 credits with lab component OR two courses totaling 6 credits",
          "validation_type": "alternative",
          "alternatives": [
            {
              "validation": {"min_credits": 4},
              "filters": [{"category": "Natural Science", "has_lab": true}]
            },
            {
              "validation": {"min_credits": 6},
              "filters": [{"category": "Natural Science"}]
            }
          ]
        },
        {
          "id": "breadth_social",
          "name": "Breadth—Social Studies",
          "validation": {"min_credits": 3},
          "filters": [{"category": "Social Studies"}]
        },
        {
          "id": "communication",
          "name": "Communication Part A & Part B",
          "validation_type": "all",
          "requirements": [
            {
              "id": "comm_a",
              "name": "Communication A",
              "validation": {"min_courses": 1},
              "filters": [{"category": "Communication Part A"}]
            },
            {
              "id": "comm_b",
              "name": "Communication B",
              "validation": {"min_courses": 1},
              "filters": [{"category": "Communication Part B"}]
            }
          ]
        },
        {
          "id": "ethnic_studies",
          "name": "Ethnic Studies",
          "validation": {"min_courses": 1},
          "filters": [{"category": "Ethnic Studies"}]
        },
        {
          "id": "quant_reasoning",
          "name": "Quantitative Reasoning Part A & Part B",
          "validation_type": "all",
          "requirements": [
            {
              "id": "quant_a",
              "name": "Quantitative Reasoning A",
              "validation": {"min_courses": 1},
              "filters": [{"category": "Quantitative Reasoning Part A"}]
            },
            {
              "id": "quant_b",
              "name": "Quantitative Reasoning B",
              "validation": {"min_courses": 1},
              "filters": [{"category": "Quantitative Reasoning Part B"}]
            }
          ]
        }
      ]
    },
    {
      "id": "mathematics",
      "name": "Mathematics",
      "validation": {"min_credits": 16},
      "requirements": [
        {
          "id": "calculus_1",
          "name": "Calculus and Analytic Geometry 1",
          "validation": {"min_courses": 1},
          "filters": [
            {"list": ["MATH 221", "MATH 217"]}
          ]
        },
        {
          "id": "calculus_2",
          "name": "Calculus and Analytic Geometry 2",
          "validation": {"min_courses": 1},
          "filters": [
            {"list": ["MATH 222"]}
          ]
        },
        {
          "id": "calculus_multivariable",
          "name": "Calculus--Functions of Several Variables",
          "validation_type": "alternative",
          "alternatives": [
            {
              "validation": {"min_courses": 1},
              "filters": [{"list": ["MATH 234"]}]
            },
            {
              "validation": {"min_courses": 2},
              "filters": [{"list": ["MATH 375", "MATH 376"]}],
              "satisfies_additional": ["advanced_math_auxiliary", "professional_electives"]
            }
          ]
        },
        {
          "id": "probability_stats",
          "name": "Probability and Statistics Elective",
          "validation": {"min_courses": 1},
          "filters": [
            {"list": ["STAT 311", "STAT/M E 424", "MATH/STAT 431", "E C E 331"]}
          ]
        },
        {
          "id": "advanced_math_auxiliary",
          "name": "Advanced Mathematics Auxiliary Condition",
          "validation": {"min_courses": 1},
          "filters": [
            {"list": ["MATH 319", "MATH 320", "MATH 340", "MATH 341", "E C E 334", "E C E/COMP SCI/M E 532"]}
          ],
          "constraints": {
            "type": "fulfillment_source",
            "description": "Can be fulfilled through dedicated courses or through courses that satisfy other requirements"
          }
        }
      ]
    },
    {
      "id": "science",
      "name": "Science",
      "validation": {"min_credits": 17},
      "requirements": [
        {
          "id": "programming",
          "name": "Programming II",
          "validation": {"min_courses": 1},
          "filters": [{"list": ["COMP SCI 300"]}]
        },
        {
          "id": "physics_1",
          "name": "General Physics 1",
          "validation_type": "alternative",
          "alternatives": [
            {
              "validation": {"min_courses": 1},
              "filters": [{"list": ["PHYSICS 201", "PHYSICS 207", "PHYSICS 247"]}]
            },
            {
              "validation": {"min_courses": 2},
              "filters": [{"list": ["E M A 201", "E M A 202"]}]
            }
          ]
        },
        {
          "id": "physics_2",
          "name": "General Physics 2",
          "validation": {"min_courses": 1},
          "filters": [{"list": ["PHYSICS 202", "PHYSICS 208", "PHYSICS 248"]}]
        },
        {
          "id": "chemistry",
          "name": "Chemistry Requirement",
          "validation": {"min_courses": 1},
          "filters": [{"list": ["CHEM 109", "CHEM 103", "CHEM 104"]}]
        }
      ]
    },
    {
      "id": "ee_core",
      "name": "Electrical Engineering Core",
      "validation": {"min_credits": 32},
      "requirements": [
        {
          "id": "core_courses",
          "name": "Core EE Courses",
          "validation": {"min_courses": 12},
          "filters": [
            {"list": ["E C E 203", "E C E 210", "E C E 222", "E C E 230", 
                      "E C E/PHYSICS 235", "E C E/COMP SCI 252", "E C E 270", 
                      "E C E 271", "E C E 330", "E C E 340", 
                      "E C E/COMP SCI 352", "E C E 370"]}
          ]
        }
      ]
    },
    {
      "id": "ee_advanced_electives",
      "name": "Electrical Engineering Advanced Electives",
      "description": "Students must take 22 credits in at least three of six areas and at least 2 credits in two laboratory courses",
      "validation": {
        "min_credits": 22, 
        "min_areas": 3
      },
      "requirements": [
        {
          "id": "lab_requirement",
          "name": "Laboratory Requirement",
          "description": "At least 2 credits in two laboratory courses",
          "validation": {"min_courses": 2, "min_credits": 2},
          "filters": [{"category": "EE Lab"}],
          "constraints": {"courses_from_list": ["E C E 303", "E C E 304", "E C E 305", "E C E 306", "E C E 308", "E C E 313", "E C E 315", "E C E 317", "E C E 432", "E C E 453", "E C E/B M E 462", "E C E 504", "E C E 512", "E C E 545", "E C E 549", "E C E 554", "E C E/M E 577"]}
        },
        {
          "id": "capstone_requirement",
          "name": "Capstone Requirement",
          "description": "At least one course must be a capstone design course",
          "validation": {"min_courses": 1},
          "filters": [{"list": ["E C E 453", "E C E 454", "E C E 455", "E C E 554"]}]
        },
        {
          "id": "advanced_math_requirement",
          "name": "Advanced Math Requirement",
          "description": "At least one course must satisfy the advanced math auxiliary condition",
          "reference": "advanced_math_auxiliary"
        },
        {
          "id": "area_fields_waves",
          "name": "Fields & Waves",
          "validation": {"min_credits": 0},
          "area_id": "fields_waves",
          "filters": [
            {"list": ["E C E 320", "E C E 420", "E C E 434", "E C E/N E/PHYSICS 525", 
                     "E C E/N E/PHYSICS 527", "E C E/N E 528", "E C E 536", 
                     "E C E 546", "E C E 547"]}
          ]
        },
        {
          "id": "area_systems_control",
          "name": "Systems & Control",
          "validation": {"min_credits": 0},
          "area_id": "systems_control",
          "filters": [
            {"list": ["E C E 332", "E C E 334", "E C E/M E 439", "E C E/M E 577"]}
          ]
        },
        {
          "id": "area_power_machines",
          "name": "Power & Machines",
          "validation": {"min_credits": 0},
          "area_id": "power_machines",
          "filters": [
            {"list": ["E C E 355", "E C E 356", "E C E 411", "E C E 412", 
                     "E C E 427", "E C E 504", "E C E 511", "E C E 512"]}
          ]
        },
        {
          "id": "area_communications",
          "name": "Communications & Signal Processing",
          "validation": {"min_credits": 0},
          "area_id": "communications",
          "filters": [
            {"list": ["E C E 331", "E C E 401", "E C E 431", "E C E 432", 
                     "E C E/COMP SCI/MATH 435", "E C E 436", "E C E 437", 
                     "E C E 447", "E C E/COMP SCI/M E 532", "E C E/COMP SCI 533", 
                     "E C E 537", "E C E/COMP SCI/M E 539", "E C E/I SY E 570", 
                     "E C E/MATH 641"]}
          ]
        },
        {
          "id": "area_circuits_devices",
          "name": "Circuits & Devices",
          "validation": {"min_credits": 0},
          "area_id": "circuits_devices",
          "filters": [
            {"list": ["E C E 335", "E C E 342", "E C E 445", "E C E/B M E 462", 
                     "E C E 466", "E C E 541", "E C E 542", "E C E 545", 
                     "E C E 548", "E C E 549", "E C E 555"]}
          ]
        },
        {
          "id": "area_computers",
          "name": "Computers & Computing",
          "validation": {"min_credits": 0},
          "area_id": "computers",
          "filters": [
            {"list": ["E C E 353", "E C E/COMP SCI 354", "E C E 453", "E C E 454", 
                     "E C E/B M E 463", "E C E/COMP SCI 506", "E C E 551", 
                     "E C E/COMP SCI 552", "E C E 553", "E C E 554", "E C E 556"]}
          ]
        }
      ],
      "constraints": [
        {
          "type": "min_areas",
          "value": 3,
          "areas": ["fields_waves", "systems_control", "power_machines", "communications", "circuits_devices", "computers"]
        },
        {
          "type": "course_credits",
          "description": "At least 9 credits must be in E C E courses numbered 400 and above",
          "filters": [{"department": "E C E", "course_number": {"$gte": 400}}],
          "min_credits": 9
        }
      ]
    },
    {
      "id": "professional_electives",
      "name": "Professional Electives",
      "validation": {"min_credits": 9},
      "filters": [
        {"list": ["MATH/COMP SCI 240", "E C E 204", "E C E 320", "E C E 331", "E C E 332", 
                 "E C E 334", "E C E 335", "E C E 342", "E C E 353", "E C E/COMP SCI 354", 
                 "E C E 355", "E C E 356"]},
        {"department": "E C E", "course_number": {"$gte": 399}},
        {"department": "COMP SCI", "course_number": {"$gte": 400}},
        {"list": ["MATH 319", "MATH 320", "MATH 321", "MATH 322", "MATH 340", "MATH 341"]},
        {"department": "MATH", "course_number": {"$gte": 400}},
        {"department": "STATS", "course_number": {"$gte": 400}},
        {"category": "Biological Science", "level": ["Intermediate", "Advanced"]},
        {"category": "Physical Science", "level": ["Intermediate", "Advanced"], "not_list": ["PHYSICS 241"]},
        {"category": "Natural Science", "level": ["Advanced"], 
         "not_departments": ["MATH", "COMP SCI", "STATS"]}
      ],
      "constraints": [
        {
          "type": "max_credits",
          "description": "Up to six credits of Professional Electives can be taken from School of Business classes numbered 300 and higher",
          "filters": [{"school": "Business", "course_number": {"$gte": 300}}],
          "max_credits": 6
        },
        {
          "type": "exclusion",
          "description": "Students may only earn degree credit for MATH 320 or MATH 340, not both",
          "exclusive_groups": [["MATH 320", "MATH 340"]]
        }
      ]
    },
    {
      "id": "communication_skills",
      "name": "Communication Skills",
      "validation": {"min_credits": 6},
      "requirements": [
        {
          "id": "first_comm_course",
          "name": "First Communication Course",
          "validation": {"min_courses": 1},
          "filters": [{"list": ["ENGL 100", "LSC 100", "COM ARTS 100", "COM ARTS 181", "ESL 118"]}]
        },
        {
          "id": "engineering_comm",
          "name": "Engineering Communication",
          "validation": {"min_courses": 1},
          "filters": [{"list": ["INTEREGR 397"]}]
        }
      ]
    },
    {
      "id": "liberal_studies",
      "name": "Liberal Studies Electives",
      "validation": {"min_credits": 15},
      "filters": [
        {"designations": ["H", "S", "L", "Z"]},
        {"category": "Language"}
      ]
    },
    {
      "id": "free_elective",
      "name": "Free Elective",
      "validation": {"min_credits": 1},
      "filters": [{}]  // No specific filters - any course can count
    }
  ],
  "honors": {
    "id": "honors_research",
    "name": "Honors in Undergraduate Research Program",
    "requirements": [
      {
        "id": "honors_gpa",
        "name": "GPA Requirement",
        "validation": {"min_gpa": 3.3}
      },
      {
        "id": "honors_credits",
        "name": "Honors Research Credits",
        "validation": {"min_credits": 6, "min_grade": "B"},
        "filters": [{"list": ["E C E 489"]}]
      }
    ]
  }
}

