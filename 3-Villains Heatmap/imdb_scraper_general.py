from bs4 import BeautifulSoup
import requests
import re
import json
from selenium import webdriver
import time
import os

driver = webdriver.Chrome()

url = 'http://www.imdb.com/chart/top'
driver.get(url)

time.sleep(5)  

soup = BeautifulSoup(driver.page_source, "html.parser")
movies = soup.select('td.titleColumn')
crew = [a.attrs.get('title') for a in soup.select('td.titleColumn a')]
ratings = [b.attrs.get('data-value') for b in soup.select('td.posterColumn span[name=ir]')]

movie_list = []

for index in range(len(movies)):
    movie_string = movies[index].get_text()
    movie = (' '.join(movie_string.split()).replace('.', ''))
    media_title = movie[len(str(index)) + 1:-7]
    year = re.search(r'\((.*?)\)', movie_string).group(1)
    place = movie[:len(str(index)) - (len(movie))]

    director, actors = crew[index].split('(dir.), ')

    data = {
        "place": place.strip(),
        "media_title": media_title.strip(),
        "rating": ratings[index],
        "year": year,
        "director": director.strip(),
        "actors": actors.strip()
    }
    movie_list.append(data)

for movie in movie_list:
    print(movie['place'], '-', movie['media_title'], '(' + movie['year'] + ') -',
          'Director:', movie['director'], 'Actors:', movie['actors'], 'Rating:', movie['rating'])

output_dir = '3-Villians Heatmap/output'
os.makedirs(output_dir, exist_ok=True)

output_file_path = os.path.join(output_dir, 'imdb_movies_and_directors.json')
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(movie_list, f, ensure_ascii=False, indent=4)

driver.quit()
