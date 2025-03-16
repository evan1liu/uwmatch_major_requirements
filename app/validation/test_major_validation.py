import pytest
from utils.parse_course_code import parse_course_code
from app.validation.EEMajorValidation import RecursiveMajorValidator

# Test fixtures and helper functions
@pytest.fixture
def basic_requirements():
    """A simple requirements structure for testing basic functionality"""
    return {
        "id": "test_major",
        "name": "Test Major Requirements",
        "validation": {"min_credits": 10},
        "requirements": [
            {
                "id": "basic_math",
                "name": "Basic Math",
                "validation": {"min_courses": 1},
                "filters": [{"list": ["MATH 101"]}]
            },
            {
                "id": "basic_science",
                "name": "Basic Science",
                "validation": {"min_credits": 3},
                "filters": [{"category": "Natural Science"}]
            }
        ]
    }

@pytest.fixture
def complex_requirements():
    """A more complex requirements structure with alternatives and nested requirements"""
    return {
        "id": "complex_major",
        "name": "Complex Major Requirements",
        "validation": {"min_credits": 15},
        "requirements": [
            {
                "id": "advanced_math",
                "name": "Advanced Math",
                "validation_type": "alternative",
                "alternatives": [
                    {
                        "validation": {"min_courses": 1},
                        "filters": [{"list": ["MATH/STAT 431"]}]
                    },
                    {
                        "validation": {"min_courses": 2},
                        "filters": [{"list": ["MATH 375", "MATH 376"]}]
                    }
                ]
            },
            {
                "id": "science_group",
                "name": "Science Group",
                "validation_type": "all",
                "requirements": [
                    {
                        "id": "lab_science",
                        "name": "Lab Science",
                        "validation": {"min_courses": 1},
                        "filters": [{"category": "Natural Science", "has_lab": True}]
                    },
                    {
                        "id": "programming",
                        "name": "Programming",
                        "validation": {"min_courses": 1},
                        "filters": [{"list": ["COMP SCI 300"]}]
                    }
                ]
            }
        ]
    }

# Actual test functions
def test_basic_course_matching():
    """Test that simple course lists are matched correctly"""
    req = basic_requirements()
    
    # Student who passed the requirement
    passing_courses = [
        {"course_code": "MATH 101", "credits": 4, "departments": ["MATH"], "course_number": "101"},
        {"course_code": "BIO 101", "credits": 3, "formatted_designations": ["Natural Science"], "departments": ["BIO"], "course_number": "101"}
    ]
    
    validator = RecursiveMajorValidator(req, passing_courses)
    result = validator.validate_major()
    assert result["satisfied"] == True
    
    # Student who failed the requirement
    failing_courses = [
        {"course_code": "MATH 102", "credits": 4, "departments": ["MATH"], "course_number": "102"},
        {"course_code": "BIO 101", "credits": 3, "formatted_designations": ["Natural Science"], "departments": ["BIO"], "course_number": "101"}
    ]
    
    validator = RecursiveMajorValidator(req, failing_courses)
    result = validator.validate_major()
    assert result["satisfied"] == False

def test_cross_listed_course_matching():
    """Test that cross-listed courses are matched correctly regardless of department order"""
    # Simple requirement for cross-listed course
    req = {
        "id": "cross_listed_req",
        "name": "Cross-Listed Requirement",
        "validation": {"min_courses": 1},
        "filters": [{"list": ["MATH/STAT 431"]}]
    }
    
    # Case 1: Exact match in departments
    courses1 = [
        {"course_code": "MATH/STAT 431", "credits": 3, "departments": ["MATH", "STAT"], "course_number": "431"}
    ]
    validator1 = RecursiveMajorValidator(req, courses1)
    result1 = validator1.validate_major()
    assert result1["satisfied"] == True
    
    # Case 2: Reverse order in departments
    courses2 = [
        {"course_code": "STAT/MATH 431", "credits": 3, "departments": ["STAT", "MATH"], "course_number": "431"}
    ]
    validator2 = RecursiveMajorValidator(req, courses2)
    result2 = validator2.validate_major()
    assert result2["satisfied"] == True
    
    # Case 3: Different course number (should fail)
    courses3 = [
        {"course_code": "MATH/STAT 432", "credits": 3, "departments": ["MATH", "STAT"], "course_number": "432"}
    ]
    validator3 = RecursiveMajorValidator(req, courses3)
    result3 = validator3.validate_major()
    assert result3["satisfied"] == False
    
    # Case 4: Missing department (should fail)
    courses4 = [
        {"course_code": "MATH 431", "credits": 3, "departments": ["MATH"], "course_number": "431"}
    ]
    validator4 = RecursiveMajorValidator(req, courses4)
    result4 = validator4.validate_major()
    assert result4["satisfied"] == False

def test_alternative_path_validation():
    """Test that alternative paths are correctly validated"""
    req = complex_requirements()
    
    # Case 1: First alternative satisfied
    courses1 = [
        {"course_code": "STAT/MATH 431", "credits": 3, "departments": ["STAT", "MATH"], "course_number": "431"},
        {"course_code": "BIO 101", "credits": 4, "formatted_designations": ["Natural Science"], "has_lab": True, "departments": ["BIO"], "course_number": "101"},
        {"course_code": "COMP SCI 300", "credits": 3, "departments": ["COMP SCI"], "course_number": "300"}
    ]
    validator1 = RecursiveMajorValidator(req, courses1)
    result1 = validator1.validate_major()
    assert result1["satisfied"] == True
    
    # Case 2: Second alternative satisfied
    courses2 = [
        {"course_code": "MATH 375", "credits": 3, "departments": ["MATH"], "course_number": "375"},
        {"course_code": "MATH 376", "credits": 3, "departments": ["MATH"], "course_number": "376"},
        {"course_code": "BIO 101", "credits": 4, "formatted_designations": ["Natural Science"], "has_lab": True, "departments": ["BIO"], "course_number": "101"},
        {"course_code": "COMP SCI 300", "credits": 3, "departments": ["COMP SCI"], "course_number": "300"}
    ]
    validator2 = RecursiveMajorValidator(req, courses2)
    result2 = validator2.validate_major()
    assert result2["satisfied"] == True
    
    # Case 3: No alternative satisfied
    courses3 = [
        {"course_code": "MATH 374", "credits": 3, "departments": ["MATH"], "course_number": "374"},
        {"course_code": "BIO 101", "credits": 4, "formatted_designations": ["Natural Science"], "has_lab": True, "departments": ["BIO"], "course_number": "101"},
        {"course_code": "COMP SCI 300", "credits": 3, "departments": ["COMP SCI"], "course_number": "300"}
    ]
    validator3 = RecursiveMajorValidator(req, courses3)
    result3 = validator3.validate_major()
    assert result3["satisfied"] == False

def test_credit_counting():
    """Test that credit counts are correctly calculated"""
    req = {
        "id": "credit_req",
        "name": "Credit Requirements",
        "validation": {"min_credits": 10},
        "filters": [{"category": "Natural Science"}]
    }
    
    # Case 1: Enough credits
    courses1 = [
        {"course_code": "BIO 101", "credits": 4, "formatted_designations": ["Natural Science"], "departments": ["BIO"], "course_number": "101"},
        {"course_code": "CHEM 103", "credits": 4, "formatted_designations": ["Natural Science"], "departments": ["CHEM"], "course_number": "103"},
        {"course_code": "PHYSICS 201", "credits": 5, "formatted_designations": ["Natural Science"], "departments": ["PHYSICS"], "course_number": "201"}
    ]
    validator1 = RecursiveMajorValidator(req, courses1)
    result1 = validator1.validate_major()
    assert result1["satisfied"] == True
    assert result1["details"]["validation_metrics"]["total_credits"] >= 10
    
    # Case 2: Not enough credits
    courses2 = [
        {"course_code": "BIO 101", "credits": 4, "formatted_designations": ["Natural Science"], "departments": ["BIO"], "course_number": "101"},
        {"course_code": "CHEM 103", "credits": 4, "formatted_designations": ["Natural Science"], "departments": ["CHEM"], "course_number": "103"}
    ]
    validator2 = RecursiveMajorValidator(req, courses2)
    result2 = validator2.validate_major()
    assert result2["satisfied"] == False
    assert result2["details"]["validation_metrics"]["total_credits"] < 10

def test_complex_nesting():
    """Test deeply nested requirements structures"""
    # Create a deeply nested requirements structure
    nested_req = {
        "id": "nested_major",
        "name": "Nested Major Requirements",
        "validation_type": "all",
        "requirements": [
            {
                "id": "level1",
                "name": "Level 1",
                "validation_type": "all",
                "requirements": [
                    {
                        "id": "level2a",
                        "name": "Level 2A",
                        "validation_type": "alternative",
                        "alternatives": [
                            {
                                "validation": {"min_courses": 1},
                                "filters": [{"list": ["MATH 221"]}]
                            },
                            {
                                "validation": {"min_courses": 1},
                                "filters": [{"list": ["MATH 217"]}]
                            }
                        ]
                    },
                    {
                        "id": "level2b",
                        "name": "Level 2B",
                        "validation": {"min_courses": 1},
                        "filters": [{"list": ["COMP SCI 300"]}]
                    }
                ]
            }
        ]
    }
    
    # Complete case - should pass
    complete_courses = [
        {"course_code": "MATH 221", "credits": 5, "departments": ["MATH"], "course_number": "221"},
        {"course_code": "COMP SCI 300", "credits": 3, "departments": ["COMP SCI"], "course_number": "300"}
    ]
    validator1 = RecursiveMajorValidator(nested_req, complete_courses)
    result1 = validator1.validate_major()
    assert result1["satisfied"] == True
    
    # Alternative path - should also pass
    alt_courses = [
        {"course_code": "MATH 217", "credits": 5, "departments": ["MATH"], "course_number": "217"},
        {"course_code": "COMP SCI 300", "credits": 3, "departments": ["COMP SCI"], "course_number": "300"}
    ]
    validator2 = RecursiveMajorValidator(nested_req, alt_courses)
    result2 = validator2.validate_major()
    assert result2["satisfied"] == True
    
    # Missing Level 2B - should fail
    incomplete_courses = [
        {"course_code": "MATH 221", "credits": 5, "departments": ["MATH"], "course_number": "221"}
    ]
    validator3 = RecursiveMajorValidator(nested_req, incomplete_courses)
    result3 = validator3.validate_major()
    assert result3["satisfied"] == False

def test_edge_cases():
    """Test edge cases like empty course lists, empty requirements, etc."""
    # Empty course list
    req = basic_requirements()
    validator = RecursiveMajorValidator(req, [])
    result = validator.validate_major()
    assert result["satisfied"] == False
    
    # Empty requirements
    empty_req = {"id": "empty", "name": "Empty Requirements", "validation": {}, "requirements": []}
    validator = RecursiveMajorValidator(empty_req, [])
    result = validator.validate_major()
    # The behavior here depends on your implementation - adjust as needed
    
    # Requirement with no filters
    no_filter_req = {
        "id": "no_filter",
        "name": "No Filter Requirement",
        "validation": {"min_courses": 1},
        "filters": []
    }
    courses = [
        {"course_code": "MATH 221", "credits": 5, "departments": ["MATH"], "course_number": "221"}
    ]
    validator = RecursiveMajorValidator(no_filter_req, courses)
    result = validator.validate_major()
    # Again, behavior depends on implementation