import os
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from shapely.geometry import Point
import time
import pandas as pd

# Load the CSV file
file_path = './output/top_10_box_office_movies_1977_2023_with_villains_origins.csv'
df = pd.read_csv(file_path)

# Filter out entries without an origin and exclude any clearly non-Earth origins
non_earth_keywords = ["Tatooine", "Mars", "Krypton", "Space", "Jupiter", "Venus", "Unknown", "Not on Earth"]
df = df[~df['Origin'].str.contains('|'.join(non_earth_keywords), na=True)]

# Initialize geolocator
geolocator = Nominatim(user_agent="villain_locator", timeout=10)


# Function to geocode locations
def geocode(place, retries=3):
    try:
        location = geolocator.geocode(place)
        if location:
            return Point(location.longitude, location.latitude)
    except (GeocoderTimedOut, GeocoderUnavailable):
        if retries > 0:
            time.sleep(2)  # Delay before retrying
            return geocode(place, retries - 1)
    return None


# Reduce geocoding calls by first geocoding only unique origins
unique_origins = df['Origin'].dropna().unique()

# Dictionary to store the geocoded results
geocode_results = {}

for origin in unique_origins:
    geocode_results[origin] = geocode(origin)

# Apply the geocoded coordinates back to the original dataframe
df['geometry'] = df['Origin'].map(geocode_results)
df = df.dropna(subset=['geometry'])  # Drop rows where geocoding failed

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Load world map from the local path
world = gpd.read_file('./needed_files/ne_110m_admin_0_countries.shp')
world = world[world['NAME'] != 'Antarctica']

# Create output directory if it doesn't exist
output_dir = "./output_10year_heatmaps"
os.makedirs(output_dir, exist_ok=True)

# Part 1: Heatmap Visualization with Decade Intervals
start_year = 1970
end_year = 2020
interval = 10  # Change interval to 10 years

for year in range(start_year, end_year, interval):
    subset = gdf[(gdf['Year'] >= year) & (gdf['Year'] < year + interval)]

    if len(subset) > 1:  # Ensure there are enough data points
        heatmap_data = pd.DataFrame([(point.y, point.x) for point in subset.geometry], columns=['lat', 'lon'])

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
            thresh=0.1,
            bw_adjust=0.3,
            warn_singular=False
        )

        ax.set_xticks([])
        ax.set_yticks([])
        plt.title(f"Villains' Places of Origin Heatmap: {year}-{year + interval - 1}")
        output_path = os.path.join(output_dir, f"villains_origin_heatmap_{year}_{year + interval - 1}.png")
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
    else:
        print(f"Skipping heatmap for {year}-{year + interval - 1} due to insufficient data points.")

print(f"Heatmaps saved to {output_dir}")

# Part 2: Trend Visualization for Specific Regions
# Define regions and their corresponding countries
regions = {
    'USA': ['USA', 'United States', 'America'],
    'Russia': ['Russia', 'USSR', 'Soviet Union'],
    'Europe': ['UK', 'Germany', 'France', 'Italy', 'Spain', 'Europe'],
    'Islamic Countries': ['Iran', 'Iraq', 'Afghanistan', 'Syria', 'Pakistan', 'Islamic'],
    'China': ['China'],
    'Korea': ['Korea', 'North Korea', 'South Korea']
}


# Assign each origin to a region
def assign_region(origin):
    for region, countries in regions.items():
        if any(country in origin for country in countries):
            return region
    return None


df['Region'] = df['Origin'].apply(assign_region)
df = df.dropna(subset=['Region'])

# Count villains per region over the years
villain_counts = df.groupby(['Year', 'Region']).size().unstack(fill_value=0)

# Plot the trend
plt.figure(figsize=(14, 8))
for region in regions.keys():
    if region in villain_counts.columns:
        plt.plot(villain_counts.index, villain_counts[region], label=region)

plt.xlabel('Year')
plt.ylabel('Number of Villains')
plt.title('Trend of Villains by Region Over Time')
plt.legend()
plt.grid(True)
output_trend_path = os.path.join(output_dir, "villains_trend_by_region.png")
plt.savefig(output_trend_path, bbox_inches='tight')
plt.close()

print(f"Trend visualization saved to {output_dir}")
