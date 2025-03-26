import asyncio
from crawl4ai import AsyncWebCrawler
import re

async def scrape_requirements(url):
    """
    Scrapes a requirements page from UW-Madison's Guide and extracts only the section
    between "University General Education Requirements" and the end of "University Degree Requirements".
    
    Args:
        url (str): The full URL of the requirements page to scrape
        
    Returns:
        str: The extracted requirements section in markdown format
    """
    async with AsyncWebCrawler() as crawler:
        # Perform the crawl
        result = await crawler.arun(url=url)
        
        # Get the content in markdown format
        content = result.markdown
        
        # Find the sections we want in the markdown content
        start_marker = "## University General Education Requirements"
        end_marker = "## University Degree Requirements"
        
        # Find the positions of our markers
        start_pos = content.find(start_marker)
        if start_pos == -1:
            return "Start section not found."
        
        # Find the next section after University Degree Requirements
        end_section_pos = content.find(end_marker)
        if end_section_pos == -1:
            return "End section not found."
            
        # Find the next heading after University Degree Requirements
        next_heading_pos = content.find("##", end_section_pos + len(end_marker))
        if next_heading_pos == -1:
            # If no next heading, take all remaining content
            extracted_content = content[start_pos:]
        else:
            extracted_content = content[start_pos:next_heading_pos]
        
        return extracted_content.strip()

def remove_course_links(content):
    """
    Removes all course links from the scraped content while preserving the course names.
    
    Args:
        content (str): The scraped content containing markdown course links
        
    Returns:
        str: Content with all course links removed but course names preserved
    """
    # Pattern matches markdown links: [COURSE NAME](/search/?P=COURSE%20NAME "COURSE NAME")
    # and similar variations
    clean_content = re.sub(r'\[([\w\s/​]+)\]\([^)]+\s"[^"]+"\)', r'\1', content)
    
    return clean_content

def export_to_markdown(content, filename="requirements_for_llm.md"):
    """
    Exports the scraped and cleaned content to a markdown file.
    
    Args:
        content (str): The content to export
        filename (str, optional): The name of the output file. Defaults to "requirements_for_llm.md".
        
    Returns:
        str: Path to the saved file
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filename

if __name__ == "__main__":
    # Example usage with EE requirements page
    example_url = "https://guide.wisc.edu/undergraduate/engineering/electrical-computer-engineering/electrical-engineering-bs/#requirementstext"
    content = asyncio.run(scrape_requirements(example_url))
    
    # Remove course links
    cleaned_content = remove_course_links(content)
    
    # Export to markdown file
    output_file = export_to_markdown(cleaned_content)
    
    print(f"Content extracted, cleaned, and saved to {output_file} ({len(cleaned_content)} characters)")
