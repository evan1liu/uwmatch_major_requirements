import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from openai import AsyncOpenAI
import logging
import time
from typing import List, Dict, Any, Tuple
from tqdm.asyncio import tqdm
from bson.objectid import ObjectId
import pymongo

# Disable OpenAI's HTTP request logging so that it doesn't overwhelm the terminal
# we only want the terminal to return important messages such as when a course's 'has_lab' is True
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


# Load environment variables first
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# we're connecting to our 'courses' collection here'
client = AsyncIOMotorClient(MONGODB_URI)
db = client["uwmatch"]
courses_collection = db["courses"]
# we're defining the channel with openai client here with out openai key in the .env file
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# we defined the "Semaphore" as 50
# this it the maximum number of tasks avaialable for API calls
API_SEMAPHORE = asyncio.Semaphore(50) 

# we feed in a bunch of string attributes of a course
# and get a prompt that we can feed into each API call to chatgpt 4o-mini
def get_prompt_for_has_lab (course_code, title, description, learning_outcomes):
    prompt = f"""
            Does this course have a laboratory component? Reply with ONLY "true" or "false".

            Course Code: {course_code}
            Title: {title}
            Description: {description}
            Learning Outcomes: {learning_outcomes}

            """
    return prompt

# we're feeding the course as a dictionary with course attributes
# we're returning a tuple with some the important attributes like course_id, course_code, title
# and of course we're returning whether 'has_lab' is True or False
async def check_has_lab(course: Dict[str, Any]) -> Tuple[Any, str, str, bool]:
    # """Check if a course has a lab component"""
    
    course_id = course["_id"]  # Keep as ObjectId, don't convert to string
    course_code = course.get("course_code", "None")
    title = course.get("clean_title", "None").lower()
    description = course.get("description", "None").lower()
    learning_outcomes = course.get("Learning Outcomes", "None").lower()
    # ==================================================================
    # REMOVED CODE FOR PASSING THROUGH A CHATGPT API CALL -> UNNECESSARY
    # ==================================================================
    # prompt = get_prompt_for_has_lab(course_code=course_code, title=title, description=description, learning_outcomes=learning_outcomes)
    
    # # API_SEMAPHORE is a way of rate limiting
    # # we're tracking how many tasks are currently holding the semphore
    # # if less than 50 tasks are holding the semaphore, then the task passes through immediately
    # # if it doesn't, then it waits until a task ia released from the semaphore
    # # only after this "async with" block returns a result, then the task is released from the semaphore
    # async with API_SEMAPHORE:
    #     try:
    #         await asyncio.sleep(1.0)
            
    #         response = await openai_client.chat.completions.create(
    #             model="gpt-4o-mini",
    #             messages=[
    #                 {"role": "system", "content": "You analyze if courses have lab components. Answer only with 'true' or 'false'."},
    #                 {"role": "user", "content": prompt}
    #             ],
    #             # since we're only trying to get a boolean value, we limit the max_tokens to 10
    #             max_tokens=10,
    #             # no need for creativity
    #             temperature=0
    #         )
            
    #         answer = response.choices[0].message.content.strip().lower()
    #         has_lab = 'true' in answer
    has_lab = False
    if 'lab' in title or 'lab' in description or 'lab' in learning_outcomes:
        has_lab = True
        print(course_code, title, sep=': ')
            
            # we're returning an immutable tuple that contains the attributes of a course and wheter 'has_lab' is True
    return (course_id, course_code, title, has_lab)
            

async def process_courses_batch(courses: List[Dict]) -> List[Tuple[Any, str, str, bool]]:
    """Process multiple courses concurrently"""
    
    tasks = []
    for course in courses:
        # !!! HERE, 'check_has_lab' does not return any results!!!
        # since when we call an async function without using 'await', we only create a coroutine object
        # a coroutine object tells python how to execute the function
        # we collect these coroutine objects together (in a batch of 50), and then we execute them all at once
        task = check_has_lab(course)
        tasks.append(task)
    
    # we gather all the tasks together and use asyncio to execute all tasks at once
    # 'results' stores a list of tuples outputed from the function 'check_has_lab'
    try:
        results = await asyncio.gather(*tasks)
        return results
    except Exception:
        # Return ObjectId instead of string
        return [(course["_id"], course.get("course_code", ""), 
                 course.get("clean_title", ""), False) for course in courses]


async def update_database_batch(results: List[Tuple[Any, str, str, bool]]):
    """Update database in bulk with results"""
    
    bulk_operations = []
    
    for course_id, course_code, title, has_lab in results:
        # Only log courses with labs - just the title
        if has_lab:
            print(course_code, title, sep=': ')
            
        # here, it's another different parallel processing
        # we're writing to multiple documents at once
        # same as the previous parallel processing where we call multiple api calls at once
        # here, we're gathering the operations first without executing that we'll execute all at once later
        bulk_operations.append(
            {
                "filter": {"_id": course_id},
                "update": {"$set": {"has_lab": has_lab}}
            }
        )
    
    if bulk_operations:
        try:
            # here, 'course_doc["update"]' contains the actual operation that we're using to update a doc
            # here, course_doc["filter"] filters out which document(s) we're modifying
            # in this case, it's just one document because we're using the id as a filter, and id is non-repeatable
            # here, pymongo is not specific to any syncrhonous nor asyncrhonous code, they're just descriptions for operations
            operations = [pymongo.UpdateOne(course_doc["filter"], course_doc["update"]) for course_doc in bulk_operations]
            # up to the line above, we still haven't sent anything to the mongodb server yet
            # the following line, we'll be writing into the course_collection in our mongodb's database 'uwmatch'
            # here, the order doesn't really matter, because in bulk operations,
            # we already tied each course_id with its exact operation that contains the information about the boolean value of 'has_lab'
            await courses_collection.bulk_write(operations, ordered=False)
        except Exception as e:
            print(f"Error in bulk write: {e}")

async def main():
    try:
        # Only get courses that haven't been processed yet
        query = {"has_lab": {"$exists": False}}
        # the function 'count_documents' return the number of documents that fulfills a given filter
        total_courses = await courses_collection.count_documents(query)
        
        if total_courses == 0:
            return
        
        # Smaller batch size
        batch_size = 1000
        # cursor doesn't return any document yet, it's just point to a document
        cursor = courses_collection.find(query)
        
        with tqdm(total=total_courses, desc="Processing") as pbar:
            current_batch = []
            
            # here, course is the actual document dictionary when we iterate through the cursor
            async for course in cursor:
               # we append the document dictionary to the current batch, to get a list of course dictionaries
                current_batch.append(course)
                # when the length of the current_batch is bigger or equal to the batch size we defined,
                # then we use the functions we defined earlier to get results from api calls and then write results into our collection
                if len(current_batch) >= batch_size:
                    # here, results is a list of immutable tuples: (course_id, course_code, title, has_lab)
                    results = await process_courses_batch(current_batch)
                    # we feed the list of immutable tuples into this function 'update_database_batch'
                    # to update docs in our collection
                    await update_database_batch(results)
                    # we update the progress bar, adding the number of current_batch
                    pbar.update(len(current_batch))
                    # we reset the current_batch back to zero and start with the next batch
                    current_batch = []
            
            # after looping through all courses, the last batch remains
            # the last batch hasn't been executed yet because its length is less than 50
            # therefore, we have to update the last batch here
            if current_batch:
                results = await process_courses_batch(current_batch)
                await update_database_batch(results)
                pbar.update(len(current_batch))
    
    except Exception:
        pass  # Silent error handling
    
    finally:
        client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Silent handling of keyboard interrupt
    except Exception:
        pass  # Silent handling of exceptions
