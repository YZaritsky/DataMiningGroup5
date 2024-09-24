import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def get_top_10_movies(year):
    url = f"https://www.boxofficemojo.com/year/{year}/?grossesOption=totalGrosses"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')[1:11]
    movies = []
    for row in rows:
        cols = row.find_all('td')
        rank = cols[0].text.strip()
        title = cols[1].text.strip()
        gross = cols[5].text.strip()
        movies.append([year, rank, title, gross])
    return movies

all_movies = []
for year in range(1977, 2024):
    try:
        top_movies = get_top_10_movies(year)
        all_movies.extend(top_movies)
        print(f"Successfully scraped data for {year}")
    except Exception as e:
        print(f"Failed to scrape data for {year}: {e}")

df = pd.DataFrame(all_movies, columns=['Year', 'Rank', 'Title', 'Gross'])

output_folder = 'output'
os.makedirs(output_folder, exist_ok=True)

output_path = os.path.join(output_folder, 'top_10_box_office_movies_1977_2023.csv')
df.to_csv(output_path, index=False)

print("Data scraping completed and saved to CSV.")