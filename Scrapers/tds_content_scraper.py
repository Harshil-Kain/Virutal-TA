'''
This code is used to scrape content from the TDS website, specifically targeting the articles and sections within the sidebar links. 
It uses Selenium for web automation and BeautifulSoup for HTML parsing. The scraped content is structured into blocks and saved as a JSON file.
'''

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

BASE_URL = "http://tds.s-anand.net"
HOME_PAGE = BASE_URL + "/#/2025-01/"

driver.get(HOME_PAGE)
time.sleep(3)
soup = BeautifulSoup(driver.page_source, 'html.parser')

sidebar = soup.find('aside', class_='sidebar')
link_tags = sidebar.find_all('a', href=True)
link_hrefs = {tag['href'] for tag in link_tags if tag['href'].startswith('#/')}

print(f"Found {len(link_hrefs)} sidebar links.")

def extract_article_blocks(soup):
    content_blocks = []
    article = soup.find('article', id='main', class_='markdown-section')
    if not article:
        return content_blocks

    for details in article.find_all('details'):
        item = {
            'type': 'details',
            'summary': details.find('summary').text.strip() if details.find('summary') else '',
            'paragraphs': [p.text.strip() for p in details.find_all('p') if p.text.strip()]
        }
        content_blocks.append(item)

    for heading in article.find_all(['h2', 'h3']):
        section = {
            'type': 'section',
            'heading': heading.get_text(strip=True),
            'paragraphs': [],
            'ordered_list': [],
            'unordered_list': []
        }

        next_node = heading.find_next_sibling()
        while next_node and next_node.name not in ['h2', 'h3']:
            if next_node.name == 'p':
                section['paragraphs'].append(next_node.get_text(strip=True))
            elif next_node.name == 'ol':
                section['ordered_list'].extend([li.get_text(strip=True) for li in next_node.find_all('li')])
            elif next_node.name == 'ul':
                section['unordered_list'].extend([li.get_text(strip=True) for li in next_node.find_all('li')])
            next_node = next_node.find_next_sibling()

        content_blocks.append(section)

    return content_blocks

all_content = []

for href in link_hrefs:
    full_url = BASE_URL + href
    print(f"Scraping {full_url}")
    driver.get(full_url)
    time.sleep(2)  

    page_soup = BeautifulSoup(driver.page_source, 'html.parser')
    blocks = extract_article_blocks(page_soup)
    if blocks:
        all_content.append({
            'page': href,
            'blocks': blocks
        })

driver.quit()

filename = 'tds_all_content.json'
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(all_content, f, indent=2, ensure_ascii=False)

print(f"\n✅ Scraping complete. Total pages saved: {len(all_content)} → '{filename}'")
