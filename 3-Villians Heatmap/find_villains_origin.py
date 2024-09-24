import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import pycountry

def extract_place(text):
    if pd.isna(text):
        return text

    countries = [country.name for country in pycountry.countries]
    common_places = countries + [
        "Gotham City", "Whoville", "Middle-Earth", "Bedrock", "Monstropolis", "Agrabah",
        "Atlantis", "Narnia", "Neverland", "Wakanda", "Duloc", "Isla Sorna", "Monstropolis"
    ]

    for place in common_places:
        if re.search(r'\b' + re.escape(place) + r'\b', text, re.IGNORECASE):
            return place
    return "Unknown"

def search_wiki(url, term):
    search_url = f"{url}{term.replace(' ', '_')}"
    response = requests.get(search_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        for para in paragraphs:
            if 'country' in para.text.lower() or 'origin' in para.text.lower():
                text = re.sub(r'\[.*?\]', '', para.text)
                place = extract_place(text)
                if place != "Unknown":
                    return place
    return None

def search_villains(movie, villain):
    result = search_wiki("https://villains.fandom.com/wiki/", movie)
    if not result:
        result = search_wiki("https://villains.fandom.com/wiki/", villain)
    return result

def search_heroes(movie, villain):
    result = search_wiki("https://hero.fandom.com/wiki/", movie)
    if not result:
        result = search_wiki("https://hero.fandom.com/wiki/", villain)
    return result

def search_wikipedia(movie, villain):
    result = search_wiki("https://en.wikipedia.org/wiki/", movie)
    if not result:
        result = search_wiki("https://en.wikipedia.org/wiki/", villain)
    return result

def update_csv(csv_path):
    df = pd.read_csv(csv_path)
    for index, row in df.iterrows():
        if pd.isna(row['Origin']) or row['Origin'] == 'Unknown':
            movie = row['Title']
            villain = row['Villain']
            if pd.isna(villain):
                continue
            print(f"Processing movie: {movie}, villain: {villain}")
            origin_info = search_villains(movie, villain)
            if not origin_info:
                origin_info = search_heroes(movie, villain)
            if not origin_info:
                origin_info = search_wikipedia(movie, villain)
            if origin_info:
                print(f"Found origin for {movie} (villain: {villain}): {origin_info}")
                df.at[index, 'Origin'] = origin_info
            else:
                print(f"No origin found for {movie} (villain: {villain})")
    df.to_csv(csv_path, index=False)
    print(f"Updated CSV saved to {csv_path}")
    return df

csv_path = 'output/top_10_box_office_movies_1977_2023_with_villains_origins.csv'
updated_df = update_csv(csv_path)
print(updated_df.head())