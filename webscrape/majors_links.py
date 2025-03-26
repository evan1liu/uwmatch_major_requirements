from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
import json

def get_table_links(url="https://www.wisc.edu/academics/majors/", 
                    table_id="programs-results-table", wait_time=5):
    """
    Fetches the given URL using Selenium (to render JavaScript content),
    parses the page with BeautifulSoup, and returns a list of link URLs 
    from the table with the specified ID.

    Args:
        url (str): The URL to scrape.
        table_id (str): The ID of the table to search for.
        wait_time (int): Number of seconds to wait for the page to load.
    
    Returns:
        list: A list of URLs (strings) found within the specified table.
    """
    # Set up Selenium with headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without a UI
    driver = webdriver.Chrome(options=chrome_options)
    
    # Open the URL and wait for dynamic content to load
    driver.get(url)
    time.sleep(wait_time)
    
    # Get the rendered HTML and parse with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    # Locate the table by its ID
    table = soup.find("table", id=table_id)
    links = []
    
    if table:
        # Find all <a> tags inside the table and extract their href attributes
        a_tags = table.find_all("a")
        links = [a.get("href") for a in a_tags if a.get("href")]
    else:
        print(f"Table with id='{table_id}' not found.")
    
    driver.quit()
    return links

def extract_schools(links: list[str]) -> dict:
    """
    Extracts unique school/college names from URLs using regex.
    
    Args:
        links (list): List of URLs containing school information.
        
    Returns:
        dict: Dictionary with the count of majors for each school/college,
              sorted from highest count to lowest count
    """
    schools = {}
    pattern = r"undergraduate/([^/]+)/"
    # r"" treats backslashes as literal characters
    # undergruate/ -> must match the characters exactly
    # paratheses creates a capturing group
    # [...] defines a character set
    # ^/ means "NOT slash", any character that is not a forward slash is included in the capture group
    # the plus means one or more characters
    # after the paranthese is to match the slash at the end
    
    for link in links:
        match = re.search(pattern, link)
        if match:
            print(match)
            school = match.group(1)
            schools[school] = schools.get(school, 0) + 1
    
    return dict(sorted(schools.items(), key= lambda x: x[1], reverse=True))

def save_major_urls_to_json(links, filename='major_urls.json'):
    with open(filename, 'w') as f:
        json.dump({"major_urls": links}, f, indent=4)

def save_schools_to_json(schools, filename='schools.json'):
    with open(filename, 'w') as f:
        json.dump({"schools": schools}, f, indent=4)

# Example usage:
if __name__ == "__main__":
    links = get_table_links()
    print("Number of links found: ", len(links))
    print("\nLinks found in the table:")
    for link in links:
        print(link)
    # save_major_urls_to_json(links)
        
    schools = extract_schools(links)
    print("\nSchools/colleges & Number of Majors:")
    for school, count in schools.items():
        print(f"{school}: {count}")
    # save_schools_to_json(schools)
