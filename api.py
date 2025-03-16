"""
API endpoints for major requirements validation.

This module provides FastAPI endpoints to validate student courses against major requirements
and return detailed results for frontend visualization.
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

from major_validation import MajorRequirementsValidator

# Database connection
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "uwmatch"
COURSES_COLLECTION = "courses"

# MongoDB connection context manager
@asynccontextmanager
async def get_mongodb():
    client = AsyncIOMotorClient(MONGODB_URL)
    try:
        yield client[DB_NAME]
    finally:
        client.close()

class Course(BaseModel):
    """Model for a single course"""
    course_code: str
    credits: float
    grade: Optional[str] = None
    attributes: Optional[List[str]] = []
    breadth: Optional[str] = None
    has_lab: Optional[bool] = False
    category: Optional[str] = None

class StudentCoursesRequest(BaseModel):
    """Request model for validating student courses"""
    student_id: Optional[str] = None
    major_code: str
    course_ids: List[str]

# FastAPI app with database dependency
app = FastAPI(title="UW Major Requirements Validation API")

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "UW Major Requirements Validation API"}

@app.get("/majors")
async def get_available_majors():
    """Get list of available majors for validation"""
    # Scan for all JSON files in the directory that might be major requirements
    major_files = []
    for file in os.listdir():
        if file.endswith("_major_requirements.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    major_files.append({
                        "code": data.get("major_code", file.replace("_major_requirements.json", "")),
                        "name": data.get("major_name", "Unknown Major"),
                        "file": file
                    })
            except (json.JSONDecodeError, FileNotFoundError):
                continue
    
    return {"majors": major_files}

async def fetch_courses_from_mongodb(db, course_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch course data from MongoDB based on course IDs
    
    Args:
        db: MongoDB database connection
        course_ids: List of course IDs to fetch
        
    Returns:
        List of course dictionaries with all necessary information
    """
    # Fetch courses
    cursor = db[COURSES_COLLECTION].find({"course_code": {"$in": course_ids}})
    courses = await cursor.to_list(length=None)
    
    # Transform to the format needed by the validator
    formatted_courses = []
    for course in courses:
        formatted_course = {
            "course_code": course.get("course_code", ""),
            "credits": course.get("credits", 0),
        }
        
        # Add optional fields if they exist
        if "attributes" in course:
            formatted_course["attributes"] = course["attributes"]
        if "breadth" in course:
            formatted_course["breadth"] = course["breadth"]
        if "has_lab" in course:
            formatted_course["has_lab"] = course["has_lab"]
        if "category" in course:
            formatted_course["category"] = course["category"]
        
        formatted_courses.append(formatted_course)
    
    return formatted_courses

@app.post("/validate")
async def validate_student_courses(request: StudentCoursesRequest):
    """
    Validate a student's courses against major requirements
    
    This endpoint accepts a list of course IDs and major code,
    fetches course data from MongoDB, and returns detailed validation results.
    """
    # Map of major codes to requirement files
    major_file_mapping = {
        "EE": "ee_major_requirements.json",
        # Add other majors as needed
    }
    
    if request.major_code not in major_file_mapping:
        raise HTTPException(status_code=404, detail=f"Major code '{request.major_code}' not found")
    
    try:
        # Get MongoDB connection
        async with get_mongodb() as db:
            # Fetch course data from MongoDB
            student_courses = await fetch_courses_from_mongodb(db, request.course_ids)
            
            if not student_courses:
                raise HTTPException(status_code=404, detail="No courses found with the provided IDs")
            
            # Initialize validator with requirements file
            validator = MajorRequirementsValidator(major_file_mapping[request.major_code])
            
            # Validate courses against major requirements
            result = validator.validate_student_courses(student_courses)
            
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.get("/requirements/{major_code}")
def get_major_requirements(major_code: str):
    """
    Get the raw requirements for a specific major
    
    This endpoint returns the full JSON schema for a major's requirements.
    """
    # Map of major codes to requirement files
    major_file_mapping = {
        "EE": "ee_major_requirements.json",
        # Add other majors as needed
    }
    
    if major_code not in major_file_mapping:
        raise HTTPException(status_code=404, detail=f"Major code '{major_code}' not found")
    
    try:
        with open(major_file_mapping[major_code], "r") as f:
            requirements = json.load(f)
        return requirements
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Requirements file for major '{major_code}' not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in requirements file for major '{major_code}'")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
