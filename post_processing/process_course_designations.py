from motor.motor_asyncio import AsyncIOMotorClient
from config import Settings
import asyncio

async def format_course_designations(course_collection):
    """
    Process all course documents and add a 'formatted_designations' field
    with the structured representation of course_designation data
    """
    # Count documents to process
    total_docs = await course_collection.count_documents({})
    print(f"Processing {total_docs} course documents...")
    
    # Counter for processed documents
    processed = 0
    
    # Process each document
    async for course in course_collection.find({}):
        if 'course_designation' in course and course['course_designation']:
            # Format the designations
            formatted = format_designation_text(course['course_designation'])
            
            # Update the document with the new field
            await course_collection.update_one(
                {'_id': course['_id']},
                {'$set': {'formatted_designations': formatted}}
            )
            
            # Update counter
            processed += 1
            if processed % 100 == 0:
                print(f"Processed {processed}/{total_docs} documents...")
    
    print(f"Completed. Added formatted_designations to {processed} documents.")


def format_designation_text(designation_text):
    """
    Convert course_designation text to a structured array format
    """
    if not designation_text:
        return []
        
    # Split the text by newlines and strip whitespace
    designations = [d.strip() for d in designation_text.split('\n') if d.strip()]
    
    # Initialize result array
    result = []
    
    # Process each designation
    for designation in designations:
        # Handle Breadth designations
        if designation.startswith('Breadth - '):
            # Special handling for "Either X or Y" breadth designations
            if 'Either Humanities or Social Science' in designation:
                result.append('Breadth - Humanities')
                result.append('Breadth - Social Science')
            elif 'Either Humanities or Natural Science' in designation:
                result.append('Breadth - Humanities')
                result.append('Breadth - Natural Science')
            elif 'Either Social Science or Natural Science' in designation:
                result.append('Breadth - Social Science')
                result.append('Breadth - Natural Science')
            elif 'Either Biological Science or Social Science' in designation:
                result.append('Breadth - Biological Science')
                result.append('Breadth - Social Science')
            # Clean up breadth designations with explanatory text
            elif 'Biological Sci.' in designation:
                result.append('Breadth - Biological Science')
            elif 'Physical Sci.' in designation:
                result.append('Breadth - Physical Science')
            elif 'Literature.' in designation:
                result.append('Breadth - Literature')
            else:
                # Keep other breadth designations as is
                result.append(designation)
        else:
            # For all other designations, keep as is
            result.append(designation)
    
    # Remove any duplicates
    result = list(set(result))
    
    return result


async def main():
    # Connect to the database
    client = AsyncIOMotorClient(Settings.MONGODB_URI)
    db = client.uwmatch
    course_collection = db.courses
    
    # Format course designations
    await format_course_designations(course_collection)
    
    # Close the connection
    client.close()


if __name__ == "__main__":
    asyncio.run(main()) 