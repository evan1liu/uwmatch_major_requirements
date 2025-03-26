import asyncio
from crawl4ai import AsyncWebCrawler
from majors_links import get_table_links

async def count_characters_from_first_link():
    """
    Uses Crawl4AI's AsyncWebCrawler to fetch the first link (with "#requirementstext" appended)
    from get_table_links(), then counts and returns the total number of characters in the
    scraped content (using cleaned_html if available, otherwise markdown).
    """
    links = get_table_links()
    if not links:
        print("No links found.")
        return 0

    # Append the fragment to the first link
    link1 = links[0] + "#requirementstext"

    async with AsyncWebCrawler() as crawler:
        # Perform the crawl; this returns a CrawlResult object
        result = await crawler.arun(url=link1)
        # Prefer cleaned_html; fallback to markdown if cleaned_html is empty or not available.
        content = result.cleaned_html if getattr(result, 'cleaned_html', None) else result.markdown
        return len(content)

if __name__ == "__main__":
    total_chars = asyncio.run(count_characters_from_first_link())
    print("Total number of characters scraped:", total_chars)
