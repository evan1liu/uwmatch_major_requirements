
{
  "major_name": "Electrical Engineering",
  "total_credits_required": 120,
  "requirement_groups": [
    {
      "name": "Mathematics",
      "description": "Mathematics requirements including calculus, multi-variable calculus, and stats",
      "credits_required": 16,
      "conditions": [
        {
          "description": "Calculus and Analytic Geometry 1",
          "filters": [{"list": ["MATH 221", "MATH 217"]}],
          "validation": {"min_courses": 1}
        },
        {
          "description": "Calculus and Analytic Geometry 2",
          "filters": [{"list": ["MATH 222"]}],
          "validation": {"min_courses": 1}
        },
        {
          "description": "Calculus--Functions of Several Variables",
          "filters": [{"list": ["MATH 234"]}],
          "validation": {"min_courses": 1},
          "alternative_fulfillment": [
            {
              "description": "Honors Calculus Path",
              "filters": [{"list": ["MATH 375", "MATH 376"]}],
              "validation": {"min_courses": 2},
              "additional_credits_apply_to": ["Professional Electives", "Advanced Math Auxiliary"]
            }
          ]
        },
        {
          "description": "Probability and Statistics",
          "filters": [{"list": ["STAT 311", "STAT/M E 424", "MATH/STAT 431", "E C E 331"]}],
          "validation": {"min_courses": 1}
        }
      ],
      "auxiliary_conditions": [
        {
          "name": "Advanced Math Auxiliary",
          "description": "At least one additional math course must be completed",
          "filters": [{"list": ["MATH 319", "MATH 320", "MATH 340", "MATH 341", "E C E 334", "E C E/COMP SCI/M E 532"]}],
          "validation": {"min_courses": 1},
          "credits_apply_to": ["Professional Electives", "Advanced Electives"]
        }
      ]
    },
    {
      "name": "Science",
      "description": "Science requirements including physics, chemistry, and programming",
      "credits_required": 17,
      "conditions": [
        {
          "description": "Programming II",
          "filters": [{"list": ["COMP SCI 300"]}],
          "validation": {"min_courses": 1}
        },
        {
          "description": "General Physics 1",
          "filters": [{"list": ["PHYSICS 201", "PHYSICS 207", "PHYSICS 247"]}],
          "validation": {"min_courses": 1},
          "alternative_fulfillment": [
            {
              "description": "Engineering Mechanics Alternative",
              "filters": [{"list": ["E M A 201", "E M A 202"]}],
              "validation": {"min_courses": 2}
            }
          ]
        },
        {
          "description": "General Physics 2",
          "filters": [{"list": ["PHYSICS 202", "PHYSICS 208", "PHYSICS 248"]}],
          "validation": {"min_courses": 1}
        },
        {
          "description": "Chemistry",
          "filters": [{"list": ["CHEM 109", "CHEM 103", "CHEM 104"]}],
          "validation": {"min_courses": 1}
        }
      ]
    },
    {
      "name": "Electrical Engineering Core",
      "description": "Core courses required for all EE majors",
      "credits_required": 32,
      "conditions": [
        {
          "description": "EE Core Courses",
          "filters": [
            {"list": [
              "E C E 203", "E C E 210", "E C E 222", "E C E 230", 
              "E C E/PHYSICS 235", "E C E/COMP SCI 252", "E C E 270", 
              "E C E 271", "E C E 330", "E C E 340", 
              "E C E/COMP SCI 352", "E C E 370"
            ]}
          ],
          "validation": {"min_courses": 12}
        }
      ]
    },
    {
      "name": "Electrical Engineering Advanced Electives",
      "description": "Advanced electives with distribution requirements across areas",
      "credits_required": 24,
      "conditions": [
        {
          "description": "Advanced Electives Distribution",
          "areas": [
            {
              "name": "Laboratory",
              "filters": [
                {"list": ["E C E 303", "E C E 304", "E C E 305", "E C E 306", 
                  "E C E 308", "E C E 313", "E C E 315", "E C E 317"]}
              ],
              "validation": {"min_courses": 1}
            },
            {
              "name": "Additional Laboratory",
              "filters": [
                {"list": ["E C E 303", "E C E 304", "E C E 305", "E C E 306", 
                  "E C E 308", "E C E 313", "E C E 315", "E C E 317", 
                  "E C E 432", "E C E 453", "E C E/B M E 462", "E C E 504", 
                  "E C E 512", "E C E 545", "E C E 549", "E C E 554", 
                  "E C E/M E 577"]}
              ],
              "validation": {"min_courses": 1}
            },
            {
              "name": "Fields & Waves",
              "filters": [
                {"list": ["E C E 320", "E C E 420", "E C E 434", 
                  "E C E/N E/PHYSICS 525", "E C E/N E/PHYSICS 527", 
                  "E C E/N E 528", "E C E 536", "E C E 546", "E C E 547"]}
              ]
            },
            {
              "name": "Systems & Control",
              "filters": [
                {"list": ["E C E 332", "E C E 334", "E C E/M E 439", "E C E/M E 577"]}
              ]
            },
            {
              "name": "Power & Machines",
              "filters": [
                {"list": ["E C E 355", "E C E 356", "E C E 411", "E C E 412", 
                  "E C E 427", "E C E 504", "E C E 511", "E C E 512"]}
              ]
            },
            {
              "name": "Communications & Signal Processing",
              "filters": [
                {"list": ["E C E 331", "E C E 401", "E C E 431", "E C E 432", 
                  "E C E/COMP SCI/MATH 435", "E C E 436", "E C E 437", 
                  "E C E 447", "E C E/COMP SCI/M E 532", "E C E/COMP SCI 533", 
                  "E C E 537", "E C E/COMP SCI/M E 539", "E C E/I SY E 570", 
                  "E C E/MATH 641"]}
              ]
            },
            {
              "name": "Circuits & Devices",
              "filters": [
                {"list": ["E C E 335", "E C E 342", "E C E 445", "E C E/B M E 462", 
                  "E C E 466", "E C E 541", "E C E 542", "E C E 545", 
                  "E C E 548", "E C E 549", "E C E 555"]}
              ]
            },
            {
              "name": "Computers & Computing",
              "filters": [
                {"list": ["E C E 353", "E C E/COMP SCI 354", "E C E 453", 
                  "E C E 454", "E C E/B M E 463", "E C E/COMP SCI 506", 
                  "E C E 551", "E C E/COMP SCI 552", "E C E 553", 
                  "E C E 554", "E C E 556"]}
              ]
            }
          ],
          "validation": {
            "min_areas": 3,
            "min_credits": 22,
            "additional_requirements": [
              {
                "type": "min_courses",
                "courses": {
                  "filters": [{"list": ["E C E 453", "E C E 454", "E C E 455", "E C E 554"]}]
                },
                "count": 1,
                "description": "Capstone Design Course"
              },
              {
                "type": "min_credits",
                "courses": {
                  "filters": [{"department": "E C E", "course_number": {"$gte": 400}}]
                },
                "count": 9,
                "description": "At least 9 credits must be in E C E courses numbered 400 and above"
              }
            ]
          }
        }
      ],
      "special_conditions": [
        {
          "description": "Independent Study or Research Credits",
          "filters": [
            {"list": ["E C E 399", "E C E 489", "E C E 699"]}
          ],
          "validation": {"max_credits": 6}
        },
        {
          "description": "Cooperative Education",
          "filters": [{"list": ["E C E 1"]}],
          "validation": {"max_credits": 1}
        },
        {
          "description": "Special Topics",
          "filters": [{"list": ["E C E 379", "E C E 601"]}],
          "validation": {"count_toward": "Advanced Electives"}
        },
        {
          "description": "COMP SCI Advanced Courses",
          "filters": [{"department": "COMP SCI", "course_number": {"$gte": 500}}],
          "validation": {"max_credits": 5, "exclude": ["Independent Study"]}
        }
      ]
    },
    {
      "name": "Professional Electives",
      "description": "Courses to be taken in an area of professional interest",
      "credits_required": 9,
      "conditions": [
        {
          "description": "Professional Electives",
          "filters": [
            {"list": ["MATH/COMP SCI 240", "E C E 204", "MATH 319", "MATH 320", 
              "MATH 321", "MATH 322", "MATH 340", "MATH 341"]},
            {"department": "E C E", "course_number": {"$gte": 320, "$lt": 399}},
            {"department": "E C E", "course_number": {"$gte": 399}},
            {"department": "COMP SCI", "course_number": {"$gte": 400}},
            {"department": "MATH", "course_number": {"$gte": 400}},
            {"department": "STATS", "course_number": {"$gte": 400}},
            {"category": "Biological Science", "level": ["Intermediate", "Advanced"]},
            {"category": "Physical Science", "level": ["Intermediate", "Advanced"], 
             "exclude": ["PHYSICS 241"]},
            {"category": "Natural Science", "level": ["Advanced"], 
             "exclude": ["MATH", "COMP SCI", "STATS"]},
            {"school": "Engineering", "course_number": {"$gte": 300}, 
             "exclude_departments": ["E C E"]},
            {"school": "Business", "course_number": {"$gte": 300}},
            {"list": ["DS 501", "DANCE 560"]}
          ],
          "validation": {"min_credits": 9}
        }
      ],
      "special_conditions": [
        {
          "description": "Business School Limit",
          "filters": [{"school": "Business", "course_number": {"$gte": 300}}],
          "validation": {"max_credits": 6}
        },
        {
          "description": "MATH Course Exclusion",
          "notes": "Students may only earn degree credit for MATH 320 or MATH 340, not both"
        }
      ]
    },
    {
      "name": "Communication Skills",
      "description": "Required communication courses",
      "credits_required": 6,
      "conditions": [
        {
          "description": "First Communication Course",
          "filters": [{"list": ["ENGL 100", "LSC 100", "COM ARTS 100", "COM ARTS 181", "ESL 118"]}],
          "validation": {"min_courses": 1}
        },
        {
          "description": "Engineering Communication",
          "filters": [{"list": ["INTEREGR 397"]}],
          "validation": {"min_courses": 1}
        }
      ]
    },
    {
      "name": "Liberal Studies",
      "description": "Liberal studies electives",
      "credits_required": 15,
      "conditions": [
        {
          "description": "Liberal Studies Requirement",
          "filters": [
            {"attribute": ["H", "S", "L", "Z"]},
            {"category": "Language"}
          ],
          "validation": {"min_credits": 15}
        }
      ]
    },
    {
      "name": "Free Electives",
      "description": "Additional coursework to reach 120 total credits",
      "credits_required": 1
    },
    {
      "name": "University General Education Requirements",
      "description": "University-wide requirements that must be fulfilled",
      "conditions": [
        {
          "description": "Breadth-Humanities/Literature/Arts",
          "filters": [{"breadth": "Humanities/Literature/Arts"}],
          "validation": {"min_credits": 6}
        },
        {
          "description": "Breadth-Natural Science",
          "filters": [
            {"breadth": "Natural Science", "has_lab": true},
            {"breadth": "Natural Science"}
          ],
          "validation": {
            "min_credits": 4,
            "options": [
              {"type": "one_course_with_lab", "min_credits": 4},
              {"type": "two_courses", "min_credits": 6}
            ]
          }
        },
        {
          "description": "Breadth-Social Studies",
          "filters": [{"breadth": "Social Studies"}],
          "validation": {"min_credits": 3}
        },
        {
          "description": "Communication Part A",
          "filters": [{"attribute": "Communication A"}],
          "validation": {"min_courses": 1}
        },
        {
          "description": "Communication Part B",
          "filters": [{"attribute": "Communication B"}],
          "validation": {"min_courses": 1}
        },
        {
          "description": "Ethnic Studies",
          "filters": [{"attribute": "Ethnic Studies"}],
          "validation": {"min_courses": 1}
        },
        {
          "description": "Quantitative Reasoning Part A",
          "filters": [{"attribute": "Quantitative Reasoning A"}],
          "validation": {"min_courses": 1}
        },
        {
          "description": "Quantitative Reasoning Part B",
          "filters": [{"attribute": "Quantitative Reasoning B"}],
          "validation": {"min_courses": 1}
        }
      ]
    }
  ]
}
```

## Code Updates

Here are the necessary code updates to handle this complex structure:

```python:optimized_validation_requirements.py
# New function to handle hierarchical areas in advanced electives
async def mem_handle_areas_criterion(course: dict, areas: List[dict], validation: dict) -> dict:
    """
    Handle complex area distribution requirements with in-memory course data
    Returns a dict with areas fulfilled and related metrics
    """
    fulfilled_areas = []
    total_credits = 0
    area_details = {}
    
    for area in areas:
        area_name = area["name"]
        area_passes = False
        
        # Check each filter in the area
        for filter_criteria in area.get("filters", []):
            for criterion_type, criterion in filter_criteria.items():
                handler = mem_criterion_handlers.get(criterion_type)
                if handler and await handler(course, criterion):
                    area_passes = True
                    
                    # Calculate credits for this area
                    area_credits = course.get("credits", 0)
                    total_credits += area_credits
                    
                    # Track details
                    if area_name not in area_details:
                        area_details[area_name] = {
                            "courses": [],
                            "total_credits": 0
                        }
                    
                    area_details[area_name]["courses"].append({
                        "course_id": str(course.get("_id")),
                        "course_code": course.get("course_code", ""),
                        "credits": area_credits
                    })
                    area_details[area_name]["total_credits"] += area_credits
                    break
            
            if area_passes:
                fulfilled_areas.append(area_name)
                break
    
    return {
        "fulfilled_areas": fulfilled_areas,
        "distinct_areas_count": len(set(fulfilled_areas)),
        "total_credits": total_credits,
        "area_details": area_details
    }

# Function to handle additional requirements in validation
async def mem_handle_additional_requirements(course: dict, requirements: List[dict]) -> dict:
    """
    Process additional requirements specified in validation rules
    Returns dict of requirement fulfillment status
    """
    results = {}
    
    for req in requirements:
        req_type = req.get("type")
        req_name = req.get("description", "Unnamed Requirement")
        
        if req_type == "min_courses" or req_type == "min_credits":
            # Check courses that match filters
            matches = False
            for filter_criteria in req.get("courses", {}).get("filters", []):
                for criterion_type, criterion in filter_criteria.items():
                    handler = mem_criterion_handlers.get(criterion_type)
                    if handler and await handler(course, criterion):
                        matches = True
                        break
                if matches:
                    break
            
            if matches:
                if req_name not in results:
                    results[req_name] = {
                        "courses": [],
                        "credits": 0
                    }
                
                results[req_name]["courses"].append({
                    "course_id": str(course.get("_id")),
                    "course_code": course.get("course_code", ""),
                    "credits": course.get("credits", 0)
                })
                results[req_name]["credits"] += course.get("credits", 0)
    
    return results

# Update the course_meets_condition_mem function to handle the hierarchical structure
async def course_meets_condition_mem(course: dict, condition: dict) -> dict:
    """
    Enhanced function to evaluate course against conditions 
    Returns a dict with detailed assessment results
    """
    # First handle the simple case for backward compatibility
    if "filters" in condition:
        simple_result = await check_simple_condition(course, condition)
        return {
            "passes": simple_result,
            "details": {"simple_filter": simple_result}
        }
    
    # Handle complex hierarchical requirements
    results = {
        "passes": False,
        "areas_fulfilled": [],
        "additional_requirements_met": {},
        "credits_applied": 0,
        "details": {}
    }
    
    # Handle areas distribution if present
    if "areas" in condition:
        areas_result = await mem_handle_areas_criterion(
            course, 
            condition.get("areas", []), 
            condition.get("validation", {})
        )
        
        results["areas_fulfilled"] = areas_result["fulfilled_areas"]
        results["credits_applied"] += areas_result["total_credits"]
        results["details"]["areas"] = areas_result
    
    # Handle additional requirements if present
    if "additional_requirements" in condition.get("validation", {}):
        add_reqs_result = await mem_handle_additional_requirements(
            course,
            condition.get("validation", {}).get("additional_requirements", [])
        )
        
        results["additional_requirements_met"] = add_reqs_result
        results["details"]["additional_requirements"] = add_reqs_result
    
    # Check if the course passes any filter directly defined in the condition
    if "filters" in condition:
        direct_filter_result = await check_simple_condition(course, condition)
        results["details"]["direct_filter"] = direct_filter_result
        if direct_filter_result:
            results["passes"] = True
    
    # Determine the overall pass status
    if results["areas_fulfilled"] or results["additional_requirements_met"]:
        results["passes"] = True
    
    return results

async def check_simple_condition(course: dict, condition: dict) -> bool:
    """Simple filter check for backward compatibility"""
    for filter_criteria in condition.get('filters', []):
        all_criterion_match = True
        
        for criterion_type, criterion in filter_criteria.items():
            handler = mem_criterion_handlers.get(criterion_type)
            if handler and not await handler(course, criterion):
                all_criterion_match = False
                break
                
        if all_criterion_match:
            return True
    return False

# Update bulk strategy check to handle hierarchical results
async def bulk_strategy_check_courses_condition(condition: dict, courses: List[str]) -> dict:
    """
    Enhanced function to check conditions across multiple courses
    Returns rich visualization data for frontend display
    """
    # ... existing code for fetching course data ...
    
    # Initialize detailed output structure
    result = {
        "description": condition.get("description", ""),
        "validation_requirements": condition.get("validation", {}),
        "passing_courses": [],
        "metrics": {
            "total_passing_courses": 0,
            "total_credits": 0,
            "validation_status": {},
            "overall_passed": False
        },
        "visualization_data": {
            "area_distribution": {},
            "requirement_fulfillment": {},
            "courses_by_area": {},
            "progress_percentage": 0
        }
    }
    
    # Process each course with the enhanced condition checker
    fulfilled_areas = set()
    area_credits = {}
    additional_req_fulfillment = {}
    
    for course in course_data:
        course_id = str(course["_id"])
        course_code = course.get("course_code", "Unknown").replace('\u200b', '')
        
        # Use the enhanced strategy pattern
        evaluation = await course_meets_condition_mem(course, condition)
        
        if evaluation["passes"]:
            # Add to passing courses
            result["passing_courses"].append(course_code)
            result["metrics"]["total_credits"] += course.get("credits", 0)
            
            # Track areas fulfilled
            for area in evaluation.get("areas_fulfilled", []):
                fulfilled_areas.add(area)
                
                if area not in area_credits:
                    area_credits[area] = 0
                area_credits[area] += course.get("credits", 0)
                
                if area not in result["visualization_data"]["courses_by_area"]:
                    result["visualization_data"]["courses_by_area"][area] = []
                
                result["visualization_data"]["courses_by_area"][area].append({
                    "course_code": course_code,
                    "course_id": course_id,
                    "credits": course.get("credits", 0)
                })
            
            # Track additional requirements
            for req_name, req_data in evaluation.get("additional_requirements_met", {}).items():
                if req_name not in additional_req_fulfillment:
                    additional_req_fulfillment[req_name] = {
                        "courses": [],
                        "credits": 0
                    }
                
                additional_req_fulfillment[req_name]["courses"].extend(req_data.get("courses", []))
                additional_req_fulfillment[req_name]["credits"] += req_data.get("credits", 0)
    
    # Update metrics
    result["metrics"]["total_passing_courses"] = len(result["passing_courses"])
    
    # Process area distribution for visualization
    result["visualization_data"]["area_distribution"] = {
        area: {
            "credits": credits,
            "course_count": len(result["visualization_data"]["courses_by_area"].get(area, []))
        } for area, credits in area_credits.items()
    }
    
    # Process requirement fulfillment
    for req_name, req_data in additional_req_fulfillment.items():
        result["visualization_data"]["requirement_fulfillment"][req_name] = {
            "credits": req_data["credits"],
            "course_count": len(req_data["courses"]),
            "courses": req_data["courses"]
        }
    
    # Check validation requirements
    validation_reqs = condition.get("validation", {})
    
    # Check min_areas requirement
    if "min_areas" in validation_reqs:
        min_areas = validation_reqs["min_areas"]
        areas_satisfied = len(fulfilled_areas)
        result["metrics"]["validation_status"]["min_areas"] = {
            "required": min_areas,
            "satisfied": areas_satisfied,
            "passed": areas_satisfied >= min_areas
        }
    
    # Check min_credits requirement
    if "min_credits" in validation_reqs:
        min_credits = validation_reqs["min_credits"]
        result["metrics"]["validation_status"]["min_credits"] = {
            "required": min_credits,
            "satisfied": result["metrics"]["total_credits"],
            "passed": result["metrics"]["total_credits"] >= min_credits
        }
    
    # Check min_courses requirement
    if "min_courses" in validation_reqs:
        min_courses = validation_reqs["min_courses"]
        result["metrics"]["validation_status"]["min_courses"] = {
            "required": min_courses,
            "satisfied": result["metrics"]["total_passing_courses"],
            "passed": result["metrics"]["total_passing_courses"] >= min_courses
        }
    
    # Check additional requirements
    if "additional_requirements" in validation_reqs:
        for req in validation_reqs["additional_requirements"]:
            req_name = req.get("description", "Unnamed")
            req_type = req.get("type")
            required_count = req.get("count", 0)
            
            if req_name in additional_req_fulfillment:
                satisfied = 0
                if req_type == "min_courses":
                    satisfied = len(additional_req_fulfillment[req_name]["courses"])
                elif req_type == "min_credits":
                    satisfied = additional_req_fulfillment[req_name]["credits"]
                
                result["metrics"]["validation_status"][req_name] = {
                    "required": required_count,
                    "satisfied": satisfied,
                    "passed": satisfied >= required_count
                }
            else:
                result["metrics"]["validation_status"][req_name] = {
                    "required": required_count,
                    "satisfied": 0,
                    "passed": False
                }
    
    # Calculate overall validation status
    result["metrics"]["overall_passed"] = all(
        status["passed"] for status in result["metrics"]["validation_status"].values()
    ) if result["metrics"]["validation_status"] else False
    
    # Calculate progress percentage for visualization
    if result["metrics"]["validation_status"]:
        total_requirements = len(result["metrics"]["validation_status"])
        passed_requirements = sum(
            1 for status in result["metrics"]["validation_status"].values() 
            if status["passed"]
        )
        result["visualization_data"]["progress_percentage"] = (
            (passed_requirements / total_requirements) * 100 
            if total_requirements > 0 else 0
        )
    
    return result

# ... existing code ...
```

## Frontend Visualization Component

Here's a skeleton React component to visualize the requirements:

```jsx:MajorRequirementsVisualization.jsx
import React, { useState } from 'react';
import { Progress, Card, Table, Tabs, Collapse, Badge, List, Tooltip } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, InfoCircleOutlined } from '@ant-design/icons';

const { TabPane } = Tabs;
const { Panel } = Collapse;

const MajorRequirementsVisualization = ({ requirementsData }) => {
  const [activeGroup, setActiveGroup] = useState(null);
  
  if (!requirementsData || !requirementsData.requirement_groups) {
    return <div>No requirements data available</div>;
  }
  
  const renderRequirementGroup = (group) => {
    const groupMetrics = group.metrics || {};
    const isPassed = groupMetrics.overall_passed;
    const progressPercentage = groupMetrics.visualization_data?.progress_percentage || 0;
    
    return (
      <Card 
        title={group.name}
        className={`requirement-group ${isPassed ? 'fulfilled' : 'unfulfilled'}`}
        extra={
          <Badge 
            status={isPassed ? "success" : "error"} 
            text={isPassed ? "Complete" : "Incomplete"} 
          />
        }
      >
        <Progress percent={Math.round(progressPercentage)} status={isPassed ? "success" : "active"} />
        
        <Collapse>
          {group.conditions.map((condition, index) => (
            <Panel 
              key={`${group.name}-condition-${index}`}
              header={
                <div>
                  {condition.description}
                  <Badge 
                    className="requirement-badge"
                    status={condition.metrics?.overall_passed ? "success" : "error"} 
                  />
                </div>
              }
            >
              <div className="requirement-details">
                <h4>Validation Requirements</h4>
                <Table 
                  dataSource={Object.entries(condition.metrics?.validation_status || {}).map(([key, value]) => ({
                    key,
                    requirement: key,
                    required: value.required,
                    satisfied: value.satisfied,
                    status: value.passed ? "Passed" : "Failed"
                  }))}
                  columns={[
                    { title: 'Requirement', dataIndex: 'requirement' },
                    { title: 'Required', dataIndex: 'required' },
                    { title: 'Satisfied', dataIndex: 'satisfied' },
                    { 
                      title: 'Status', 
                      dataIndex: 'status',
                      render: status => (
                        <Badge 
                          status={status === "Passed" ? "success" : "error"} 
                          text={status} 
                        />
                      )
                    }
                  ]}
                  size="small"
                />
                
                <h4>Passing Courses</h4>
                <List
                  size="small"
                  bordered
                  dataSource={condition.passing_courses || []}
                  renderItem={course => (
                    <List.Item>
                      <Tooltip title="Click for course details">
                        <div className="course-item">{course}</div>
                      </Tooltip>
                    </List.Item>
                  )}
                />
                
                {condition.visualization_data?.area_distribution && (
                  <>
                    <h4>Area Distribution</h4>
                    <Table 
                      dataSource={Object.entries(condition.visualization_data.area_distribution).map(([area, data]) => ({
                        key: area,
                        area: area,
                        credits: data.credits,
                        courses: data.course_count
                      }))}
                      columns={[
                        { title: 'Area', dataIndex: 'area' },
                        { title: 'Credits', dataIndex: 'credits' },
                        { title: 'Courses', dataIndex: 'courses' }
                      ]}
                      size="small"
                    />
                  </>
                )}
              </div>
            </Panel>
          ))}
        </Collapse>
      </Card>
    );
  };

  return (
    <div className="major-requirements-visualization">
      <h2>Electrical Engineering Major Requirements</h2>
      
      <Tabs defaultActiveKey="overview">
        <TabPane tab="Overview" key="overview">
          <div className="requirements-summary">
            {requirementsData.requirement_groups.map((group, index) => (
              <Card 
                key={`group-summary-${index}`}
                className="group-summary-card"
                onClick={() => setActiveGroup(index)}
              >
                <div className="group-title">{group.name}</div>
                <Progress 
                  percent={group.metrics?.visualization_data?.progress_percentage || 0} 
                  size="small" 
                  status={group.metrics?.overall_passed ? "success" : "active"} 
                />
                <div className="group-credits">
                  {group.metrics?.total_credits || 0}/{group.credits_required} credits
                </div>
              </Card>
            ))}
          </div>
        </TabPane>
        
        <TabPane tab="Detailed View" key="detailed">
          {requirementsData.requirement_groups.map((group, index) => (
            <div key={`group-detail-${index}`} className="group-detail-container">
              {renderRequirementGroup(group)}
            </div>
          ))}
        </TabPane>
        
        <TabPane tab="Course Allocation" key="allocation">
          <p>This view shows how your courses are allocated to fulfill requirements.</p>
          {/* Course allocation visualization */}
        </TabPane>
      </Tabs>
    </div>
  );
};

export default MajorRequirementsVisualization;
```

## Recommendations for Implementation

1. **Incremental Implementation**: 
   - Start with core requirements and add complexity gradually
   - Implement the basic structure first before adding special cases

2. **Testing Strategy**:
   - Create test fixtures for different requirement scenarios
   - Build unit tests for each handler function
   - Create integration tests with sample student roadmaps

3. **Performance Considerations**:
   - Use MongoDB aggregation for initial filtering
   - Implement caching for frequently accessed validations
   - Consider background pre-calculation of requirement status

4. **Frontend Integration**:
   - Use progressive disclosure to manage complexity
   - Provide drill-down capability from overview to details
   - Include interactive elements to explore "what-if" scenarios

5. **Data Management**:
   - Create admin tools to maintain requirements as they change over time
   - Version requirements by catalog year
   - Include effective dates for requirements

This system provides a comprehensive and flexible approach to validating complex major requirements while generating rich visualization data for the frontend. 