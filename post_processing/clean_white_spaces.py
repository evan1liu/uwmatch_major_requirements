import asyncio
from utils.get_mongodb_collection import get_mongodb_collection

COURSE_COLLECTION = get_mongodb_collection("courses")

def clean_unicode_chars(value: any) -> any:
    """Clean unicode characters like \u200b from strings or lists of strings."""
    if isinstance(value, str):
        return value.replace('\u200b', '')
    elif isinstance(value, list):
        return [clean_unicode_chars(item) for item in value]
    elif isinstance(value, dict):
        return {k: clean_unicode_chars(v) for k, v in value.items()}
    return value

async def clean_database():
    cursor = COURSE_COLLECTION.find({})
    async for doc in cursor:
        cleaned_doc = clean_unicode_chars(doc)
        if cleaned_doc != doc:
            # Exclude _id from the update
            cleaned_doc.pop('_id', None)
            await COURSE_COLLECTION.update_one(
                {'_id': doc['_id']},
                {'$set': cleaned_doc}
            )

# Run with:
asyncio.run(clean_database())
