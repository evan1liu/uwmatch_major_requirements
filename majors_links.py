from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

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

# Example usage:
if __name__ == "__main__":
    links = get_table_links()
    print("Number of links found: ", len(links))
    print("Links found in the table:")
    for link in links:
        print(link)
