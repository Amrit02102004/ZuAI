import requests
from bs4 import BeautifulSoup
import json
import traceback
import sys
from urllib.parse import urlparse, unquote
from working import scrape_nailib_page
def extract_math_ia_links(base_url):
    """
    Extract Math IA links from the webpage.
    """
    try:
        # Send a GET request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(base_url, headers=headers)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all anchor tags with the specific class
        links = []
        matching_tags = soup.find_all('a', class_=lambda x: x and 'sample_sample__fWsLe' in x)
        print(f"Found {len(matching_tags)} matching tags")
        
        for link in matching_tags:
            href = link.get('href', '')
            print(f"Raw href: {href}")
            
            # Decode the URL
            decoded_href = unquote(href)
            
            # Split by '/' and find the last part that looks like a valid ID
            path_parts = decoded_href.split('/')
            
            # Find the last part that looks like a valid hash/ID
            valid_ids = [part for part in path_parts if len(part) == 24 and part.isalnum()]
            
            if valid_ids:
                # Take the last valid ID
                last_part = valid_ids[-1]
                full_url = f"https://nailib.com/ia-sample/ib-math-aa-hl/{last_part}"
                links.append(full_url)
                print(f"Found valid link: {full_url}")
        
        # Remove duplicates while preserving order
        unique_links = list(dict.fromkeys(links))
        
        return unique_links
    
    except requests.RequestException as e:
        print(f"Request Error: {e}")
        traceback.print_exc()
        return []
    except Exception as e:
        print(f"Unexpected Error: {e}")
        traceback.print_exc()
        return []

def scrape_multiple_math_ias(urls):
    """
    Scrape multiple Math IA URLs and collect their data.
    """
    all_ia_data = []
    
    for url in urls:
        print(f"Scraping URL: {url}")
        try:
            ia_data = scrape_nailib_page(url)
            
            if ia_data:
                all_ia_data.append(ia_data)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    return all_ia_data

def main():
    # List of base URLs to search for Math IA samples
    base_urls = [
        'https://nailib.com/ia-sample/ib-math-ai-sl',
        'https://nailib.com/ee-sample/ib-math-ai-sl'
    ]
    
    # Collect all Math IA links
    all_math_ia_links = []
    for base_url in base_urls:
        math_ia_links = extract_math_ia_links(base_url)
        all_math_ia_links.extend(math_ia_links)
    
    # Remove duplicates
    all_math_ia_links = list(dict.fromkeys(all_math_ia_links))
    
    print(f"Found {len(all_math_ia_links)} Math IA links")
    if all_math_ia_links:
        print("Links:", all_math_ia_links)
        
        # Scrape all found links
        scraped_data = scrape_multiple_math_ias(all_math_ia_links)
        
        # Save all scraped data to a single JSON file
        with open('all_math_ia_data.json', 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=2)
        
        print(f"Scraped and saved data for {len(scraped_data)} Math IAs")
    else:
        print("No valid Math IA links found.")

if __name__ == "__main__":
    main()