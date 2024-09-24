import json
import os
import time
from selenium import webdriver
from bs4 import BeautifulSoup

BASE_URL = "https://www.superherodb.com"
MALE_VILLAINS_URL = f'{BASE_URL}/characters/male/villains/?set_gender=male&set_side=bad&page_nr='
FEMALE_VILLAINS_URL = f'{BASE_URL}/characters/female/villains/?set_gender=female&set_side=bad&page_nr='

def get_villain_links(driver, base_url, max_page):
    links = []
    for page in range(1, max_page + 1):
        url = f"{base_url}{page}"
        driver.get(url)
        time.sleep(1)
        driver.execute_script("window.stop();")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        character_links = [BASE_URL + a['href'] for a in soup.select('div.column.col-12 ul.list-md li a')]
        links.extend(character_links)
    return links

def get_villain_details(driver, url):
    driver.get(url)
    time.sleep(1)
    driver.execute_script("window.stop();")
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        details = {}
        name_tag = soup.select_one('div.columns.profile-titles h1')
        if name_tag:
            details['name'] = name_tag.text.strip()
        else:
            print(f"Name not found for {url}")
            return {}
        universe_tag = soup.select_one('div.columns.profile-titles h3')
        if universe_tag:
            details['universe'] = universe_tag.text.strip()
        origin_table = soup.select('div.column.col-8.col-md-7.col-sm-12 table.profile-table')
        for table in origin_table:
            for row in table.select('tr'):
                key_tag = row.select_one('td')
                value_tag = row.select('td')[1] if len(row.select('td')) > 1 else None
                if key_tag and value_tag:
                    key = key_tag.text.strip()
                    if key == 'Place of birth':
                        details[key] = value_tag.text.strip()
                    elif key == 'Species // Type':
                        species = ' // '.join([a.text for a in value_tag.select('a')])
                        details['species'] = species
        return details
    except Exception as e:
        print(f"Error fetching details for {url}: {e}")
        return {}

def scrape_villains(driver, links):
    villains = []
    for link in links:
        details = get_villain_details(driver, link)
        if 'name' in details:
            villain = {
                'name': details['name'],
                'place_of_birth': details.get('Place of birth', 'Unknown'),
                'universe': details.get('universe', 'Unknown'),
                'species': details.get('species', 'Unknown')
            }
            print(f"Scraped villain: {villain}")
            villains.append(villain)
    return villains

def main():
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.video": 2,
        "profile.managed_default_content_settings.audio": 2,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.automatic_downloads": 2,
        "profile.managed_default_content_settings.ads": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)

    male_links = get_villain_links(driver, MALE_VILLAINS_URL, max_page=18)
    female_links = get_villain_links(driver, FEMALE_VILLAINS_URL, max_page=5)
    all_links = male_links + female_links

    villains_data = scrape_villains(driver, all_links)

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'villains_data.json')
    with open(output_path, 'w') as f:
        json.dump(villains_data, f, indent=4)

    print(f"Data saved to '{output_path}'")
    driver.quit()

if __name__ == '__main__':
    main()
