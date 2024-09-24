import os
import pandas as pd
import matplotlib.pyplot as plt
import json

def load_data(folder_path):
    data = {}
    for year in range(1970, 2023 + 1):
        file_path = os.path.join(folder_path, f'yob{year}.txt')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, names=['name', 'gender', 'count'])
            data[year] = df
    return data

def get_counts(name, data, start_year):
    counts = []
    for year in range(start_year, start_year + 8):
        if year in data:
            count = data[year][data[year]['name'] == name]['count'].sum()
            counts.append(count)
        else:
            counts.append(0)
    return counts

def plot_trends(shows, name_data, file_name):
    plt.figure(figsize=(8, 4))
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'magenta', 'yellow', 'brown', 'pink', 'black']
    color_index = 0

    for show in shows:
        debut_year = show['release_year']
        for character in show['characters']:
            first_name = character.split()[0]
            debut_count = get_counts(first_name, name_data, debut_year)[0]
            if debut_count == 0:
                counts = get_counts(first_name, name_data, debut_year)
                x_values = range(0, 8)
                plt.plot(x_values, counts, label=f"{first_name} ({show['tv_show_name']} {debut_year})",
                         color=colors[color_index % len(colors)])
                color_index += 1

    if color_index > 0:
        plt.title('7-Year Popularity Trends for Names with 0 Babies at TV Show Debut')
        plt.xlabel('Years After Debut')
        plt.ylabel('Number of Babies')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
        plt.grid(True)
        plt.tight_layout()
        plt.text(1, 0.0, f"File: {file_name}", horizontalalignment='right', verticalalignment='bottom',
                 transform=plt.gca().transAxes, fontsize=6, color='black')
        plt.show()
    else:
        print("No characters with 0 at debut.")

def load_shows(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    folder_path = r'C:\Users\ybars\OneDrive - huji.ac.il\HUJI Documents Shana BET\MATAR Bet\Data Mining 47717\babynames text files'
    name_data = load_data(folder_path)

    shows_file_path = r'C:\Users\ybars\PycharmProjects\datamining\DM_Names_new_approach\output\tv_shows_new_release.json'
    all_shows = load_shows(shows_file_path)

    file_name = "line_graph5zeros.py"
    plot_trends(all_shows, name_data, file_name)
