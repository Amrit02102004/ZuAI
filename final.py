import requests
from bs4 import BeautifulSoup
import traceback
import sys
from urllib.parse import urlparse, unquote
from working import scrape_nailib_page
from motor.motor_asyncio import AsyncIOMotorClient
from model import IAModel, convert_model_to_dict

# Import MongoDB CRUD class
from mongo import MongoCRUD

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

async def scrape_multiple_math_ias(urls, mongo_crud):
    """
    Scrape multiple Math IA URLs and store directly in MongoDB.
    
    :param urls: List of URLs to scrape
    :param mongo_crud: MongoDB CRUD instance for storing samples
    """
    successful_samples = 0
    
    for url in urls:
        print(f"Scraping URL: {url}")
        try:
            # Scrape individual page
            ia_data = scrape_nailib_page(url)
            
            if ia_data:
                # Convert to Pydantic model
                sample_model = IAModel(**{
                    **ia_data, 
                    'source_url': url  # Add source URL to the sample
                })
                
                # Convert to dictionary and store in MongoDB
                sample_dict = convert_model_to_dict(sample_model)
                await mongo_crud.create_sample(sample_dict)
                
                successful_samples += 1
                print(f"Successfully stored sample from {url}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            traceback.print_exc()
    
    return successful_samples

async def main():
    """
    Modified main function to be fully async
    """
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
        # Initialize MongoDB CRUD
        mongo_crud = MongoCRUD()
        
        # Scrape and store samples
        successful_samples = await scrape_multiple_math_ias(all_math_ia_links, mongo_crud)
        
        print(f"Successfully scraped and stored {successful_samples} Math IAs into MongoDB")
    else:
        print("No valid Math IA links found.")
    
    # Return the number of successful samples
    return {"successful_samples": successful_samples}
