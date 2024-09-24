import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# IMDb URLs for the directors
directors_imdb = {
    "Clint Eastwood": "https://www.imdb.com/name/nm0000142/awards/",
    "Martin Scorsese": "https://www.imdb.com/name/nm0000217/awards/",
    "Francis Ford Coppola": "https://www.imdb.com/name/nm0000338/awards/",
    "Tim Burton": "https://www.imdb.com/name/nm0000318/awards/",
    "Renny Harlin": "https://www.imdb.com/name/nm0001317/awards/",
    "Alfred Hitchcock": "https://www.imdb.com/name/nm0000033/awards/",
    "Ron Howard": "https://www.imdb.com/name/nm0000165/awards/",
    "Ridley Scott": "https://www.imdb.com/name/nm0000631/awards/",
    "Steven Spielberg": "https://www.imdb.com/name/nm0000229/awards/",
    "Woody Allen": "https://www.imdb.com/name/nm0000095/awards/",
    "Robert Zemeckis": "https://www.imdb.com/name/nm0000709/awards/",
    "Steven Soderbergh": "https://www.imdb.com/name/nm0001752/awards/"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


# Function to scrape awards data for a given director
def scrape_imdb_awards(director, url):
    print(f"Fetching awards for {director} from {url}...")
    response = requests.get(url, headers=headers)
    if response.status_code == 403:
        print(f"Access forbidden for {director}, please check your headers or proxy settings.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    awards_data = []

    # Find all awards listed
    awards_items = soup.find_all('li', class_='ipc-metadata-list-summary-item')

    if not awards_items:
        print(f"No awards found for {director}.")
        return awards_data

    for item in awards_items:
        # Extract the year, award type, category, and title
        award_info = item.find('a', class_='ipc-metadata-list-summary-item__t')
        if award_info:
            award_year_and_type = award_info.get_text(strip=True)
            award_parts = award_year_and_type.split(' ', 1)
            award_year = award_parts[0]
            award_type = award_parts[1] if len(award_parts) > 1 else ''
            award_category = item.find('span', class_='awardCategoryName').get_text(strip=True) if item.find('span',
                                                                                                             class_='awardCategoryName') else ''
            award_title = item.find('a', class_='ipc-metadata-list-summary-item__li--link').get_text(
                strip=True) if item.find('a', class_='ipc-metadata-list-summary-item__li--link') else ''

            # Append the data to the list
            awards_data.append({
                "Director": director,
                "Year": award_year,
                "Award_Type": award_type,
                "Category": award_category,
                "Title": award_title
            })

    return awards_data


def main():
    all_awards_data = []

    for director, url in directors_imdb.items():
        director_awards = scrape_imdb_awards(director, url)
        all_awards_data.extend(director_awards)
        time.sleep(2)  # Delay to avoid being blocked

    # Convert the scraped data into a DataFrame
    awards_df = pd.DataFrame(all_awards_data)

    # Debugging: Print the first few rows of the DataFrame to verify its structure
    print(awards_df.head())

    # Step 1: Group by director and year, and count the number of films/awards in each year
    if 'Director' in awards_df.columns and 'Year' in awards_df.columns:
        awards_grouped = awards_df.groupby(['Director', 'Year']).size().reset_index(name='Film_Count')

        # Step 2: Save the list to a CSV file
        os.makedirs('./output', exist_ok=True)
        awards_grouped.to_csv('./output/director_awards_list.csv', index=False)
        print("Scraping complete. Data saved to './output/director_awards_list.csv'")
    else:
        print("Error: Missing 'Director' or 'Year' column in the DataFrame")


if __name__ == "__main__":
    main()