import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def extract_details(soup):
    ia_data = {
        "title": "",
        "subject": "Math AI SL",
        "description": "",
        "sections": {},
        "word_count": 0,
        "read_time": "",
        "file_link": "",
        "publication_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    # Extract title
    title_elem = soup.find('h1', class_='file_sample__body__container__middle__cover__heading__VG9Sj')
    if title_elem:
        ia_data["title"] = title_elem.get_text(strip=True)
    
    # Extract read time
    read_time_elem = soup.find('div', class_='file_sample__body__container__middle__cover__stat__item__text__6umeQ', string=re.compile(r'\d+\s*mins\s*read'))
    if read_time_elem:
        ia_data["read_time"] = read_time_elem.get_text(strip=True)
    
    # Word count extraction
    word_count_div = soup.find('div', class_='file_sample__body__container__middle__cover__list__nmVAV')
    
    if word_count_div:
        print("Word count div found!")
        # Print out the entire div content for inspection
        print("Full div content:", word_count_div.get_text())
        
        # Multiple approaches to find word count
        word_count_patterns = [
            re.compile(r'Word\s*count\s*:\s*(\d+(?:,\d+)?)'),
            re.compile(r'(\d+(?:,\d+)?)\s*(?:word|words)')
        ]
        
        for pattern in word_count_patterns:
            word_count_match = pattern.search(word_count_div.get_text())
            if word_count_match:
                word_count_str = word_count_match.group(1)
                ia_data["word_count"] = int(word_count_str.replace(',', ''))
                print(f"Word count found: {ia_data['word_count']}")
                break
    else:
        print("Word count div NOT found!")
    
    
    # Extract PDF file link
    pdf_link = soup.find('a', href=lambda href: href and href.endswith('.pdf'))
    if pdf_link:
        ia_data["file_link"] = pdf_link['href']
    
    # Find all h2 headings to define sections
    h2_headings = soup.find_all('h2')
    
    # Extract introduction description (first 4 lines of paragraphs)
    intro_paragraphs = soup.find_all('p')
    description_lines = [p.get_text(strip=True) for p in intro_paragraphs[:4]]
    ia_data["description"] = " ".join(description_lines)
    
    # Process sections starting from Introduction
    sections = {}
    current_section = None
    
    # Find all paragraphs
    all_paragraphs = soup.find_all('p')
    
    # Skip the first 4 paragraphs (used in description)
    for paragraph in all_paragraphs[4:]:
        # Check if this paragraph is near a section heading
        for heading in h2_headings:
            if heading.find_next('p') == paragraph:
                current_section = heading.get_text(strip=True)
                sections[current_section] = ""
                break
        
        # Add paragraph to current section
        if current_section:
            if current_section in sections:
                sections[current_section] += paragraph.get_text(strip=True) + " "
    
    # Clean up sections
    sections = {k: v.strip() for k, v in sections.items() if v.strip()}
    
    ia_data["sections"] = sections
    
    return ia_data

def scrape_nailib_page(url):
    try:
        # Send a GET request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract detailed information
        ia_data = extract_details(soup)
        
        # Print the extracted data
        print(json.dumps(ia_data, indent=2))
        
        # Save the data to a JSON file
        with open('nailib_ia_data_2.json', 'w', encoding='utf-8') as f:
            json.dump(ia_data, f, ensure_ascii=False, indent=2)
        
        return ia_data
    
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# url = 'https://nailib.com/ia-sample/ib-math-aa-hl/649a7fa93367e8a2e6bfda28'
# scrape_nailib_page(url)``