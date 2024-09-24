import pandas as pd
import matplotlib.pyplot as plt
import re

file_path = './output/top_10_box_office_movies_1977_2023_with_villains_origins.csv'
df = pd.read_csv(file_path)

regions = {
    'Islamic Countries': ['iran', 'iraq', 'afghanistan', 'syria', 'pakistan', 'saudi', 'egypt', 'turkey', 'libya', 'islamic', 'arab'],
    'Communist Asia': ['china', 'north korea'],
    'USA': ['united states', 'usa', 'u.s.', 'america', 'gotham', 'new york', 'california', 'texas', 'illinois', 'los angeles', 'boston', 'amityville', 'haddonfield', 'metropolis', 'smallville', 'derry', 'maine'],
    'Russian/Ukrainian': ['russia', 'russian', 'ussr', 'soviet', 'ukraine', 'ukrainian', 'stalingrad', 'moscow', 'kyiv', 'kiev']
}

geopolitical_conflicts = {
    'Islamic Countries': [
        {'period': (1979, 1981), 'event': 'Iran Hostage Crisis'},
        {'period': (1991, 1993), 'event': 'Gulf War'},
        {'period': (2001, 2001), 'event': '9/11 Attacks'},
        {'period': (2002, 2015), 'event': 'Iraq and Afghanistan Wars'}
    ],
    'USA': [
        {'period': (1980, 1985), 'event': 'Cold War Tension'},
        {'period': (2001, 2001), 'event': '9/11 Attacks'},
        {'period': (2002, 2015), 'event': 'Iraq and Afghanistan Wars'},
        {'period': (2020, 2024), 'event': 'China Marked as Greatest Threat to the USA'}
    ],
    'Communist Asia': [
        {'period': (2006, 2018), 'event': 'North Korea Nuclear Threat'},
        {'period': (2020, 2024), 'event': 'China Marked as Greatest Threat to the USA'}
    ],
    'Russian/Ukrainian': [
        {'period': (1980, 1985), 'event': 'Cold War Tension'},
        {'period': (2014, 2016), 'event': 'Ukraine Crisis'},
        {'period': (2022, 2024), 'event': 'Russia-Ukraine Conflict'}
    ]
}

def assign_region(origin):
    origin_lower = str(origin).lower()
    for region, terms in regions.items():
        if any(re.search(r'\b' + re.escape(term) + r'\b', origin_lower) for term in terms):
            return region
    return 'Other'

df['Region'] = df['Origin'].apply(assign_region)
df = df[df['Region'] != 'Other']
villain_counts = df.groupby(['Year', 'Region']).size().unstack(fill_value=0)

def plot_region_trend_and_impact(region_name, combined=False):
    if not combined:
        plt.figure(figsize=(14, 8))

    if region_name in villain_counts.columns:
        plt.plot(villain_counts.index, villain_counts[region_name], label=region_name)

    if region_name in geopolitical_conflicts:
        for conflict in geopolitical_conflicts[region_name]:
            start_year, end_year = conflict['period']
            event_name = conflict['event']
            plt.axvline(x=start_year, color='gray', linestyle='--')
            plt.axvline(x=end_year, color='gray', linestyle='--')
            plt.text(start_year, plt.ylim()[1] * 0.85, f'{event_name} ({start_year}-{end_year})', rotation=90, verticalalignment='center', fontsize=10)

    if not combined:
        plt.xlabel('Year')
        plt.ylabel('Number of Villains')
        plt.title(f'Trend and Impact of Geopolitical Events on Villain Origins: {region_name}')
        plt.legend(loc='upper right', bbox_to_anchor=(1, 1), fontsize=10)
        plt.grid(True)
        sanitized_region_name = region_name.lower().replace(' ', '_').replace('/', '_')
        output_path = f"./output_10year_heatmaps/villains_trend_and_impact_{sanitized_region_name}.png"
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"Trend and impact visualization for {region_name} saved to {output_path}")

for region in geopolitical_conflicts.keys():
    plot_region_trend_and_impact(region)

plt.figure(figsize=(14, 8))
for region in geopolitical_conflicts.keys():
    if region in villain_counts.columns:
        plot_region_trend_and_impact(region, combined=True)

plt.xlabel('Year')
plt.ylabel('Number of Villains')
plt.title('Trend and Impact of Geopolitical Events on Villain Origins (All Regions)')
plt.legend(loc='upper right', bbox_to_anchor=(1, 1), fontsize=10)
plt.grid(True)
output_combined_path = "./output_10year_heatmaps/villains_trend_and_impact_all_regions.png"
plt.savefig(output_combined_path, bbox_inches='tight')
plt.close()
print(f"Combined trend and impact visualization saved to {output_combined_path}")
