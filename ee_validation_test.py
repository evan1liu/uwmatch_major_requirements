"""
Test script for validating EE major requirements using existing validation infrastructure.

This script converts the EE JSON requirements into conditions compatible with the
existing validation code and tests them against the sample course IDs.
"""

import json
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any
import os

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Import the validation module with all dependencies
from tests.optimized_validation_requirements import bulk_strategy_check_courses_condition
from tests.example_list_of_courses import test_courses

# Define a simplified version of concurrent_main since we might have import issues
async def concurrent_main(courses: List[str], conditions: List[Dict]) -> List[Dict]:
    """Process multiple conditions concurrently"""
    tasks = []
    for condition in conditions:
        tasks.append(bulk_strategy_check_courses_condition(condition, courses))
    
    # Run all tasks concurrently and collect results
    return await asyncio.gather(*tasks)

async def convert_json_to_conditions(json_file_path: str) -> List[Dict[str, Any]]:
    """
    Convert the EE major requirements JSON into a list of conditions
    compatible with the existing validation code.
    
    Args:
        json_file_path: Path to the EE major requirements JSON file
        
    Returns:
        List of condition dictionaries
    """
    with open(json_file_path, 'r') as f:
        ee_requirements = json.load(f)
    
    conditions = []
    
    # Process each requirement group in the JSON
    for group in ee_requirements.get("requirement_groups", []):
        group_name = group.get("name", "Unnamed Group")
        
        # Process each condition in the group
        for condition in group.get("conditions", []):
            # Handle standard conditions
            condition_dict = {
                "description": f"{group_name}: {condition.get('description', 'Unnamed Condition')}",
                "filters": condition.get("filters", []),
                "validation": condition.get("validation", {})
            }
            conditions.append(condition_dict)
            
            # Handle areas if present (advanced electives, etc.)
            if "areas" in condition:
                for area in condition.get("areas", []):
                    area_dict = {
                        "description": f"{group_name}: {condition.get('description', 'Unnamed Condition')} - {area.get('name', 'Unnamed Area')}",
                        "filters": area.get("filters", []),
                        "validation": area.get("validation", {})
                    }
                    conditions.append(area_dict)
    
    return conditions

async def main():
    """Main test function"""
    print("\n=== VALIDATING EE MAJOR REQUIREMENTS ===\n")
    print(f"Using test courses: {test_courses}")
    
    # Convert JSON requirements to conditions
    conditions = await convert_json_to_conditions("ee_major_requirements.json")
    print(f"Converted {len(conditions)} requirements conditions from JSON")
    
    # Test first few conditions only to verify functionality
    test_conditions = conditions[:3]
    print(f"\nTesting with first {len(test_conditions)} conditions to verify functionality:")
    for i, condition in enumerate(test_conditions):
        print(f"{i+1}. {condition['description']}")
    
    try:
        # Validate test conditions against the test courses
        print("\nValidating test courses against conditions...\n")
        results = await concurrent_main(test_courses, test_conditions)
        
        # Print results in a readable format
        for i, result in enumerate(results):
            passed = result.get("metrics", {}).get("overall_passed", False)
            status_icon = "✅" if passed else "❌"
            description = result.get("description", "Unknown")
            
            # Extract validation requirements and results
            validation = result.get("validation_requirements", {})
            metrics = result.get("metrics", {}).get("validation_status", {})
            
            validation_details = []
            for key, val in metrics.items():
                if key == "min_courses":
                    validation_details.append(f"Courses: {val.get('satisfied', 0)}/{val.get('required', 0)}")
                elif key == "min_credits":
                    validation_details.append(f"Credits: {val.get('satisfied', 0)}/{val.get('required', 0)}")
            
            # Count passing courses
            passing_courses = result.get("passing_courses", [])
            
            # Print the result line
            print(f"{status_icon} {description}")
            if validation_details:
                print(f"   {', '.join(validation_details)}")
            
            if passing_courses:
                print(f"   Passing courses ({len(passing_courses)}):")
                for course in passing_courses[:5]:  # Show only the first 5 to keep output manageable
                    print(f"     - {course}")
                if len(passing_courses) > 5:
                    print(f"     - ... and {len(passing_courses) - 5} more")
            print()
        
        # If the test is successful, run all conditions
        print("\nTest successful! Running validation for all conditions...\n")
        all_results = await concurrent_main(test_courses, conditions)
        
        # Calculate overall statistics
        total_conditions = len(all_results)
        passed_conditions = sum(1 for r in all_results if r.get("metrics", {}).get("overall_passed", False))
        
        print(f"\nOverall Progress: {passed_conditions}/{total_conditions} requirements met ({passed_conditions/total_conditions*100:.1f}%)")
        
        # Save detailed results to file
        with open("ee_validation_results.json", "w") as f:
            json.dump(all_results, f, indent=2)
        
        print("\nDetailed results saved to ee_validation_results.json")
    
    except Exception as e:
        print(f"Error during validation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
