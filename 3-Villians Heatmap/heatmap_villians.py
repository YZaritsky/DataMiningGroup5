import json
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from shapely.geometry import Point
import time
import pandas as pd

with open('./output/villains_data.json', 'r') as f:
    data = json.load(f)

places_of_birth = [
    {
        'name': villain['name'],
        'place_of_birth': villain['place_of_birth'],
        'universe': villain['universe']
    }
    for villain in data if villain.get('place_of_birth', '')
]

geolocator = Nominatim(user_agent="villain_locator", timeout=10)

def geocode(place, retries=3):
    try:
        location = geolocator.geocode(place)
        if location:
            return Point(location.longitude, location.latitude)
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        if retries > 0:
            time.sleep(2)
            return geocode(place, retries - 1)
        else:
            print(f"Geocoding failed for {place} after several retries: {e}")
    return None

geo_data = []
for place in places_of_birth:
    point = geocode(place['place_of_birth'])
    if point:
        geo_data.append({
            'name': place['name'],
            'universe': place['universe'],
            'geometry': point
        })

gdf = gpd.GeoDataFrame(geo_data)
heatmap_data = pd.DataFrame([(point.y, point.x) for point in gdf.geometry], columns=['lat', 'lon'])

world = gpd.read_file("./needed_files/ne_110m_admin_0_countries.shp")
world = world[world['CONTINENT'] != 'Antarctica']

fig, ax = plt.subplots(figsize=(20, 10), dpi=300)
world.boundary.plot(ax=ax, color="black", linewidth=0.5)

sns.kdeplot(
    data=heatmap_data,
    x='lon',
    y='lat',
    fill=True,
    cmap='Reds',
    alpha=0.6,
    ax=ax,
    levels=100,
    thresh=0.01
)

ax.set_xticks([])
ax.set_yticks([])
plt.title("Villains' Places of Birth Heatmap")

output_path = "./output/villains_places_of_birth_heatmap.png"
plt.savefig(output_path, bbox_inches='tight')
plt.show()

print(f"Heatmap saved to {output_path}")
