import asyncio
from utils.get_mongodb_collection import get_mongodb_collection

COURSE_COLLECTION = get_mongodb_collection("courses")

def clean_unicode_chars(value: any) -> any:
    """Clean unicode characters like \u200b from strings or lists of strings."""
    if isinstance(value, str):
        return value.replace('\u200b', '')
    elif isinstance(value, list):
        return [clean_unicode_chars(item) for item in value]
    return value

async def clean_database():
    cursor = COURSE_COLLECTION.find({})
    async for doc in cursor:
        updates = {}
        for key in ['departments', 'course_code', 'course_codes']:
            if key in doc:
                cleaned_value = clean_unicode_chars(doc[key])
                if cleaned_value != doc[key]:
                    updates[key] = cleaned_value
        
        if updates:
            await COURSE_COLLECTION.update_one(
                {'_id': doc['_id']},
                {'$set': updates}
            )

# Run with:
asyncio.run(clean_database())
