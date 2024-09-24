# newest scraper that does both characters and the release date!
# saves to "tv_shows_new_release.json"
import requests
from bs4 import BeautifulSoup
import json
import os
import time

## GLOBAL VARS ##
MAIN_URL = "https://www.imdb.com/search/title/?title_type=tv_series&sort=num_votes,desc"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.5'
}

num_of_shows = 10
num_of_chars = 6


def get_tv_show_links():
    print("Fetching the main page...")
    response = requests.get(MAIN_URL, headers=headers)
    if response.status_code == 403:
        print("Access forbidden, please check your headers or proxy settings.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    tv_show_links = []

    for a_tag in soup.find_all('a', class_='ipc-title-link-wrapper'):
        if 'href' in a_tag.attrs:
            tv_show_links.append('https://www.imdb.com' + a_tag['href'])

    print(f"Found {len(tv_show_links)} TV show links.")
    return tv_show_links[:num_of_shows]


def get_tv_show_info(tv_show_url):
    print(f"Fetching info from {tv_show_url}...")
    response = requests.get(tv_show_url, headers=headers)
    if response.status_code == 403:
        print("Access forbidden, please check your headers or proxy settings.")
        return None, None, None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Get TV show name
    title_tag = soup.find('span', class_='hero__primary-text')
    tv_show_name = title_tag.text if title_tag else None

    # Get release year
    release_year_tag = soup.find('a', class_='ipc-link ipc-link--baseAlt ipc-link--inherit-color',
                                 attrs={'href': lambda x: x and 'releaseinfo' in x})
    release_year = release_year_tag.text.split('–')[0].strip() if release_year_tag else None

    # Get characters
    characters = []
    for div in soup.find_all('div', class_='sc-bfec09a1-7 kSFMrr'):
        character_list = div.find('div', class_='title-cast-item__characters-list')
        if character_list:
            character_name = character_list.find('span', class_='sc-bfec09a1-4 iZBIdd')
            if character_name:
                characters.append(character_name.text)
            if len(characters) >= num_of_chars:
                break

    print(f"Found TV show: {tv_show_name}, Release year: {release_year}, Characters: {len(characters)}")
    return tv_show_name, int(release_year), characters


def main():
    tv_show_links = get_tv_show_links()

    tv_show_data = []
    for idx, tv_show_url in enumerate(tv_show_links):
        tv_show_name, release_year, characters = get_tv_show_info(tv_show_url)
        if tv_show_name:
            print(f"Processing TV show {idx + 1}/{num_of_shows}: {tv_show_name}")
            tv_show_data.append({
                'tv_show_name': tv_show_name,
                'characters': characters,
                'release_year': release_year
            })
        else:
            print(f"Failed to retrieve the info for TV show {idx + 1}")
        time.sleep(2)  # Delay to avoid being blocked

    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)

    # Save the data to a JSON file
    with open('output/tv_shows_new_release2.json', 'w') as f:
        json.dump(tv_show_data, f, indent=4)

    print("Data saved to output/tv_shows_new_release2.json")


if __name__ == "__main__":
    main()